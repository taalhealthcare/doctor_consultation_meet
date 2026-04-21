import re
import frappe
from frappe.utils import today, add_days


@frappe.whitelist()
def get_appointment_dashboard_data():
    t = today()
    return {
        "kpis":           _kpis(t),
        "charts":         _charts(t),
        "today_schedule": _today_schedule(t),
        "activity_feed":  _activity_feed(),
        "pipeline":       _pipeline(),
        "top3":           _top3(),
        "patient_stats":  _patient_stats(),
    }


# ── Helpers ───────────────────────────────────────────────────────

def _q(sql, args=None):
    r = frappe.db.sql(sql, args or [], as_list=True)
    return int(r[0][0] or 0) if r else 0


def _trend(cur, prev):
    if prev == 0:
        return {"pct": 0.0, "dir": "flat"}
    diff = cur - prev
    pct  = round(abs(diff) / prev * 100, 1)
    return {"pct": pct, "dir": "up" if diff > 0 else ("down" if diff < 0 else "flat")}


# ── KPIs ──────────────────────────────────────────────────────────

def _kpis(t):
    t7  = str(add_days(t, -7))
    t14 = str(add_days(t, -14))
    ty  = str(add_days(t, -1))
    ts  = str(t)

    total    = _q("SELECT COUNT(*) FROM `tabAppointment Details`")
    t_7d     = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE appointment_date BETWEEN %s AND %s", [t7, ts])
    t_p7d    = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE appointment_date BETWEEN %s AND %s", [t14, ty])

    today_c  = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE appointment_date = %s", [ts])
    yest_c   = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE appointment_date = %s", [ty])

    active   = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE status IN ('Waiting','Approved','InConsultation')")
    act_7d   = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE status IN ('Waiting','Approved','InConsultation') AND appointment_date BETWEEN %s AND %s", [t7, ts])
    act_p7d  = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE status IN ('Waiting','Approved','InConsultation') AND appointment_date BETWEEN %s AND %s", [t14, ty])

    bp       = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE status = 'Bill Paid'")
    bp_7d    = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE status = 'Bill Paid' AND appointment_date BETWEEN %s AND %s", [t7, ts])
    bp_p7d   = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE status = 'Bill Paid' AND appointment_date BETWEEN %s AND %s", [t14, ty])

    can      = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE status = 'Cancelled'")
    can_7d   = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE status = 'Cancelled' AND appointment_date BETWEEN %s AND %s", [t7, ts])
    can_p7d  = _q("SELECT COUNT(*) FROM `tabAppointment Details` WHERE status = 'Cancelled' AND appointment_date BETWEEN %s AND %s", [t14, ty])

    return {
        "total":        total,
        "total_trend":  _trend(t_7d,    t_p7d),
        "today":        today_c,
        "today_trend":  _trend(today_c, yest_c),
        "week":         t_7d,
        "week_trend":   _trend(t_7d,    t_p7d),
        "active":       active,
        "active_trend": _trend(act_7d,  act_p7d),
        "bill_paid":    bp,
        "bp_trend":     _trend(bp_7d,   bp_p7d),
        "cancelled":    can,
        "can_trend":    _trend(can_7d,  can_p7d),
        "completion":   round(bp / total * 100, 1) if total > 0 else 0.0,
    }


# ── Chart data ────────────────────────────────────────────────────

def _status_grouped():
    rows = frappe.db.sql(
        "SELECT status, COUNT(*) AS cnt FROM `tabAppointment Details` "
        "WHERE status IS NOT NULL AND status != '' GROUP BY status",
        as_dict=True
    )
    sm = {r.status: int(r.cnt) for r in rows}
    buckets = {
        "Active":    sm.get("Waiting",0) + sm.get("Approved",0) + sm.get("InConsultation",0),
        "Treatment": sm.get("Lab",0) + sm.get("Pharmacy",0),
        "Completed": sm.get("Bill Paid",0),
        "Follow-Up": sm.get("Follow-Up",0) + sm.get("ReScheduled",0),
        "Cancelled": sm.get("Cancelled",0),
    }
    return {
        "labels":   list(buckets.keys()),
        "datasets": [{"name": "Appointments", "values": list(buckets.values())}]
    }


def _gender():
    rows = frappe.db.sql(
        "SELECT sex, COUNT(*) AS cnt FROM `tabAppointment Data` "
        "WHERE sex IS NOT NULL AND sex != '' GROUP BY sex",
        as_dict=True
    )
    return {
        "labels":   [r.sex for r in rows],
        "datasets": [{"name": "Patients", "values": [int(r.cnt) for r in rows]}]
    }


def _age_groups():
    rows = frappe.db.sql(
        "SELECT age FROM `tabAppointment Data` WHERE age IS NOT NULL AND age != ''",
        as_list=True
    )
    buckets = {"0-17": 0, "18-34": 0, "35-49": 0, "50+": 0}
    unknown = 0
    for row in rows:
        m = re.match(r"(\d+)", str(row[0] or "").strip())
        if m:
            v = int(m.group(1))
            if   v < 18: buckets["0-17"] += 1
            elif v < 35: buckets["18-34"] += 1
            elif v < 50: buckets["35-49"] += 1
            else:        buckets["50+"]   += 1
        else:
            unknown += 1
    labels = list(buckets.keys())
    values = list(buckets.values())
    if unknown > 0:
        labels.append("Unknown")
        values.append(unknown)
    return {
        "labels":   labels,
        "datasets": [{"name": "Patients", "values": values}]
    }


def _monthly(t):
    rows = frappe.db.sql("""
        SELECT DATE_FORMAT(appointment_date,'%%b %%Y') AS mo,
               YEAR(appointment_date)*100+MONTH(appointment_date) AS sk,
               COUNT(*) AS cnt
        FROM `tabAppointment Details`
        WHERE appointment_date >= DATE_SUB(%s, INTERVAL 6 MONTH)
          AND appointment_date IS NOT NULL
        GROUP BY mo, sk ORDER BY sk
    """, str(t), as_dict=True)
    return {
        "labels":   [r.mo for r in rows],
        "datasets": [{"name": "Appointments", "values": [int(r.cnt) for r in rows]}]
    }


def _day_of_week(t):
    rows = frappe.db.sql("""
        SELECT DAYOFWEEK(appointment_date) AS dow, COUNT(*) AS cnt
        FROM `tabAppointment Details`
        WHERE appointment_date >= DATE_SUB(%s, INTERVAL 3 MONTH)
          AND appointment_date IS NOT NULL
        GROUP BY dow ORDER BY dow
    """, str(t), as_dict=True)
    dm       = {int(r.dow): int(r.cnt) for r in rows}
    day_lbl  = {2:"Mon", 3:"Tue", 4:"Wed", 5:"Thu", 6:"Fri", 7:"Sat"}
    days     = [2, 3, 4, 5, 6, 7]
    return {
        "labels":   [day_lbl[d] for d in days],
        "datasets": [{"name": "Appointments", "values": [dm.get(d, 0) for d in days]}]
    }


def _practitioner_chart():
    rows = frappe.db.sql("""
        SELECT COALESCE(hp.practitioner_name, ad.practitioner_assigned) AS nm,
               COUNT(*) AS cnt
        FROM `tabAppointment Details` ad
        LEFT JOIN `tabHealthcare Practitioner` hp ON hp.name = ad.practitioner_assigned
        WHERE ad.practitioner_assigned IS NOT NULL AND ad.practitioner_assigned != ''
        GROUP BY ad.practitioner_assigned ORDER BY cnt DESC LIMIT 8
    """, as_dict=True)
    return {
        "labels":   [r.nm for r in rows],
        "datasets": [{"name": "Appointments", "values": [int(r.cnt) for r in rows]}]
    }


def _opd_chart():
    rows = frappe.db.sql("""
        SELECT opd_allotted, COUNT(*) AS cnt
        FROM `tabAppointment Details`
        WHERE opd_allotted IS NOT NULL AND opd_allotted != ''
        GROUP BY opd_allotted ORDER BY cnt DESC LIMIT 8
    """, as_dict=True)
    return {
        "labels":   [r.opd_allotted for r in rows],
        "datasets": [{"name": "Appointments", "values": [int(r.cnt) for r in rows]}]
    }


def _charts(t):
    return {
        "status_grouped": _status_grouped(),
        "gender":         _gender(),
        "age_groups":     _age_groups(),
        "monthly":        _monthly(t),
        "day_of_week":    _day_of_week(t),
        "practitioner":   _practitioner_chart(),
        "opd":            _opd_chart(),
    }


# ── Today's schedule ─────────────────────────────────────────────

def _today_schedule(t):
    rows = frappe.db.sql("""
        SELECT COALESCE(pat.patient_name, apd.patient_name, 'Unknown') AS patient_display,
               COALESCE(hp.practitioner_name, ad.practitioner_assigned, '—')  AS practitioner,
               COALESCE(ad.opd_allotted, '—') AS opd_allotted,
               COALESCE(ad.status, '—')        AS status
        FROM `tabAppointment Details` ad
        JOIN  `tabAppointment Data`  apd ON apd.name = ad.parent
        LEFT JOIN `tabPatient`              pat ON pat.name  = apd.patient_name
        LEFT JOIN `tabHealthcare Practitioner` hp ON hp.name = ad.practitioner_assigned
        WHERE ad.appointment_date = %s
        ORDER BY apd.record_created ASC
        LIMIT 20
    """, str(t), as_dict=True)
    return [dict(r) for r in rows]


# ── Activity feed ─────────────────────────────────────────────────

def _activity_feed():
    rows = frappe.db.sql("""
        SELECT COALESCE(pat.patient_name, apd.patient_name, 'Unknown') AS patient_display,
               COALESCE(hp.practitioner_name, ad.practitioner_assigned, '—')  AS practitioner,
               COALESCE(ad.opd_allotted, '—') AS opd_allotted,
               COALESCE(ad.status, '—')        AS status,
               ad.appointment_date,
               apd.location
        FROM `tabAppointment Details` ad
        JOIN  `tabAppointment Data`  apd ON apd.name = ad.parent
        LEFT JOIN `tabPatient`              pat ON pat.name  = apd.patient_name
        LEFT JOIN `tabHealthcare Practitioner` hp ON hp.name = ad.practitioner_assigned
        ORDER BY apd.record_created DESC
        LIMIT 5
    """, as_dict=True)
    result = []
    for r in rows:
        row = dict(r)
        if row.get("appointment_date"):
            row["appointment_date"] = str(row["appointment_date"])
        result.append(row)
    return result


# ── Pipeline ─────────────────────────────────────────────────────

def _pipeline():
    rows = frappe.db.sql("""
        SELECT status, COUNT(*) AS cnt
        FROM `tabAppointment Details`
        WHERE status IS NOT NULL AND status != ''
        GROUP BY status
    """, as_dict=True)
    sm = {r.status: int(r.cnt) for r in rows}
    statuses = [
        "Waiting", "Approved", "InConsultation", "Lab",
        "Pharmacy", "Bill Paid", "Follow-Up", "ReScheduled", "Cancelled"
    ]
    total = _q("SELECT COUNT(*) FROM `tabAppointment Details`")
    return {
        "statuses": {s: sm.get(s, 0) for s in statuses},
        "total":    total,
    }


# ── Top 3 ─────────────────────────────────────────────────────────

def _top3():
    loc_rows = frappe.db.sql("""
        SELECT apd.location, COUNT(ad.name) AS cnt
        FROM `tabAppointment Details` ad
        JOIN `tabAppointment Data` apd ON apd.name = ad.parent
        WHERE apd.location IS NOT NULL AND apd.location != ''
        GROUP BY apd.location ORDER BY cnt DESC LIMIT 3
    """, as_dict=True)
    loc_total = sum(int(r.cnt) for r in loc_rows) or 1

    prac_rows = frappe.db.sql("""
        SELECT COALESCE(hp.practitioner_name, ad.practitioner_assigned) AS nm,
               COUNT(*) AS cnt
        FROM `tabAppointment Details` ad
        LEFT JOIN `tabHealthcare Practitioner` hp ON hp.name = ad.practitioner_assigned
        WHERE ad.practitioner_assigned IS NOT NULL AND ad.practitioner_assigned != ''
        GROUP BY ad.practitioner_assigned ORDER BY cnt DESC LIMIT 3
    """, as_dict=True)
    prac_total = sum(int(r.cnt) for r in prac_rows) or 1

    return {
        "locations": [
            {"name": r.location, "cnt": int(r.cnt), "pct": round(int(r.cnt)/loc_total*100)}
            for r in loc_rows
        ],
        "practitioners": [
            {"name": r.nm, "cnt": int(r.cnt), "pct": round(int(r.cnt)/prac_total*100)}
            for r in prac_rows
        ],
    }


# ── Patient stats ─────────────────────────────────────────────────

def _patient_stats():
    total_p = _q(
        "SELECT COUNT(DISTINCT patient_name) FROM `tabAppointment Data` "
        "WHERE patient_name IS NOT NULL AND patient_name != ''"
    )
    total_a = _q("SELECT COUNT(*) FROM `tabAppointment Details`")
    returning = _q("""
        SELECT COUNT(*) FROM (
            SELECT apd.patient_name
            FROM `tabAppointment Details` ad
            JOIN `tabAppointment Data` apd ON apd.name = ad.parent
            WHERE apd.patient_name IS NOT NULL AND apd.patient_name != ''
            GROUP BY apd.patient_name HAVING COUNT(*) > 1
        ) t
    """)
    return {
        "total_patients":  total_p,
        "returning":       returning,
        "return_rate":     round(returning / total_p * 100) if total_p > 0 else 0,
        "avg_per_patient": round(total_a / total_p, 1)      if total_p > 0 else 0.0,
    }
