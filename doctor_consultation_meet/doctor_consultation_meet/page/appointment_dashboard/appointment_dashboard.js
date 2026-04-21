// ================================================================
//  Appointment Dashboard
//  App  : doctor_consultation_meet
//  Page : appointment-dashboard
//  URL  : /app/appointment-dashboard
//  Data : doctor_consultation_meet.services.appointment_dashboard
// ================================================================

frappe.pages["appointment-dashboard"].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent:        wrapper,
        title:         "Offline Doctor Consultation Dashboard",
        single_column: true
    });

    page.add_inner_button(__("Refresh Dashboard"), function () {
        _apd_load(page);
    });

    _apd_inject_styles();
    _apd_load(page);
};


// ================================================================
//  STYLES
// ================================================================
function _apd_inject_styles() {
    if (document.getElementById("_apd_css")) return;
    var el = document.createElement("style");
    el.id  = "_apd_css";
    el.textContent = ""
        + ".apd-wrap{padding:16px 20px 48px;max-width:1400px;margin:0 auto}"
        + ".apd-topbar{display:flex;align-items:center;justify-content:space-between;"
        +   "padding:14px 18px;background:#fff;border:0.5px solid #e2e8f0;"
        +   "border-radius:12px;margin-bottom:20px;flex-wrap:wrap;gap:10px}"
        + ".apd-tb-ttl{font-size:16px;font-weight:500;color:#111;margin-bottom:2px}"
        + ".apd-tb-sub{font-size:11px;color:#94a3b8}"
        + ".apd-tb-chips{display:flex;gap:8px;flex-wrap:wrap}"
        + ".apd-chip{font-size:11px;font-weight:500;padding:3px 10px;border-radius:999px;border:0.5px solid}"
        + ".apd-chip-g{background:#EAF3DE;color:#27500A;border-color:#639922}"
        + ".apd-chip-b{background:#E6F1FB;color:#0C447C;border-color:#378ADD}"
        + ".apd-chip-a{background:#FAEEDA;color:#633806;border-color:#BA7517}"
        + ".apd-sechd{display:flex;align-items:center;gap:8px;margin:22px 0 10px}"
        + ".apd-seclbl{font-size:10px;font-weight:500;text-transform:uppercase;"
        +   "letter-spacing:.08em;color:#94a3b8;white-space:nowrap}"
        + ".apd-secline{flex:1;height:0.5px;background:#e2e8f0}"
        + ".apd-g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:14px}"
        + ".apd-g2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:14px}"
        + ".apd-g3b{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:14px}"
        // ── KPI cards ────────────────────────────────────────────
        + ".apd-kpi{background:#fff;border:0.5px solid #e2e8f0;border-radius:12px;"
        +   "padding:15px 17px;position:relative;overflow:hidden;cursor:default;"
        +   "transition:transform .18s ease,box-shadow .18s ease,border-color .2s ease}"
        + ".apd-kpi:hover{transform:translateY(-4px);"
        +   "box-shadow:0 8px 22px rgba(0,0,0,.09);border-color:#bbb}"
        + ".apd-kpi::before{content:'';position:absolute;top:0;left:0;right:0;"
        +   "height:3px;border-radius:12px 12px 0 0}"
        + ".apd-kpi.kb::before{background:#378ADD} .apd-kpi.kb .apd-kv{color:#0C447C}"
        + ".apd-kpi.kg::before{background:#639922} .apd-kpi.kg .apd-kv{color:#27500A}"
        + ".apd-kpi.kt::before{background:#1D9E75} .apd-kpi.kt .apd-kv{color:#085041}"
        + ".apd-kpi.ka::before{background:#BA7517} .apd-kpi.ka .apd-kv{color:#633806}"
        + ".apd-kpi.kp::before{background:#7F77DD} .apd-kpi.kp .apd-kv{color:#3C3489}"
        + ".apd-kpi.kc::before{background:#D85A30} .apd-kpi.kc .apd-kv{color:#712B13}"
        + ".apd-kl{font-size:11px;font-weight:500;color:#64748b;margin-bottom:4px}"
        + ".apd-kv{font-size:26px;font-weight:500;line-height:1;"
        +   "font-variant-numeric:tabular-nums;margin-bottom:4px}"
        + ".apd-trend{font-size:10px;font-weight:500;margin-bottom:5px}"
        + ".apd-trend-up{color:#27500A}"
        + ".apd-trend-dn{color:#791F1F}"
        + ".apd-trend-cn-up{color:#791F1F}"
        + ".apd-trend-cn-dn{color:#27500A}"
        + ".apd-trend-flat{color:#94a3b8}"
        + ".apd-ks{font-size:10px;color:#94a3b8;margin-bottom:8px}"
        + ".apd-kb{height:3px;border-radius:999px;background:#e2e8f0}"
        + ".apd-kbf{height:100%;border-radius:999px;transition:width 1.1s ease;width:0%}"
        // ── Cards ────────────────────────────────────────────────
        + ".apd-card{background:#fff;border:0.5px solid #e2e8f0;border-radius:12px;"
        +   "padding:16px 18px;transition:box-shadow .18s ease}"
        + ".apd-card:hover{box-shadow:0 4px 14px rgba(0,0,0,.07)}"
        + ".apd-ct{font-size:13px;font-weight:500;color:#111;margin-bottom:2px}"
        + ".apd-cs{font-size:11px;color:#94a3b8;margin-bottom:12px}"
        // ── Legend ───────────────────────────────────────────────
        + ".apd-leg{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:10px}"
        + ".apd-li{display:flex;align-items:center;gap:4px;font-size:11px;color:#64748b}"
        + ".apd-lsq{width:10px;height:10px;border-radius:2px;flex-shrink:0}"
        // ── Ranked list (top 3) ──────────────────────────────────
        + ".apd-rank-item{display:flex;align-items:center;gap:8px;padding:7px 0;"
        +   "border-bottom:0.5px solid #e2e8f0}"
        + ".apd-rank-item:last-child{border-bottom:none}"
        + ".apd-rank-num{width:20px;height:20px;border-radius:50%;background:#E6F1FB;"
        +   "color:#0C447C;font-size:11px;font-weight:500;display:flex;"
        +   "align-items:center;justify-content:center;flex-shrink:0}"
        + ".apd-rank-name{font-size:12px;font-weight:500;color:#111;margin-bottom:3px;"
        +   "white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        + ".apd-rank-bw{flex:1;height:4px;border-radius:999px;background:#e2e8f0}"
        + ".apd-rank-bf{height:100%;border-radius:999px;transition:width 1.1s ease;width:0%}"
        + ".apd-rank-pct{font-size:10px;color:#94a3b8;min-width:28px;text-align:right}"
        + ".apd-rank-cnt{font-size:11px;font-weight:500;color:#555;min-width:22px;text-align:right}"
        // ── Completion rate card ─────────────────────────────────
        + ".apd-comp-val{font-size:36px;font-weight:500;line-height:1;"
        +   "font-variant-numeric:tabular-nums;color:#27500A;margin-bottom:4px}"
        // ── Activity feed ────────────────────────────────────────
        + ".apd-frow{display:flex;align-items:flex-start;gap:9px;padding:8px 0;"
        +   "border-bottom:0.5px solid #e2e8f0}"
        + ".apd-frow:last-child{border-bottom:none}"
        + ".apd-fdot{width:7px;height:7px;border-radius:50%;flex-shrink:0;margin-top:5px}"
        + ".apd-fn{font-size:12px;font-weight:500;color:#111}"
        + ".apd-fm{font-size:11px;color:#94a3b8;margin-top:1px}"
        + ".apd-fr{display:flex;flex-direction:column;align-items:flex-end;gap:3px;flex-shrink:0}"
        // ── Status badges ────────────────────────────────────────
        + ".apd-badge{font-size:10px;font-weight:500;padding:1px 7px;border-radius:999px}"
        + ".apd-b-ap{background:#EAF3DE;color:#085041}"
        + ".apd-b-wt{background:#FAEEDA;color:#633806}"
        + ".apd-b-ic{background:#E6F1FB;color:#0C447C}"
        + ".apd-b-lb{background:#EEEDFE;color:#3C3489}"
        + ".apd-b-ph{background:#FAEEDA;color:#633806}"
        + ".apd-b-bp{background:#E1F5EE;color:#085041}"
        + ".apd-b-fu{background:#E6F1FB;color:#0C447C}"
        + ".apd-b-rs{background:#F1EFE8;color:#444441}"
        + ".apd-b-cn{background:#FCEBEB;color:#791F1F}"
        // ── Today's schedule ────────────────────────────────────
        + ".apd-sched-hd{display:grid;grid-template-columns:2fr 1.5fr 1fr 1fr;"
        +   "gap:8px;padding:6px 0;border-bottom:0.5px solid #e2e8f0;margin-bottom:4px}"
        + ".apd-sched-hd span{font-size:10px;font-weight:500;color:#94a3b8;"
        +   "text-transform:uppercase;letter-spacing:.04em}"
        + ".apd-sched-row{display:grid;grid-template-columns:2fr 1.5fr 1fr 1fr;"
        +   "gap:8px;padding:7px 0;border-bottom:0.5px solid #e2e8f0;"
        +   "align-items:center;transition:background .12s ease;border-radius:4px}"
        + ".apd-sched-row:last-child{border-bottom:none}"
        + ".apd-sched-row:hover{background:#f8fafc}"
        + ".apd-sched-name{font-size:12px;font-weight:500;color:#111;"
        +   "white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        + ".apd-sched-prac{font-size:11px;color:#64748b;"
        +   "white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        + ".apd-sched-opd{font-size:11px;color:#94a3b8;"
        +   "white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        // ── Day-of-week heatmap ──────────────────────────────────
        + ".apd-dow-g{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));"
        +   "gap:6px;margin-bottom:14px}"
        + ".apd-dow-c{border-radius:8px;padding:11px 8px;text-align:center;"
        +   "transition:transform .15s ease,box-shadow .15s ease;cursor:default}"
        + ".apd-dow-c:hover{transform:translateY(-2px);box-shadow:0 5px 14px rgba(0,0,0,.09)}"
        + ".apd-dow-t{font-size:11px;font-weight:500;margin-bottom:3px}"
        + ".apd-dow-n{font-size:20px;font-weight:500;line-height:1;font-variant-numeric:tabular-nums}"
        // ── Patient stats ────────────────────────────────────────
        + ".apd-pstat-g{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:10px}"
        + ".apd-pstat{background:#f8fafc;border-radius:10px;padding:12px 14px;text-align:center;"
        +   "transition:transform .15s ease}"
        + ".apd-pstat:hover{transform:translateY(-2px)}"
        + ".apd-pstat-val{font-size:22px;font-weight:500;line-height:1;"
        +   "font-variant-numeric:tabular-nums;color:#0C447C;margin-bottom:3px}"
        + ".apd-pstat-lbl{font-size:10px;font-weight:500;color:#94a3b8;"
        +   "text-transform:uppercase;letter-spacing:.04em}"
        // ── Snapshot stat cards ───────────────────────────────────
        + ".apd-stc{background:#f8fafc;border-radius:10px;padding:12px 14px;"
        +   "transition:transform .15s ease}"
        + ".apd-stc:hover{transform:translateY(-2px)}"
        + ".apd-stl{font-size:10px;font-weight:500;text-transform:uppercase;"
        +   "letter-spacing:.05em;color:#94a3b8;margin-bottom:5px}"
        + ".apd-stv{font-size:14px;font-weight:500;color:#111;margin-bottom:2px}"
        + ".apd-sts{font-size:10px;color:#94a3b8;margin-bottom:6px}"
        + ".apd-stb{height:3px;border-radius:999px;background:#e2e8f0}"
        + ".apd-stbf{height:100%;border-radius:999px;transition:width 1.1s ease;width:0%}"
        // ── Pipeline ─────────────────────────────────────────────
        + ".apd-pipe{display:flex;align-items:stretch;margin:12px 0 14px}"
        + ".apd-ps{flex:1;text-align:center}"
        + ".apd-pb{border-radius:10px;padding:11px 4px;"
        +   "transition:transform .15s ease,box-shadow .15s ease;cursor:default}"
        + ".apd-pb:hover{transform:translateY(-3px);box-shadow:0 5px 14px rgba(0,0,0,.09)}"
        + ".apd-pn{font-size:20px;font-weight:500;line-height:1;margin-bottom:2px;"
        +   "font-variant-numeric:tabular-nums}"
        + ".apd-pl{font-size:8px;font-weight:500;text-transform:uppercase;letter-spacing:.04em}"
        + ".apd-pa{width:14px;flex-shrink:0;display:flex;align-items:center;justify-content:center}"
        // ── Progress bars ────────────────────────────────────────
        + ".apd-pw{height:5px;border-radius:999px;background:#e2e8f0}"
        + ".apd-pf{height:100%;border-radius:999px;transition:width 1.2s ease;width:0%}"
        + ".apd-prow{display:flex;justify-content:space-between;margin-top:3px}"
        // ── Loading / empty ──────────────────────────────────────
        + ".apd-loading{text-align:center;padding:80px 20px;font-size:14px;color:#94a3b8}"
        + ".apd-empty{text-align:center;padding:24px 0;font-size:13px;color:#94a3b8;font-style:italic}"
        // ── Animations ───────────────────────────────────────────
        + "@keyframes _apdIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}"
        + ".apd-kpi:nth-child(1){animation:_apdIn .4s .04s ease both}"
        + ".apd-kpi:nth-child(2){animation:_apdIn .4s .08s ease both}"
        + ".apd-kpi:nth-child(3){animation:_apdIn .4s .12s ease both}"
        + ".apd-kpi:nth-child(4){animation:_apdIn .4s .16s ease both}"
        + ".apd-kpi:nth-child(5){animation:_apdIn .4s .20s ease both}"
        + ".apd-kpi:nth-child(6){animation:_apdIn .4s .24s ease both}"
        + ".apd-card{animation:_apdIn .4s .28s ease both}"
        + ".apd-stc{animation:_apdIn .4s .30s ease both}"
        + ".apd-pstat{animation:_apdIn .4s .32s ease both}";
    document.head.appendChild(el);
}


// ================================================================
//  LOAD
// ================================================================
function _apd_load(page) {
    $(page.main).find(".apd-wrap,.apd-loading,.apd-empty-page").remove();
    $(page.main).append('<div class="apd-loading">Loading dashboard…</div>');

    frappe.call({
        method:  "doctor_consultation_meet.services.appointment_dashboard.get_appointment_dashboard_data",
        freeze:  false,
        callback: function (r) {
            $(page.main).find(".apd-loading").remove();
            if (r.message) {
                _apd_load_chartjs(function () {
                    _apd_build(page, r.message);
                });
            } else {
                $(page.main).append(
                    '<div class="apd-empty-page" style="text-align:center;padding:60px;'
                    + 'font-size:14px;color:#94a3b8">No data found.</div>'
                );
            }
        },
        error: function () {
            $(page.main).find(".apd-loading").remove();
            $(page.main).append(
                '<div class="apd-empty-page" style="text-align:center;padding:60px;'
                + 'font-size:14px;color:#94a3b8">Failed to load. Please refresh.</div>'
            );
        }
    });
}


// ================================================================
//  CHART.JS LOADER
// ================================================================
function _apd_load_chartjs(cb) {
    if (window.Chart && typeof window.Chart.register === "function") { cb(); return; }
    var s   = document.createElement("script");
    s.src   = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js";
    s.onload = cb;
    s.onerror = function () {
        frappe.show_alert({ message: "Chart.js failed to load from CDN.", indicator: "red" }, 5);
    };
    document.head.appendChild(s);
}


// ================================================================
//  BUILD
// ================================================================
function _apd_build(page, data) {
    $(page.main).append(_apd_html(data));
    setTimeout(function () { _apd_animate(data); }, 120);
    setTimeout(function () { _apd_fill_bars();   }, 540);
    setTimeout(function () { _apd_charts(data); }, 340);
}


// ================================================================
//  STATUS BADGE HELPER
// ================================================================
var _APD_BADGE = {
    "Approved":       "apd-b-ap",
    "Waiting":        "apd-b-wt",
    "InConsultation": "apd-b-ic",
    "Lab":            "apd-b-lb",
    "Pharmacy":       "apd-b-ph",
    "Bill Paid":      "apd-b-bp",
    "Follow-Up":      "apd-b-fu",
    "ReScheduled":    "apd-b-rs",
    "Cancelled":      "apd-b-cn"
};

function _apd_badge(status) {
    var cls = _APD_BADGE[status] || "apd-b-wt";
    return '<span class="apd-badge ' + cls + '">' + (status || "—") + "</span>";
}


// ================================================================
//  TREND HELPER
// ================================================================
function _apd_trend_html(trend, invertColors) {
    if (!trend || trend.dir === "flat" || trend.pct === 0) {
        return '<div class="apd-trend apd-trend-flat">— stable</div>';
    }
    var isGood, arrow, cls;
    if (invertColors) {
        isGood = trend.dir === "down";
    } else {
        isGood = trend.dir === "up";
    }
    arrow = trend.dir === "up" ? "↑" : "↓";
    cls   = invertColors
        ? (trend.dir === "up" ? "apd-trend-cn-up" : "apd-trend-cn-dn")
        : (isGood             ? "apd-trend-up"     : "apd-trend-dn");
    return '<div class="apd-trend ' + cls + '">'
        + arrow + " " + trend.pct + "% vs last 7d"
        + "</div>";
}


// ================================================================
//  HTML BUILDER
// ================================================================
function _apd_html(d) {
    var kp = d.kpis          || {};
    var ch = d.charts         || {};
    var t3 = d.top3           || {};
    var pl = d.pipeline       || {};
    var ps = d.patient_stats  || {};
    var ts = d.today_schedule || [];
    var af = d.activity_feed  || [];

    var H = "";
    H += '<div class="apd-wrap">';

    // ── Top bar ──────────────────────────────────────────────────
    H += '<div class="apd-topbar">'
       + '<div>'
       + '<div class="apd-tb-ttl">Appointment Dashboard</div>'
       + '<div class="apd-tb-sub">TAALPLUS CHC Private Limited · Doctor Consultation Meet · Live data</div>'
       + '</div>'
       + '<div class="apd-tb-chips">'
       + '<span class="apd-chip apd-chip-b">' + (kp.total || 0) + " total appointments</span>"
       + '<span class="apd-chip apd-chip-g">' + (ps.total_patients || 0) + " unique patients</span>"
       + '<span class="apd-chip apd-chip-a">' + (kp.completion || 0) + "% completion rate</span>"
       + "</div></div>";

    // ════════════════════════════════════════════════════════════
    //  SECTION 1 — 6 KPI Number Cards
    // ════════════════════════════════════════════════════════════
    H += _apd_sechd("Section 1 — Operational KPIs");
    H += '<div class="apd-g3">';

    H += _apd_kpi("kb", "Total appointments",
        "apd-k1", kp.total || 0,
        _apd_trend_html(kp.total_trend, false),
        "All time · all statuses",
        "apd-kf1", "#378ADD", 100);

    H += _apd_kpi("kt", "Today's appointments",
        "apd-k2", kp.today || 0,
        _apd_trend_html(kp.today_trend, false),
        "appointment_date = " + frappe.datetime.get_today(),
        "apd-kf2", "#1D9E75",
        kp.total > 0 ? Math.round((kp.today / kp.total) * 100) : 0);

    H += _apd_kpi("kg", "Last 7 days",
        "apd-k3", kp.week || 0,
        _apd_trend_html(kp.week_trend, false),
        "Rolling 7-day window",
        "apd-kf3", "#639922",
        kp.total > 0 ? Math.round((kp.week / kp.total) * 100) : 0);

    H += _apd_kpi("ka", "Active right now",
        "apd-k4", kp.active || 0,
        _apd_trend_html(kp.active_trend, false),
        "Waiting + Approved + InConsultation",
        "apd-kf4", "#BA7517",
        kp.total > 0 ? Math.round((kp.active / kp.total) * 100) : 0);

    H += _apd_kpi("kp", "Completed (Bill Paid)",
        "apd-k5", kp.bill_paid || 0,
        _apd_trend_html(kp.bp_trend, false),
        "status = Bill Paid",
        "apd-kf5", "#7F77DD",
        kp.total > 0 ? Math.round((kp.bill_paid / kp.total) * 100) : 0);

    H += _apd_kpi("kc", "Cancelled",
        "apd-k6", kp.cancelled || 0,
        _apd_trend_html(kp.can_trend, true),
        "status = Cancelled",
        "apd-kf6", "#D85A30",
        kp.total > 0 ? Math.round((kp.cancelled / kp.total) * 100) : 0);

    H += "</div>";

    // ════════════════════════════════════════════════════════════
    //  SECTION 2 — Top 3 ranked + Completion rate
    // ════════════════════════════════════════════════════════════
    H += _apd_sechd("Section 2 — Snapshot summary");
    H += '<div class="apd-g3b">';

    // Top 3 Locations
    var locs = (t3.locations || []);
    var locRows = "";
    var locColors = ["#378ADD","#1D9E75","#7F77DD"];
    for (var li = 0; li < locs.length; li++) {
        locRows += '<div class="apd-rank-item">'
            + '<div class="apd-rank-num">' + (li + 1) + "</div>"
            + '<div style="flex:1;min-width:0">'
            + '<div class="apd-rank-name">' + (locs[li].name || "—") + "</div>"
            + '<div style="display:flex;align-items:center;gap:6px;margin-top:3px">'
            + '<div class="apd-rank-bw"><div class="apd-rank-bf" style="background:' + locColors[li] + '" data-w="' + (locs[li].pct || 0) + '"></div></div>'
            + '<span class="apd-rank-pct">' + (locs[li].pct || 0) + "%</span>"
            + "</div></div>"
            + '<div class="apd-rank-cnt">' + (locs[li].cnt || 0) + "</div>"
            + "</div>";
    }
    if (!locRows) locRows = '<div class="apd-empty">No location data</div>';

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Top 3 locations</div>'
       + '<div class="apd-cs">Appointments per branch</div>'
       + locRows + "</div>";

    // Top 3 Practitioners
    var pracs = (t3.practitioners || []);
    var pracRows = "";
    var pracColors = ["#D85A30","#639922","#BA7517"];
    for (var pi = 0; pi < pracs.length; pi++) {
        pracRows += '<div class="apd-rank-item">'
            + '<div class="apd-rank-num">' + (pi + 1) + "</div>"
            + '<div style="flex:1;min-width:0">'
            + '<div class="apd-rank-name">' + (pracs[pi].name || "—") + "</div>"
            + '<div style="display:flex;align-items:center;gap:6px;margin-top:3px">'
            + '<div class="apd-rank-bw"><div class="apd-rank-bf" style="background:' + pracColors[pi] + '" data-w="' + (pracs[pi].pct || 0) + '"></div></div>'
            + '<span class="apd-rank-pct">' + (pracs[pi].pct || 0) + "%</span>"
            + "</div></div>"
            + '<div class="apd-rank-cnt">' + (pracs[pi].cnt || 0) + "</div>"
            + "</div>";
    }
    if (!pracRows) pracRows = '<div class="apd-empty">No practitioner data</div>';

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Top 3 practitioners</div>'
       + '<div class="apd-cs">Appointments per practitioner</div>'
       + pracRows + "</div>";

    // Completion Rate Card
    var compRate = kp.completion || 0;
    H += '<div class="apd-card" style="display:flex;flex-direction:column;justify-content:center">'
       + '<div style="font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8;margin-bottom:8px">Completion rate</div>'
       + '<div class="apd-comp-val" id="apd-comp">' + compRate + "%</div>"
       + '<div style="font-size:11px;color:#94a3b8;margin-bottom:14px">Bill Paid ÷ Total appointments</div>'
       + '<div class="apd-pw"><div class="apd-pf" style="background:#639922" data-w="' + compRate + '"></div></div>'
       + '<div class="apd-prow">'
       + '<span style="font-size:10px;color:#94a3b8">0%</span>'
       + '<span style="font-size:11px;font-weight:500;color:#27500A">' + compRate + "%</span>"
       + '<span style="font-size:10px;color:#94a3b8">100%</span>'
       + "</div>"
       + '<div style="margin-top:14px;padding-top:14px;border-top:0.5px solid #e2e8f0">'
       + '<div style="display:flex;justify-content:space-between">'
       + '<div><div style="font-size:20px;font-weight:500;color:#27500A" id="apd-bp2">' + (kp.bill_paid || 0) + "</div>"
       + '<div style="font-size:10px;color:#94a3b8">Bill Paid</div></div>'
       + '<div style="text-align:right"><div style="font-size:20px;font-weight:500;color:#D85A30" id="apd-cn2">' + (kp.cancelled || 0) + "</div>"
       + '<div style="font-size:10px;color:#94a3b8">Cancelled</div></div>'
       + "</div></div></div>";

    H += "</div>";

    // ════════════════════════════════════════════════════════════
    //  SECTION 3 — Status doughnut + Gender + Age group bar
    // ════════════════════════════════════════════════════════════
    H += _apd_sechd("Section 3 — Status, gender & age distribution charts");
    H += '<div class="apd-g3">';

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Appointment status</div>'
       + '<div class="apd-cs">5 grouped buckets</div>'
       + _apd_leg([
           {c:"#27ae60", l:"Completed"},
           {c:"#f39c12", l:"Active"},
           {c:"#2490ef", l:"Treatment"},
           {c:"#8e44ad", l:"Follow-Up"},
           {c:"#e74c3c", l:"Cancelled"}
         ])
       + '<div style="position:relative;height:180px">'
       + '<canvas id="apd-ch1" role="img" aria-label="Status grouped doughnut">Appointment status distribution</canvas>'
       + "</div></div>";

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Gender distribution</div>'
       + '<div class="apd-cs">From Appointment Data records</div>'
       + _apd_leg([
           {c:"#378ADD", l:"Male"},
           {c:"#D4537E", l:"Female"},
           {c:"#888780", l:"Other"}
         ])
       + '<div style="position:relative;height:180px">'
       + '<canvas id="apd-ch2" role="img" aria-label="Gender distribution doughnut">Gender distribution</canvas>'
       + "</div></div>";

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Patient age groups</div>'
       + '<div class="apd-cs">Parsed from age field</div>'
       + '<div style="position:relative;height:210px">'
       + '<canvas id="apd-ch3" role="img" aria-label="Age group bar chart">Patient age groups</canvas>'
       + "</div></div>";

    H += "</div>";

    // ════════════════════════════════════════════════════════════
    //  SECTION 4 — Monthly trend + Day-of-week heatmap
    // ════════════════════════════════════════════════════════════
    H += _apd_sechd("Section 4 — Monthly trend & day-of-week heatmap");
    H += '<div class="apd-g2">';

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Monthly appointment trend</div>'
       + '<div class="apd-cs">Bookings grouped by appointment month · last 6 months</div>'
       + _apd_leg([{c:"#7F77DD", l:"Appointments per month"}])
       + '<div style="position:relative;height:190px">'
       + '<canvas id="apd-ch4" role="img" aria-label="Monthly trend line chart">Monthly trend</canvas>'
       + "</div></div>";

    // Day of week heatmap (rendered as colored cells, not a chart)
    var dowData  = ch.day_of_week || {};
    var dowLbls  = dowData.labels  || ["Mon","Tue","Wed","Thu","Fri","Sat"];
    var dowVals  = (dowData.datasets && dowData.datasets[0] && dowData.datasets[0].values) || [0,0,0,0,0,0];
    var dowMax   = Math.max.apply(null, dowVals) || 1;
    var dowTotal = dowVals.reduce(function (a, b) { return a + b; }, 0) || 1;
    var hCfg     = {
        high: { bg: "#85B7EB", tc: "#042C53", lc: "#042C53" },
        mid:  { bg: "#B5D4F4", tc: "#0C447C", lc: "#185FA5" },
        low:  { bg: "#E6F1FB", tc: "#0C447C", lc: "#378ADD" }
    };
    var dowCells = "";
    for (var di = 0; di < dowLbls.length; di++) {
        var dv  = dowVals[di] || 0;
        var dr  = dv / dowMax;
        var dint = dr > 0.75 ? "high" : dr > 0.35 ? "mid" : "low";
        var dcfg = hCfg[dint];
        dowCells += '<div class="apd-dow-c" style="background:' + dcfg.bg + '">'
            + '<div class="apd-dow-t" style="color:' + dcfg.lc + '">' + dowLbls[di] + "</div>"
            + '<div class="apd-dow-n" style="color:' + dcfg.tc + '">' + dv + "</div>"
            + "</div>";
    }
    var peakIdx  = dowVals.indexOf(Math.max.apply(null, dowVals));
    var peakDay  = dowLbls[peakIdx] || "";
    var peakPct  = Math.round((dowVals[peakIdx] || 0) / dowTotal * 100);

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Day-of-week heatmap</div>'
       + '<div class="apd-cs">Appointments per weekday · last 3 months</div>'
       + '<div class="apd-dow-g">' + dowCells + "</div>"
       + '<div style="border-top:0.5px solid #e2e8f0;padding-top:12px">'
       + '<div style="font-size:11px;font-weight:500;color:#64748b;margin-bottom:6px">'
       + "Busiest day — " + peakDay + " · " + peakPct + "%"
       + "</div>"
       + '<div class="apd-pw"><div class="apd-pf" id="apd-dow-bar" style="background:#378ADD" data-w="' + peakPct + '"></div></div>'
       + '<div class="apd-prow">'
       + '<span style="font-size:10px;color:#94a3b8">0%</span>'
       + '<span style="font-size:10px;color:#94a3b8">100%</span>'
       + "</div></div></div>";

    H += "</div>";

    // ════════════════════════════════════════════════════════════
    //  SECTION 5 — Practitioner bar + OPD department bar
    // ════════════════════════════════════════════════════════════
    var pracH = Math.max(220, Math.min((ch.practitioner && ch.practitioner.labels && ch.practitioner.labels.length) || 3, 8) * 40 + 80);
    var opdH  = Math.max(220, Math.min((ch.opd && ch.opd.labels && ch.opd.labels.length) || 3, 8) * 40 + 80);

    H += _apd_sechd("Section 5 — Volume by practitioner & OPD department");
    H += '<div class="apd-g2">';

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Appointments by practitioner</div>'
       + '<div class="apd-cs">Total bookings · top 8</div>'
       + '<div style="position:relative;height:' + pracH + 'px">'
       + '<canvas id="apd-ch5" role="img" aria-label="Practitioner bar chart">Practitioner appointments</canvas>'
       + "</div></div>";

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Appointments by OPD department</div>'
       + '<div class="apd-cs">Total bookings · top 8</div>'
       + '<div style="position:relative;height:' + opdH + 'px">'
       + '<canvas id="apd-ch6" role="img" aria-label="OPD department bar chart">OPD department appointments</canvas>'
       + "</div></div>";

    H += "</div>";

    // ════════════════════════════════════════════════════════════
    //  SECTION 6 — Today's schedule
    // ════════════════════════════════════════════════════════════
    H += _apd_sechd("Section 6 — Today's schedule (" + frappe.datetime.get_today() + ")");

    if (ts.length === 0) {
        H += '<div class="apd-card"><div class="apd-empty" style="padding:32px 0">'
           + "No appointments scheduled for today."
           + "</div></div>";
    } else {
        var schedRows = "";
        for (var si = 0; si < ts.length; si++) {
            var sc = ts[si];
            schedRows += '<div class="apd-sched-row">'
                + '<div class="apd-sched-name">' + (sc.patient_display || "Unknown") + "</div>"
                + '<div class="apd-sched-prac">' + (sc.practitioner || "—") + "</div>"
                + '<div class="apd-sched-opd">'  + (sc.opd_allotted || "—") + "</div>"
                + "<div>" + _apd_badge(sc.status) + "</div>"
                + "</div>";
        }
        H += '<div class="apd-card">'
           + '<div class="apd-ct">Today\'s appointments</div>'
           + '<div class="apd-cs">' + ts.length + " appointment" + (ts.length !== 1 ? "s" : "") + " scheduled</div>"
           + '<div class="apd-sched-hd">'
           + "<span>Patient</span><span>Practitioner</span><span>OPD Dept</span><span>Status</span>"
           + "</div>"
           + schedRows + "</div>";
    }

    // ════════════════════════════════════════════════════════════
    //  SECTION 7 — Activity feed + Patient return stats
    // ════════════════════════════════════════════════════════════
    H += _apd_sechd("Section 7 — Activity feed & patient statistics");
    H += '<div class="apd-g2">';

    // Activity feed
    var feedColors = ["#378ADD","#D85A30","#7F77DD","#639922","#1D9E75"];
    var feedHtml   = "";
    for (var fi = 0; fi < af.length; fi++) {
        var f = af[fi];
        feedHtml += '<div class="apd-frow">'
            + '<span class="apd-fdot" style="background:' + feedColors[fi % feedColors.length] + '"></span>'
            + '<div style="flex:1">'
            + '<div class="apd-fn">' + (f.patient_display || "Unknown") + "</div>"
            + '<div class="apd-fm">' + (f.practitioner || "—")
            + " · " + (f.appointment_date || "—")
            + (f.location ? " · " + f.location : "")
            + "</div></div>"
            + '<div class="apd-fr">'
            + _apd_badge(f.status)
            + '<span style="font-size:10px;color:#94a3b8">' + (f.opd_allotted || "—") + "</span>"
            + "</div></div>";
    }
    if (!feedHtml) feedHtml = '<div class="apd-empty">No recent records.</div>';

    H += '<div class="apd-card">'
       + '<div class="apd-ct">Recent activity feed</div>'
       + '<div class="apd-cs">Last 5 appointments · newest first</div>'
       + feedHtml + "</div>";

    // Patient return stats
    H += '<div class="apd-card">'
       + '<div class="apd-ct">Patient statistics</div>'
       + '<div class="apd-cs">Return behaviour & engagement metrics</div>'
       + '<div class="apd-pstat-g">'
       + '<div class="apd-pstat">'
       + '<div class="apd-pstat-val" id="apd-ps1">' + (ps.total_patients || 0) + "</div>"
       + '<div class="apd-pstat-lbl">Unique patients</div></div>'
       + '<div class="apd-pstat">'
       + '<div class="apd-pstat-val" id="apd-ps2">' + (ps.returning || 0) + "</div>"
       + '<div class="apd-pstat-lbl">Returning patients</div></div>'
       + '<div class="apd-pstat">'
       + '<div class="apd-pstat-val" id="apd-ps3">' + (ps.return_rate || 0) + "%</div>"
       + '<div class="apd-pstat-lbl">Return rate</div></div>'
       + "</div>"
       + '<div style="border-top:0.5px solid #e2e8f0;padding-top:14px;margin-top:4px">'
       + '<div style="font-size:11px;font-weight:500;color:#64748b;margin-bottom:6px">'
       + "Return rate — " + (ps.return_rate || 0) + "% of patients visit more than once"
       + "</div>"
       + '<div class="apd-pw"><div class="apd-pf" id="apd-rr-bar" style="background:#7F77DD" data-w="' + (ps.return_rate || 0) + '"></div></div>'
       + '<div class="apd-prow">'
       + '<span style="font-size:10px;color:#94a3b8">0%</span>'
       + '<span style="font-size:13px;font-weight:500;color:#3C3489">' + (ps.return_rate || 0) + "%</span>"
       + '<span style="font-size:10px;color:#94a3b8">100%</span>'
       + "</div>"
       + '<div style="margin-top:14px;padding-top:14px;border-top:0.5px solid #e2e8f0;'
       + 'display:flex;justify-content:space-between;align-items:center">'
       + '<span style="font-size:11px;color:#64748b">Avg appointments per patient</span>'
       + '<span style="font-size:18px;font-weight:500;color:#0C447C" id="apd-avg">' + (ps.avg_per_patient || 0) + "</span>"
       + "</div></div></div>";

    H += "</div>";

    // ════════════════════════════════════════════════════════════
    //  SECTION 8 — Full patient journey pipeline (all 9 statuses)
    // ════════════════════════════════════════════════════════════
    H += _apd_sechd("Section 8 — Patient journey pipeline");

    var plSt = pl.statuses || {};
    var plT  = pl.total    || 0;
    var bpR  = plT > 0 ? Math.round((plSt["Bill Paid"] || 0) / plT * 100) : 0;

    var pColors = {
        "Waiting":        ["#FAEEDA","#633806","#854F0B"],
        "Approved":       ["#EAF3DE","#27500A","#3B6D11"],
        "InConsultation": ["#E6F1FB","#0C447C","#185FA5"],
        "Lab":            ["#EEEDFE","#3C3489","#534AB7"],
        "Pharmacy":       ["#FAEEDA","#633806","#854F0B"],
        "Bill Paid":      ["#E1F5EE","#085041","#0F6E56"],
        "Follow-Up":      ["#E6F1FB","#0C447C","#185FA5"],
        "ReScheduled":    ["#F1EFE8","#444441","#5F5E5A"],
        "Cancelled":      ["#FCEBEB","#791F1F","#A32D2D"]
    };
    var pIds = {
        "Waiting":"apd-pp1","Approved":"apd-pp2","InConsultation":"apd-pp3",
        "Lab":"apd-pp4","Pharmacy":"apd-pp5","Bill Paid":"apd-pp6",
        "Follow-Up":"apd-pp7","ReScheduled":"apd-pp8","Cancelled":"apd-pp9"
    };
    var pLabels = {
        "InConsultation":"In Consult","Bill Paid":"Bill Paid","Follow-Up":"Follow-Up","ReScheduled":"Resched."
    };

    H += '<div class="apd-card">';
    H += '<div class="apd-ct">Patient journey pipeline</div>';
    H += '<div class="apd-cs">Appointment count at each stage · all time</div>';
    H += '<div class="apd-pipe">';

    var stages = ["Waiting","Approved","InConsultation","Lab","Pharmacy","Bill Paid","Follow-Up","ReScheduled","Cancelled"];
    for (var qi = 0; qi < stages.length; qi++) {
        var st  = stages[qi];
        var cfg = pColors[st];
        H += '<div class="apd-ps">'
           + '<div class="apd-pb" style="background:' + cfg[0] + '">'
           + '<div class="apd-pn" style="color:' + cfg[1] + '" id="' + pIds[st] + '">' + (plSt[st] || 0) + "</div>"
           + '<div class="apd-pl" style="color:' + cfg[2] + '">' + (pLabels[st] || st) + "</div>"
           + "</div></div>";
        if (qi < stages.length - 1) {
            var isDown = st === "Bill Paid";
            H += _apd_pipe_arrow(isDown);
        }
    }
    H += "</div>";

    H += '<div style="background:#f8fafc;border-radius:8px;padding:10px 14px">'
       + '<div style="font-size:11px;font-weight:500;color:#64748b;margin-bottom:5px">Overall completion rate (Bill Paid ÷ Total)</div>'
       + '<div class="apd-pw"><div class="apd-pf" id="apd-pipe-bar" style="background:#639922" data-w="' + bpR + '"></div></div>'
       + '<div class="apd-prow">'
       + '<span style="font-size:10px;color:#94a3b8">0%</span>'
       + '<span style="font-size:13px;font-weight:500;color:#27500A">' + bpR + "%</span>"
       + '<span style="font-size:10px;color:#94a3b8">100%</span>'
       + "</div></div>";

    H += "</div>"; // close card
    H += "</div>"; // close apd-wrap

    return H;
}


// ================================================================
//  COMPONENT HELPERS
// ================================================================
function _apd_sechd(lbl) {
    return '<div class="apd-sechd">'
        + '<span class="apd-seclbl">' + lbl + "</span>"
        + '<div class="apd-secline"></div>'
        + "</div>";
}

function _apd_kpi(cls, lbl, vid, val, trendHtml, sub, fid, fc, fw) {
    return '<div class="apd-kpi ' + cls + '">'
        + '<div class="apd-kl">' + lbl + "</div>"
        + '<div class="apd-kv" id="' + vid + '">' + val + "</div>"
        + trendHtml
        + '<div class="apd-ks">' + sub + "</div>"
        + '<div class="apd-kb"><div class="apd-kbf" id="' + fid + '" style="background:' + fc + '" data-w="' + fw + '"></div></div>'
        + "</div>";
}

function _apd_leg(items) {
    var h = '<div class="apd-leg">';
    for (var i = 0; i < items.length; i++) {
        h += '<span class="apd-li"><span class="apd-lsq" style="background:' + items[i].c + '"></span>' + items[i].l + "</span>";
    }
    return h + "</div>";
}

function _apd_pipe_arrow(down) {
    if (down) {
        return '<div class="apd-pa">'
            + '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
            + '<path d="M6 2v8M3 7l3 3 3-3" stroke="#E24B4A" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>'
            + "</svg></div>";
    }
    return '<div class="apd-pa">'
        + '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
        + '<path d="M2 6h8M7 3l3 3-3 3" stroke="#cbd5e1" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>'
        + "</svg></div>";
}


// ================================================================
//  ANIMATIONS
// ================================================================
function _apd_animate(d) {
    var kp = d.kpis         || {};
    var ps = d.patient_stats || {};
    var pl = d.pipeline      || {};
    var plSt = pl.statuses   || {};
    var INR  = function (n) { return Math.round(n).toLocaleString("en-IN"); };

    function cu(id, target, pre, suf) {
        var el = document.getElementById(id);
        if (!el) return;
        var s    = 0;
        var step = Math.max(1, Math.ceil(target / 25));
        var t    = setInterval(function () {
            s += step;
            if (s >= target) {
                el.textContent = (pre || "") + INR(Math.round(target)) + (suf || "");
                clearInterval(t);
            } else {
                el.textContent = (pre || "") + INR(Math.round(s)) + (suf || "");
            }
        }, 28);
    }

    cu("apd-k1",  kp.total       || 0, "",  "");
    cu("apd-k2",  kp.today       || 0, "",  "");
    cu("apd-k3",  kp.week        || 0, "",  "");
    cu("apd-k4",  kp.active      || 0, "",  "");
    cu("apd-k5",  kp.bill_paid   || 0, "",  "");
    cu("apd-k6",  kp.cancelled   || 0, "",  "");
    cu("apd-bp2", kp.bill_paid   || 0, "",  "");
    cu("apd-cn2", kp.cancelled   || 0, "",  "");
    cu("apd-ps1", ps.total_patients  || 0, "", "");
    cu("apd-ps2", ps.returning       || 0, "", "");
    cu("apd-ps3", ps.return_rate     || 0, "", "%");
    cu("apd-pp1", plSt["Waiting"]        || 0, "", "");
    cu("apd-pp2", plSt["Approved"]       || 0, "", "");
    cu("apd-pp3", plSt["InConsultation"] || 0, "", "");
    cu("apd-pp4", plSt["Lab"]            || 0, "", "");
    cu("apd-pp5", plSt["Pharmacy"]       || 0, "", "");
    cu("apd-pp6", plSt["Bill Paid"]      || 0, "", "");
    cu("apd-pp7", plSt["Follow-Up"]      || 0, "", "");
    cu("apd-pp8", plSt["ReScheduled"]    || 0, "", "");
    cu("apd-pp9", plSt["Cancelled"]      || 0, "", "");
}

function _apd_fill_bars() {
    document.querySelectorAll("[data-w]").forEach(function (el) {
        el.style.width = (el.getAttribute("data-w") || 0) + "%";
    });
}


// ================================================================
//  CHARTS — Chart.js 4.4.1
// ================================================================
function _apd_charts(d) {
    var ch   = d.charts || {};
    var dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    var gc   = dark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.06)";
    var lc   = dark ? "#94a3b8" : "#888780";
    var bdr  = dark ? "#1a1a1a" : "#ffffff";

    var dOpts = {
        responsive:          true,
        maintainAspectRatio: false,
        cutout:              "65%",
        animation:           { animateRotate: true, duration: 800 },
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: function (ctx) {
                        var tot = ctx.dataset.data.reduce(function (a, b) { return a + b; }, 0);
                        var pct = tot > 0 ? Math.round(ctx.parsed / tot * 100) : 0;
                        return " " + ctx.label + ": " + ctx.parsed + " (" + pct + "%)";
                    }
                }
            }
        }
    };

    // Chart 1 — Status grouped doughnut (5 buckets)
    var c1 = document.getElementById("apd-ch1");
    if (c1) {
        var sg = ch.status_grouped || {};
        new Chart(c1, {
            type: "doughnut",
            data: {
                labels:   sg.labels   || [],
                datasets: [{
                    data:            (sg.datasets && sg.datasets[0] && sg.datasets[0].values) || [],
                    backgroundColor: ["#27ae60","#f39c12","#2490ef","#8e44ad","#e74c3c"],
                    borderWidth:     3,
                    borderColor:     bdr,
                    hoverOffset:     8
                }]
            },
            options: dOpts
        });
    }

    // Chart 2 — Gender doughnut
    var c2 = document.getElementById("apd-ch2");
    if (c2) {
        var gd = ch.gender || {};
        new Chart(c2, {
            type: "doughnut",
            data: {
                labels:   gd.labels   || [],
                datasets: [{
                    data:            (gd.datasets && gd.datasets[0] && gd.datasets[0].values) || [],
                    backgroundColor: ["#378ADD","#D4537E","#888780"],
                    borderWidth:     3,
                    borderColor:     bdr,
                    hoverOffset:     8
                }]
            },
            options: dOpts
        });
    }

    // Chart 3 — Age group vertical bar
    var c3 = document.getElementById("apd-ch3");
    if (c3) {
        var ag = ch.age_groups || {};
        new Chart(c3, {
            type: "bar",
            data: {
                labels:   ag.labels || [],
                datasets: [{
                    label:           "Patients",
                    data:            (ag.datasets && ag.datasets[0] && ag.datasets[0].values) || [],
                    backgroundColor: ["#378ADD","#1D9E75","#D85A30","#7F77DD","#888780"],
                    borderRadius:    6,
                    borderSkipped:   false
                }]
            },
            options: {
                responsive:          true,
                maintainAspectRatio: false,
                animation:           { duration: 900 },
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: function (ctx) { return " " + ctx.parsed.y + " patients"; }}}
                },
                scales: {
                    x: { ticks: { color: lc, font: { size: 11 } }, grid: { display: false }, border: { display: false }},
                    y: { beginAtZero: true, ticks: { color: lc, font: { size: 11 }, stepSize: 1 }, grid: { color: gc }, border: { display: false }}
                }
            }
        });
    }

    // Chart 4 — Monthly trend line
    var c4 = document.getElementById("apd-ch4");
    if (c4) {
        var mt = ch.monthly || {};
        new Chart(c4, {
            type: "line",
            data: {
                labels:   (mt.labels && mt.labels.length > 0) ? mt.labels : ["No data"],
                datasets: [{
                    label:               "Appointments",
                    data:                (mt.datasets && mt.datasets[0] && mt.datasets[0].values) || [0],
                    borderColor:         "#7F77DD",
                    backgroundColor:     dark ? "rgba(127,119,221,0.12)" : "rgba(127,119,221,0.08)",
                    borderWidth:         2,
                    pointBackgroundColor: "#7F77DD",
                    pointBorderColor:    bdr,
                    pointBorderWidth:    2,
                    pointRadius:         5,
                    pointHoverRadius:    7,
                    tension:             0.4,
                    fill:                true
                }]
            },
            options: {
                responsive:          true,
                maintainAspectRatio: false,
                animation:           { duration: 900 },
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: function (ctx) { return " " + ctx.parsed.y + " appointments"; }}}
                },
                scales: {
                    x: { ticks: { color: lc, font: { size: 11 }, autoSkip: false, maxRotation: 30 }, grid: { color: gc }, border: { display: false }},
                    y: { beginAtZero: true, ticks: { color: lc, font: { size: 11 }, stepSize: 1 }, grid: { color: gc }, border: { display: false }}
                }
            }
        });
    }

    // Chart 5 — Practitioner horizontal bar
    var c5 = document.getElementById("apd-ch5");
    if (c5) {
        var pr = ch.practitioner || {};
        var prLabels = (pr.labels  || []);
        var prData   = (pr.datasets && pr.datasets[0] && pr.datasets[0].values) || [];
        var prColors = ["#D85A30","#378ADD","#7F77DD","#1D9E75","#639922","#888780","#D4537E","#BA7517"];
        new Chart(c5, {
            type: "bar",
            data: {
                labels:   prLabels,
                datasets: [{
                    label:           "Appointments",
                    data:            prData,
                    backgroundColor: prLabels.map(function (_, i) { return prColors[i % prColors.length]; }),
                    borderRadius:    6,
                    borderSkipped:   false
                }]
            },
            options: {
                indexAxis:           "y",
                responsive:          true,
                maintainAspectRatio: false,
                animation:           { duration: 900 },
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: function (ctx) { return " " + ctx.parsed.x + " appointments"; }}}
                },
                scales: {
                    x: { beginAtZero: true, ticks: { color: lc, font: { size: 11 } }, grid: { color: gc }, border: { display: false }},
                    y: { ticks: { color: lc, font: { size: 11 } }, grid: { display: false }, border: { display: false }}
                }
            }
        });
    }

    // Chart 6 — OPD department horizontal bar
    var c6 = document.getElementById("apd-ch6");
    if (c6) {
        var op = ch.opd || {};
        var opLabels = (op.labels || []);
        var opData   = (op.datasets && op.datasets[0] && op.datasets[0].values) || [];
        var opColors = ["#378ADD","#1D9E75","#7F77DD","#D85A30","#639922","#BA7517","#D4537E","#888780"];
        new Chart(c6, {
            type: "bar",
            data: {
                labels:   opLabels,
                datasets: [{
                    label:           "Appointments",
                    data:            opData,
                    backgroundColor: opLabels.map(function (_, i) { return opColors[i % opColors.length]; }),
                    borderRadius:    6,
                    borderSkipped:   false
                }]
            },
            options: {
                indexAxis:           "y",
                responsive:          true,
                maintainAspectRatio: false,
                animation:           { duration: 900 },
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: function (ctx) { return " " + ctx.parsed.x + " appointments"; }}}
                },
                scales: {
                    x: { beginAtZero: true, ticks: { color: lc, font: { size: 11 } }, grid: { color: gc }, border: { display: false }},
                    y: { ticks: { color: lc, font: { size: 11 } }, grid: { display: false }, border: { display: false }}
                }
            }
        });
    }
}