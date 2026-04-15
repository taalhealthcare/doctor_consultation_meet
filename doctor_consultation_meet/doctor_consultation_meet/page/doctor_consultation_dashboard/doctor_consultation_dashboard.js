// ================================================================
//  Doctor Consultation Dashboard
//  App  : doctor_consultation_meet
//  Page : doctor-consultation-dashboard
//  URL  : /app/doctor-consultation-dashboard
// ================================================================

frappe.pages["doctor-consultation-dashboard"].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "Doctor Consultation Dashboard",
        single_column: true
    });

    page.add_inner_button(__("Refresh Dashboard"), function () {
        _dc_load(page);
    });

    _dc_inject_styles();
    _dc_load(page);
};


// ================================================================
//  STYLES
// ================================================================
function _dc_inject_styles() {
    if (document.getElementById("_dc_styles")) return;
    var el = document.createElement("style");
    el.id = "_dc_styles";
    el.textContent = ""
        + ".dcw{padding:16px 20px 48px;max-width:1400px;margin:0 auto}"
        + ".dc-topbar{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;"
        + "background:#fff;border:0.5px solid #e2e8f0;border-radius:12px;margin-bottom:20px;"
        + "flex-wrap:wrap;gap:10px}"
        + ".dc-tb-ttl{font-size:16px;font-weight:500;color:#111;margin-bottom:2px}"
        + ".dc-tb-sub{font-size:11px;color:#94a3b8}"
        + ".dc-tb-chips{display:flex;gap:8px;flex-wrap:wrap}"
        + ".dc-chip{font-size:11px;font-weight:500;padding:3px 10px;border-radius:999px;border:0.5px solid}"
        + ".dc-chip-g{background:#EAF3DE;color:#27500A;border-color:#639922}"
        + ".dc-chip-b{background:#E6F1FB;color:#0C447C;border-color:#378ADD}"
        + ".dc-chip-a{background:#FAEEDA;color:#633806;border-color:#BA7517}"
        + ".dc-sechd{display:flex;align-items:center;gap:8px;margin:22px 0 10px}"
        + ".dc-seclbl{font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.08em;"
        + "color:#94a3b8;white-space:nowrap}"
        + ".dc-secline{flex:1;height:0.5px;background:#e2e8f0}"
        + ".dc-g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:14px}"
        + ".dc-g2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:14px}"
        + ".dc-g3b{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:14px}"
        + ".dc-kpi{background:#fff;border:0.5px solid #e2e8f0;border-radius:12px;padding:15px 17px;"
        + "position:relative;overflow:hidden;cursor:default;"
        + "transition:transform .18s ease,box-shadow .18s ease,border-color .2s ease}"
        + ".dc-kpi:hover{transform:translateY(-4px);box-shadow:0 8px 22px rgba(0,0,0,.09);border-color:#bbb}"
        + ".dc-kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:12px 12px 0 0}"
        + ".dc-kpi.kg::before{background:#639922} .dc-kpi.kg .dc-kv{color:#27500A}"
        + ".dc-kpi.ka::before{background:#BA7517} .dc-kpi.ka .dc-kv{color:#633806}"
        + ".dc-kpi.kp::before{background:#7F77DD} .dc-kpi.kp .dc-kv{color:#3C3489}"
        + ".dc-kpi.kb::before{background:#378ADD} .dc-kpi.kb .dc-kv{color:#0C447C}"
        + ".dc-kpi.kt::before{background:#1D9E75} .dc-kpi.kt .dc-kv{color:#085041}"
        + ".dc-kpi.kc::before{background:#D85A30} .dc-kpi.kc .dc-kv{color:#712B13}"
        + ".dc-kl{font-size:11px;font-weight:500;color:#64748b;margin-bottom:4px}"
        + ".dc-kv{font-size:26px;font-weight:500;line-height:1;font-variant-numeric:tabular-nums;margin-bottom:5px}"
        + ".dc-ks{font-size:10px;color:#94a3b8;margin-bottom:8px}"
        + ".dc-kb{height:3px;border-radius:999px;background:#e2e8f0}"
        + ".dc-kbf{height:100%;border-radius:999px;transition:width 1.1s ease;width:0%}"
        + ".dc-card{background:#fff;border:0.5px solid #e2e8f0;border-radius:12px;padding:16px 18px;"
        + "transition:box-shadow .18s ease}"
        + ".dc-card:hover{box-shadow:0 4px 14px rgba(0,0,0,.07)}"
        + ".dc-ct{font-size:13px;font-weight:500;color:#111;margin-bottom:2px}"
        + ".dc-cs{font-size:11px;color:#94a3b8;margin-bottom:12px}"
        + ".dc-leg{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:10px}"
        + ".dc-li{display:flex;align-items:center;gap:4px;font-size:11px;color:#64748b}"
        + ".dc-lsq{width:10px;height:10px;border-radius:2px;flex-shrink:0}"
        + ".dc-frow{display:flex;align-items:flex-start;gap:9px;padding:8px 0;border-bottom:0.5px solid #e2e8f0}"
        + ".dc-frow:last-child{border-bottom:none}"
        + ".dc-fdot{width:7px;height:7px;border-radius:50%;flex-shrink:0;margin-top:5px}"
        + ".dc-fn{font-size:12px;font-weight:500;color:#111}"
        + ".dc-fm{font-size:11px;color:#94a3b8;margin-top:1px}"
        + ".dc-fr{display:flex;flex-direction:column;align-items:flex-end;gap:3px;flex-shrink:0}"
        + ".dc-badge{font-size:10px;font-weight:500;padding:1px 7px;border-radius:999px}"
        + ".dc-bs{background:#E1F5EE;color:#085041}"
        + ".dc-bf{background:#FCEBEB;color:#791F1F}"
        + ".dc-bp{background:#FAEEDA;color:#633806}"
        + ".dc-bq{background:#E6F1FB;color:#0C447C}"
        + ".dc-hg{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-bottom:14px}"
        + ".dc-hc{border-radius:8px;padding:11px 8px;text-align:center;"
        + "transition:transform .15s ease,box-shadow .15s ease;cursor:default}"
        + ".dc-hc:hover{transform:translateY(-2px);box-shadow:0 5px 14px rgba(0,0,0,.09)}"
        + ".dc-ht{font-size:10px;font-weight:500;margin-bottom:3px}"
        + ".dc-hn{font-size:20px;font-weight:500;line-height:1;font-variant-numeric:tabular-nums}"
        + ".dc-hl{font-size:10px;margin-top:2px}"
        + ".dc-srow{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:0.5px solid #e2e8f0}"
        + ".dc-srow:last-child{border-bottom:none}"
        + ".dc-sn{font-size:12px;color:#111;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        + ".dc-sc{font-size:11px;font-weight:500;color:#555;min-width:20px;text-align:right}"
        + ".dc-sv{font-size:11px;color:#27500A;min-width:60px;text-align:right}"
        + ".dc-sbw{flex:1;min-width:40px;height:4px;border-radius:999px;background:#e2e8f0}"
        + ".dc-sbf{height:100%;border-radius:999px;transition:width 1.1s ease;width:0%}"
        + ".dc-pipe{display:flex;align-items:stretch;margin:12px 0 14px}"
        + ".dc-ps{flex:1;text-align:center}"
        + ".dc-pb{border-radius:10px;padding:13px 6px;transition:transform .15s ease,box-shadow .15s ease;cursor:default}"
        + ".dc-pb:hover{transform:translateY(-3px);box-shadow:0 5px 14px rgba(0,0,0,.09)}"
        + ".dc-pn{font-size:22px;font-weight:500;line-height:1;margin-bottom:2px;font-variant-numeric:tabular-nums}"
        + ".dc-pl{font-size:9px;font-weight:500;text-transform:uppercase;letter-spacing:.05em}"
        + ".dc-pa{width:20px;flex-shrink:0;display:flex;align-items:center;justify-content:center}"
        + ".dc-stc{background:#f8fafc;border-radius:10px;padding:12px 14px;transition:transform .15s ease}"
        + ".dc-stc:hover{transform:translateY(-2px)}"
        + ".dc-stl{font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#94a3b8;margin-bottom:5px}"
        + ".dc-stv{font-size:14px;font-weight:500;color:#111;margin-bottom:2px}"
        + ".dc-sts{font-size:10px;color:#94a3b8;margin-bottom:6px}"
        + ".dc-stb{height:3px;border-radius:999px;background:#e2e8f0}"
        + ".dc-stbf{height:100%;border-radius:999px;transition:width 1.1s ease;width:0%}"
        + ".dc-pw{height:5px;border-radius:999px;background:#e2e8f0}"
        + ".dc-pf{height:100%;border-radius:999px;transition:width 1.2s ease;width:0%}"
        + ".dc-prow{display:flex;justify-content:space-between;margin-top:3px}"
        + ".dc-loading{text-align:center;padding:80px 20px;font-size:14px;color:#94a3b8}"
        + ".dc-empty{text-align:center;padding:60px 20px;font-size:14px;color:#94a3b8;border:0.5px dashed #e2e8f0;border-radius:12px}"
        + "@keyframes _dcIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}"
        + ".dc-kpi:nth-child(1){animation:_dcIn .4s .04s ease both}"
        + ".dc-kpi:nth-child(2){animation:_dcIn .4s .08s ease both}"
        + ".dc-kpi:nth-child(3){animation:_dcIn .4s .12s ease both}"
        + ".dc-kpi:nth-child(4){animation:_dcIn .4s .16s ease both}"
        + ".dc-kpi:nth-child(5){animation:_dcIn .4s .20s ease both}"
        + ".dc-kpi:nth-child(6){animation:_dcIn .4s .24s ease both}"
        + ".dc-card{animation:_dcIn .4s .28s ease both}"
        + ".dc-stc{animation:_dcIn .4s .32s ease both}";
    document.head.appendChild(el);
}


// ================================================================
//  LOAD — fetch data then render
// ================================================================
function _dc_load(page) {
    $(page.main).find(".dcw,.dc-loading,.dc-empty").remove();
    $(page.main).append('<div class="dc-loading">Loading dashboard…</div>');

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Doctor Consultation",
            fields: [
                "name", "patient_name", "mobile_number", "gender",
                "appointment_date", "time", "book_specialist",
                "mode_of_consultation", "payment_status", "doctor_name",
                "meet_generation_status", "g_meet", "creation"
            ],
            limit: 0,
            order_by: "appointment_date desc, creation desc"
        },
        callback: function (r) {
            $(page.main).find(".dc-loading").remove();
            if (!r.message || r.message.length === 0) {
                $(page.main).append(
                    '<div class="dc-empty">No Doctor Consultation records found.</div>'
                );
                return;
            }
            _dc_load_chartjs(function () {
                _dc_build(page, r.message);
            });
        },
        error: function () {
            $(page.main).find(".dc-loading").remove();
            $(page.main).append(
                '<div class="dc-empty">Failed to load data. Please refresh.</div>'
            );
        }
    });
}


// ================================================================
//  CHART.JS — load from CDN once
// ================================================================
function _dc_load_chartjs(cb) {
    if (window.Chart && typeof window.Chart.register === "function") {
        cb();
        return;
    }
    var s = document.createElement("script");
    s.src = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js";
    s.onload = cb;
    s.onerror = function () {
        frappe.show_alert({ message: "Chart.js failed to load from CDN.", indicator: "red" }, 5);
    };
    document.head.appendChild(s);
}


// ================================================================
//  PROCESS — compute all KPIs and groupings from raw records
//
//  Key facts used:
//  - appointment_date stored as YYYY-MM-DD string → safe string compare
//  - time stored as "HH:MM AM/PM - HH:MM AM/PM" range string
//  - mode_of_payment = "Consultation Fee 499" always → RATE = 499
//  - payment_status default = "Pending", updated manually to "Paid"
// ================================================================
function _dc_process(recs) {
    var RATE    = 499;
    var today   = frappe.datetime.get_today();
    var weekEnd = frappe.datetime.add_days(today, 7);

    var total = recs.length;
    var paid = 0;
    var todayCnt = 0;
    var weekCnt  = 0;
    var mOk = 0, mFail = 0, mPend = 0, mQ = 0;

    var uDocs = [];
    var uPats = [];

    // Maps for charts
    var gMap  = {};                         // gender distribution
    var spMap = {};                         // specialist count
    var mMap  = {};                         // month → count (YYYY-MM key)
    var slots = { morning: 0, afternoon: 0, evening: 0, night: 0 };

    // Feed: last 5 records (already sorted desc by appointment_date)
    var feed = [];

    for (var i = 0; i < recs.length; i++) {
        var r = recs[i];

        // appointment_date is YYYY-MM-DD Data field — direct string compare is safe
        var ad = (r.appointment_date || "").toString().substring(0, 10);
        var ms = r.meet_generation_status || "";
        var dn = r.doctor_name || "";
        var pn = r.patient_name || "";

        if (r.payment_status === "Paid") paid++;

        if (ad === today)                 todayCnt++;
        if (ad >= today && ad <= weekEnd) weekCnt++;

        if      (ms === "Success") mOk++;
        else if (ms === "Failed")  mFail++;
        else if (ms === "Pending") mPend++;
        else if (ms === "Queued")  mQ++;

        if (dn && uDocs.indexOf(dn) === -1) uDocs.push(dn);
        if (pn && uPats.indexOf(pn) === -1) uPats.push(pn);

        var gk = r.gender || "Unknown";
        gMap[gk] = (gMap[gk] || 0) + 1;

        var sk = r.book_specialist || "Unknown";
        spMap[sk] = (spMap[sk] || 0) + 1;

        // Month grouping — appointment_date YYYY-MM-DD → take YYYY-MM
        if (ad && ad.length >= 7) {
            var mk = ad.substring(0, 7);
            mMap[mk] = (mMap[mk] || 0) + 1;
        }

        // Time slot — "12:30 PM - 01:00 PM" → parse start time
        slots[_dc_slot(r.time || "")]++;

        if (feed.length < 5) {
            feed.push({
                name:       pn,
                specialist: r.book_specialist || "—",
                date:       ad,
                time:       r.time || "—",
                doctor:     dn,
                ms:         ms || "Pending"
            });
        }
    }

    // Sort specialist map descending by count
    var spList = [];
    for (var k in spMap) {
        if (spMap.hasOwnProperty(k)) spList.push({ name: k, count: spMap[k] });
    }
    spList.sort(function (a, b) { return b.count - a.count; });

    // Sort month keys ascending for trend chart
    var mKeys = [];
    for (var mk2 in mMap) {
        if (mMap.hasOwnProperty(mk2)) mKeys.push(mk2);
    }
    mKeys.sort();

    var tsTotal = slots.morning + slots.afternoon + slots.evening + slots.night;

    // Compute peak slot
    var peakSlot = "Afternoon";
    var peakVal  = slots.afternoon;
    if (slots.morning   > peakVal) { peakSlot = "Morning";   peakVal = slots.morning;   }
    if (slots.evening   > peakVal) { peakSlot = "Evening";   peakVal = slots.evening;   }
    if (slots.night     > peakVal) { peakSlot = "Night";     peakVal = slots.night;     }
    var peakPct = tsTotal > 0 ? Math.round((peakVal / tsTotal) * 100) : 0;

    var topSp    = spList.length > 0 ? spList[0] : { name: "—", count: 0 };
    var topSpPct = total > 0 ? Math.round((topSp.count / total) * 100) : 0;
    var topDoc   = uDocs.length > 0 ? uDocs[0] : "—";
    var mRate    = total > 0 ? Math.round((mOk / total) * 100) : 0;
    var conv     = total > 0 ? Math.round((paid / total) * 100) : 0;

    return {
        total:    total,
        paid:     paid,
        RATE:     RATE,
        paidRev:  paid * RATE,
        pendRev:  (total - paid) * RATE,
        conv:     conv,
        todayCnt: todayCnt,
        weekCnt:  weekCnt,
        mQ:       mQ,
        mOk:      mOk,
        mFail:    mFail,
        mPend:    mPend,
        mRate:    mRate,
        uDocs:    uDocs,
        uPats:    uPats,
        gMap:     gMap,
        spList:   spList,
        mLabels:  mKeys.map(function (k) {
            var d2 = new Date(k + "-01");
            return d2.toLocaleDateString("en-IN", { month: "short", year: "numeric" });
        }),
        mData:    mKeys.map(function (k) { return mMap[k]; }),
        slots:    slots,
        tsTotal:  tsTotal,
        feed:     feed,
        topSp:    topSp,
        topSpPct: topSpPct,
        topDoc:   topDoc,
        peakSlot: peakSlot,
        peakPct:  peakPct
    };
}


// ================================================================
//  TIME SLOT PARSER
//  Input: "12:30 PM - 01:00 PM" or "01:30 PM" etc.
//  Extracts start time, returns slot bucket key
// ================================================================
function _dc_slot(timeStr) {
    if (!timeStr) return "night";
    var start = timeStr.split(" - ")[0].trim();
    var parts = start.split(" ");
    var hm    = (parts[0] || "0:0").split(":");
    var h     = parseInt(hm[0], 10) || 0;
    var ampm  = (parts[1] || "").toUpperCase();
    if (ampm === "PM" && h !== 12) h += 12;
    if (ampm === "AM" && h === 12) h  = 0;
    if (h >=  9 && h < 12) return "morning";
    if (h >= 12 && h < 16) return "afternoon";
    if (h >= 16 && h < 19) return "evening";
    return "night";
}


// ================================================================
//  BUILD — process + render HTML + animate + charts
// ================================================================
function _dc_build(page, recs) {
    var d = _dc_process(recs);

    $(page.main).append(_dc_html(d));

    // Stagger: DOM paint first, then animations, then bars, then charts
    setTimeout(function () { _dc_animate(d); },    120);
    setTimeout(function () { _dc_fill_bars(); },   540);
    setTimeout(function () { _dc_charts(d); },     340);
}


// ================================================================
//  HTML BUILDER
// ================================================================
function _dc_html(d) {
    var INR = function (n) {
        return Math.round(n).toLocaleString("en-IN");
    };
    var H = "";

    // ── Outer wrapper ────────────────────────────────────────────
    H += '<div class="dcw">';

    // ── Top bar ──────────────────────────────────────────────────
    H += '<div class="dc-topbar">'
       + '<div>'
       + '<div class="dc-tb-ttl">Doctor Consultation Dashboard</div>'
       + '<div class="dc-tb-sub">TAALPLUS CHC Private Limited · Healthcare · Live data</div>'
       + '</div>'
       + '<div class="dc-tb-chips">'
       + '<span class="dc-chip dc-chip-g">' + d.total + ' total records</span>'
       + '<span class="dc-chip dc-chip-b">' + d.uDocs.length + ' doctors</span>'
       + '<span class="dc-chip dc-chip-a">' + d.mRate + '% meet rate</span>'
       + '</div></div>';

    // ════════════════════════════════════════════════════════════
    //  SECTION 1 — 6 KPI Number Cards (financial + operational)
    //  All different from the report's 6 cards
    // ════════════════════════════════════════════════════════════
    H += _dc_sechd("Section 1 — Financial & operational KPIs");
    H += '<div class="dc-g3">';

    // Card 1 — Total revenue collected (Paid × ₹499)
    H += _dc_kpi("kg",
        "Total revenue collected",
        "dc-kv1", "₹" + INR(d.paidRev),
        "Paid consultations × ₹" + d.RATE,
        "dc-kf1", "#639922",
        d.paid > 0 ? 100 : 0
    );

    // Card 2 — Pending revenue (Unpaid × ₹499)
    H += _dc_kpi("ka",
        "Pending revenue",
        "dc-kv2", "₹" + INR(d.pendRev),
        "Unpaid × ₹" + d.RATE + " — to collect",
        "dc-kf2", "#BA7517",
        d.total > 0 ? Math.round(((d.total - d.paid) / d.total) * 100) : 0
    );

    // Card 3 — Payment conversion rate
    H += _dc_kpi("kp",
        "Payment conversion rate",
        "dc-kv3", d.conv + "%",
        "Paid ÷ Total consultations",
        "dc-kf3", "#7F77DD",
        d.conv
    );

    // Card 4 — Today's appointments (appointment_date == today YYYY-MM-DD)
    H += _dc_kpi("kb",
        "Today's appointments",
        "dc-kv4", String(d.todayCnt),
        "appointment_date = " + frappe.datetime.get_today(),
        "dc-kf4", "#378ADD",
        d.total > 0 ? Math.round((d.todayCnt / d.total) * 100) : 0
    );

    // Card 5 — This week's appointments
    H += _dc_kpi("kt",
        "This week's appointments",
        "dc-kv5", String(d.weekCnt),
        "Next 7 days including today",
        "dc-kf5", "#1D9E75",
        d.total > 0 ? Math.round((d.weekCnt / d.total) * 100) : 0
    );

    // Card 6 — Meets in queue
    H += _dc_kpi("kc",
        "Meets in queue",
        "dc-kv6", String(d.mQ),
        "meet_generation_status = Queued",
        "dc-kf6", "#D85A30",
        d.total > 0 ? Math.round((d.mQ / d.total) * 100) : 0
    );

    H += '</div>';

    // ════════════════════════════════════════════════════════════
    //  SECTION 2 — Snapshot summary stat cards
    //  Sits immediately below the 6 KPI cards
    // ════════════════════════════════════════════════════════════
    H += _dc_sechd("Section 2 — Snapshot summary");
    H += '<div class="dc-g3b">';

    var tdoc = d.topDoc.length > 22 ? d.topDoc.substring(0, 20) + "…" : d.topDoc;

    H += _dc_stat("Top specialist",
        d.topSp.name,
        d.topSp.count + " consultations · " + d.topSpPct + "%",
        "#D85A30", d.topSpPct
    );
    H += _dc_stat("Top doctor",
        tdoc,
        d.uDocs.length + " unique doctor(s) on record",
        "#1D9E75", 100
    );
    H += _dc_stat("Meet success rate",
        d.mRate + "%",
        d.mOk + " of " + d.total + " meets generated",
        "#639922", d.mRate
    );

    H += '</div>';

    // ════════════════════════════════════════════════════════════
    //  SECTION 3 — 3 doughnut charts
    //  Payment Status · Meet Generation · Gender Distribution
    // ════════════════════════════════════════════════════════════
    H += _dc_sechd("Section 3 — Status distribution charts");
    H += '<div class="dc-g3">';

    var male = d.gMap["Male"] || 0;
    var fem  = d.gMap["Female"] || 0;
    var pnts = d.gMap["Prefer Not to Say"] || 0;

    H += '<div class="dc-card">'
       + '<div class="dc-ct">Payment status</div>'
       + '<div class="dc-cs">Paid vs Pending</div>'
       + _dc_leg([
           { c: "#639922", l: "Paid · " + d.paid },
           { c: "#BA7517", l: "Pending · " + (d.total - d.paid) }
         ])
       + '<div style="position:relative;height:180px">'
       + '<canvas id="dc-ch1" role="img" aria-label="Payment status doughnut chart">'
       + 'Paid: ' + d.paid + ', Pending: ' + (d.total - d.paid)
       + '</canvas></div></div>';

    H += '<div class="dc-card">'
       + '<div class="dc-ct">Meet generation status</div>'
       + '<div class="dc-cs">Success · Failed · Pending · Queued</div>'
       + _dc_leg([
           { c: "#1D9E75", l: "Success · " + d.mOk },
           { c: "#E24B4A", l: "Failed · "  + d.mFail },
           { c: "#BA7517", l: "Pending · " + d.mPend },
           { c: "#378ADD", l: "Queued · "  + d.mQ }
         ])
       + '<div style="position:relative;height:180px">'
       + '<canvas id="dc-ch2" role="img" aria-label="Meet generation status doughnut chart">'
       + 'Success: ' + d.mOk
       + '</canvas></div></div>';

    H += '<div class="dc-card">'
       + '<div class="dc-ct">Gender distribution</div>'
       + '<div class="dc-cs">Male · Female · Prefer not to say</div>'
       + _dc_leg([
           { c: "#378ADD", l: "Male · "   + male },
           { c: "#D4537E", l: "Female · " + fem  },
           { c: "#888780", l: "Other · "  + pnts }
         ])
       + '<div style="position:relative;height:180px">'
       + '<canvas id="dc-ch3" role="img" aria-label="Gender distribution doughnut chart">'
       + 'Male: ' + male + ', Female: ' + fem
       + '</canvas></div></div>';

    H += '</div>';

    // ════════════════════════════════════════════════════════════
    //  SECTION 4 — Specialist bar + Monthly trend line
    // ════════════════════════════════════════════════════════════
    H += _dc_sechd("Section 4 — Volume & trend charts");
    H += '<div class="dc-g2">';

    var barH = Math.max(220, Math.min(d.spList.length, 8) * 40 + 60);
    H += '<div class="dc-card">'
       + '<div class="dc-ct">Consultations by specialist</div>'
       + '<div class="dc-cs">Total bookings per category</div>'
       + '<div style="position:relative;height:' + barH + 'px">'
       + '<canvas id="dc-ch4" role="img" aria-label="Consultations by specialist horizontal bar chart">'
       + 'Specialist data'
       + '</canvas></div></div>';

    H += '<div class="dc-card">'
       + '<div class="dc-ct">Monthly consultation trend</div>'
       + '<div class="dc-cs">Bookings grouped by appointment month</div>'
       + _dc_leg([{ c: "#7F77DD", l: "Bookings per month" }])
       + '<div style="position:relative;height:190px">'
       + '<canvas id="dc-ch5" role="img" aria-label="Monthly consultation trend line chart">'
       + 'Monthly trend data'
       + '</canvas></div></div>';

    H += '</div>';

    // ════════════════════════════════════════════════════════════
    //  SECTION 5 — Recent activity feed + Time slot heatmap
    // ════════════════════════════════════════════════════════════
    H += _dc_sechd("Section 5 — Activity feed & time slot heatmap");
    H += '<div class="dc-g2">';

    // Feed
    var feedColors = ["#378ADD","#D85A30","#7F77DD","#639922","#1D9E75"];
    var feedHTML   = "";
    for (var fi = 0; fi < d.feed.length; fi++) {
        var f   = d.feed[fi];
        var bCls = "dc-bs";
        if (f.ms === "Failed")  bCls = "dc-bf";
        if (f.ms === "Pending") bCls = "dc-bp";
        if (f.ms === "Queued")  bCls = "dc-bq";
        feedHTML += '<div class="dc-frow">'
            + '<span class="dc-fdot" style="background:' + feedColors[fi % feedColors.length] + '"></span>'
            + '<div style="flex:1">'
            + '<div class="dc-fn">' + (f.name || "Unknown") + '</div>'
            + '<div class="dc-fm">' + (f.specialist || "—") + ' · ' + (f.date || "—") + ' · ' + (f.time || "—") + '</div>'
            + '</div>'
            + '<div class="dc-fr">'
            + '<span class="dc-badge ' + bCls + '">' + (f.ms || "Pending") + '</span>'
            + '<span style="font-size:10px;color:#94a3b8">' + (f.doctor || "—") + '</span>'
            + '</div></div>';
    }
    if (!feedHTML) {
        feedHTML = '<div style="font-size:13px;color:#94a3b8;padding:12px 0">No records found.</div>';
    }

    H += '<div class="dc-card">'
       + '<div class="dc-ct">Recent activity feed</div>'
       + '<div class="dc-cs">Last ' + d.feed.length + ' consultations (newest first)</div>'
       + feedHTML
       + '</div>';

    // Heatmap — intensity based on proportion of peak
    var hCfg = {
        high: { bg: "#85B7EB", tc: "#042C53", lc: "#042C53" },
        mid:  { bg: "#B5D4F4", tc: "#0C447C", lc: "#185FA5" },
        low:  { bg: "#E6F1FB", tc: "#0C447C", lc: "#378ADD" }
    };
    function _hi(v) {
        var mx = Math.max(d.slots.morning, d.slots.afternoon, d.slots.evening, d.slots.night) || 1;
        var r2 = v / mx;
        return r2 > 0.75 ? "high" : r2 > 0.35 ? "mid" : "low";
    }
    function _hcell(slot, lbl, range) {
        var cfg = hCfg[_hi(d.slots[slot])];
        return '<div class="dc-hc" style="background:' + cfg.bg + '">'
            + '<div class="dc-ht" style="color:' + cfg.lc + '">' + lbl + '</div>'
            + '<div class="dc-hn" style="color:' + cfg.tc + '">' + d.slots[slot] + '</div>'
            + '<div class="dc-hl" style="color:' + cfg.lc + '">' + range + '</div>'
            + '</div>';
    }

    H += '<div class="dc-card">'
       + '<div class="dc-ct">Appointment time slot heatmap</div>'
       + '<div class="dc-cs">Bookings grouped by time of day (parsed from time field)</div>'
       + '<div class="dc-hg">'
       + _hcell("morning",   "Morning",   "9am–12pm")
       + _hcell("afternoon", "Afternoon", "12–4pm")
       + _hcell("evening",   "Evening",   "4–7pm")
       + _hcell("night",     "Night",     "7–11pm")
       + '</div>'
       + '<div style="border-top:0.5px solid #e2e8f0;padding-top:12px">'
       + '<div style="font-size:11px;font-weight:500;color:#64748b;margin-bottom:6px">'
       + 'Peak slot — ' + d.peakSlot + ' · ' + d.peakPct + '%'
       + '</div>'
       + '<div class="dc-pw">'
       + '<div class="dc-pf" id="dc-peak" style="background:#378ADD" data-w="' + d.peakPct + '"></div>'
       + '</div>'
       + '<div class="dc-prow">'
       + '<span style="font-size:10px;color:#94a3b8">0%</span>'
       + '<span style="font-size:10px;color:#94a3b8">100%</span>'
       + '</div></div></div>';

    H += '</div>';

    // ════════════════════════════════════════════════════════════
    //  SECTION 6 — Specialist revenue table + Meet pipeline
    // ════════════════════════════════════════════════════════════
    H += _dc_sechd("Section 6 — Specialist revenue table & meet pipeline");
    H += '<div class="dc-g2">';

    // Revenue table
    var spColors = ["#D85A30","#378ADD","#7F77DD","#1D9E75","#639922","#888780","#D4537E","#BA7517"];
    var spMax    = d.spList.length > 0 ? d.spList[0].count : 1;
    var spRows   = "";
    for (var si = 0; si < Math.min(d.spList.length, 8); si++) {
        var sp   = d.spList[si];
        var spW  = Math.round((sp.count / spMax) * 100);
        var spRv = sp.count * d.RATE;
        spRows += '<div class="dc-srow">'
            + '<div class="dc-sbw"><div class="dc-sbf" style="background:' + spColors[si % spColors.length] + '" data-w="' + spW + '"></div></div>'
            + '<span class="dc-sn">' + sp.name + '</span>'
            + '<span class="dc-sc">' + sp.count + '</span>'
            + '<span class="dc-sv">₹' + INR(spRv) + '</span>'
            + '</div>';
    }

    H += '<div class="dc-card">'
       + '<div class="dc-ct">Specialist revenue table</div>'
       + '<div class="dc-cs">Estimated revenue = bookings × ₹' + d.RATE + '</div>'
       + '<div style="display:flex;gap:8px;padding:5px 0;border-bottom:0.5px solid #e2e8f0;margin-bottom:2px">'
       + '<div style="flex:1;min-width:40px"></div>'
       + '<span style="font-size:10px;font-weight:500;color:#94a3b8;flex:1;min-width:0">Specialist</span>'
       + '<span style="font-size:10px;font-weight:500;color:#94a3b8;min-width:26px;text-align:right">Cnt</span>'
       + '<span style="font-size:10px;font-weight:500;color:#94a3b8;min-width:65px;text-align:right">Est. Revenue</span>'
       + '</div>'
       + spRows
       + '<div style="border-top:0.5px solid #e2e8f0;margin-top:8px;padding-top:8px;'
       + 'display:flex;justify-content:space-between;align-items:center">'
       + '<span style="font-size:11px;font-weight:500;color:#64748b">Total estimated revenue</span>'
       + '<span style="font-size:14px;font-weight:500;color:#27500A">₹' + INR(d.total * d.RATE) + '</span>'
       + '</div></div>';

    // Meet pipeline — Total → Pending → Queued → Success ↓ Failed
    H += '<div class="dc-card">'
       + '<div class="dc-ct">Meet generation pipeline</div>'
       + '<div class="dc-cs">Status flow from submission to outcome</div>'
       + '<div class="dc-pipe">'
       + _dc_pipe_stage("#E6F1FB","#0C447C","#185FA5","dc-pp1", String(d.total),  "Total")
       + _dc_pipe_arrow(false)
       + _dc_pipe_stage("#FAEEDA","#633806","#854F0B","dc-pp2", String(d.mPend),  "Pending")
       + _dc_pipe_arrow(false)
       + _dc_pipe_stage("#E6F1FB","#0C447C","#185FA5","dc-pp3", String(d.mQ),     "Queued")
       + _dc_pipe_arrow(false)
       + _dc_pipe_stage("#EAF3DE","#27500A","#3B6D11","dc-pp4", String(d.mOk),    "Success")
       + _dc_pipe_arrow(true)
       + _dc_pipe_stage("#FCEBEB","#791F1F","#A32D2D","dc-pp5", String(d.mFail),  "Failed")
       + '</div>'
       + '<div style="background:#f8fafc;border-radius:8px;padding:10px 12px">'
       + '<div style="font-size:11px;font-weight:500;color:#64748b;margin-bottom:5px">Meet success rate</div>'
       + '<div class="dc-pw"><div class="dc-pf" id="dc-pipebar" style="background:#639922" data-w="' + d.mRate + '"></div></div>'
       + '<div class="dc-prow">'
       + '<span style="font-size:10px;color:#94a3b8">0%</span>'
       + '<span style="font-size:13px;font-weight:500;color:#27500A">' + d.mRate + '%</span>'
       + '<span style="font-size:10px;color:#94a3b8">100%</span>'
       + '</div></div></div>';

    H += '</div>';

    H += '</div>'; // close dcw

    return H;
}


// ================================================================
//  HTML COMPONENT HELPERS
// ================================================================
function _dc_sechd(lbl) {
    return '<div class="dc-sechd">'
        + '<span class="dc-seclbl">' + lbl + '</span>'
        + '<div class="dc-secline"></div>'
        + '</div>';
}

function _dc_kpi(cls, lbl, valId, val, sub, fillId, fillColor, fillPct) {
    return '<div class="dc-kpi ' + cls + '">'
        + '<div class="dc-kl">' + lbl + '</div>'
        + '<div class="dc-kv" id="' + valId + '">' + val + '</div>'
        + '<div class="dc-ks">' + sub + '</div>'
        + '<div class="dc-kb"><div class="dc-kbf" id="' + fillId + '" style="background:' + fillColor + '" data-w="' + fillPct + '"></div></div>'
        + '</div>';
}

function _dc_leg(items) {
    var h = '<div class="dc-leg">';
    for (var i = 0; i < items.length; i++) {
        h += '<span class="dc-li"><span class="dc-lsq" style="background:' + items[i].c + '"></span>' + items[i].l + '</span>';
    }
    return h + '</div>';
}

function _dc_pipe_stage(bg, nc, lc, id, val, lbl) {
    return '<div class="dc-ps">'
        + '<div class="dc-pb" style="background:' + bg + '">'
        + '<div class="dc-pn" style="color:' + nc + '" id="' + id + '">' + val + '</div>'
        + '<div class="dc-pl" style="color:' + lc + '">' + lbl + '</div>'
        + '</div></div>';
}

function _dc_pipe_arrow(down) {
    if (down) {
        return '<div class="dc-pa">'
            + '<svg width="16" height="16" viewBox="0 0 16 16" fill="none">'
            + '<path d="M8 4v8M5 9l3 3 3-3" stroke="#E24B4A" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>'
            + '</svg></div>';
    }
    return '<div class="dc-pa">'
        + '<svg width="16" height="16" viewBox="0 0 16 16" fill="none">'
        + '<path d="M4 8h8M9 5l3 3-3 3" stroke="#cbd5e1" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>'
        + '</svg></div>';
}

function _dc_stat(lbl, val, sub, color, pct) {
    return '<div class="dc-stc">'
        + '<div class="dc-stl">' + lbl + '</div>'
        + '<div class="dc-stv">' + val + '</div>'
        + '<div class="dc-sts">' + sub + '</div>'
        + '<div class="dc-stb"><div class="dc-stbf" style="background:' + color + '" data-w="' + pct + '"></div></div>'
        + '</div>';
}


// ================================================================
//  ANIMATIONS — count-up for KPI values + pipeline numbers
// ================================================================
function _dc_animate(d) {
    var INR = function (n) {
        return Math.round(n).toLocaleString("en-IN");
    };

    function cu(id, target, pre, suf) {
        var el = document.getElementById(id);
        if (!el) return;
        var s    = 0;
        var step = Math.max(1, Math.ceil(target / 25));
        var t    = setInterval(function () {
            s += step;
            if (s >= target) {
                el.textContent = (pre || "") + INR(target) + (suf || "");
                clearInterval(t);
            } else {
                el.textContent = (pre || "") + INR(s) + (suf || "");
            }
        }, 28);
    }

    // KPI cards
    cu("dc-kv1", d.paidRev,  "₹", "");
    cu("dc-kv2", d.pendRev,  "₹", "");
    cu("dc-kv3", d.conv,     "",  "%");
    cu("dc-kv4", d.todayCnt, "",  "");
    cu("dc-kv5", d.weekCnt,  "",  "");
    cu("dc-kv6", d.mQ,       "",  "");

    // Pipeline stages
    cu("dc-pp1", d.total,  "", "");
    cu("dc-pp2", d.mPend,  "", "");
    cu("dc-pp3", d.mQ,     "", "");
    cu("dc-pp4", d.mOk,    "", "");
    cu("dc-pp5", d.mFail,  "", "");
}


// ================================================================
//  FILL BARS — animates all [data-w] progress bars
// ================================================================
function _dc_fill_bars() {
    document.querySelectorAll("[data-w]").forEach(function (el) {
        el.style.width = (el.getAttribute("data-w") || 0) + "%";
    });
}


// ================================================================
//  CHARTS — Chart.js 4.4.1
// ================================================================
function _dc_charts(d) {
    var dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    var gc   = dark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.06)";
    var lc   = dark ? "#94a3b8" : "#888780";
    var bdr  = dark ? "#1a1a1a" : "#ffffff";

    // Shared doughnut options
    var dOpts = {
        responsive:         true,
        maintainAspectRatio: false,
        cutout:             "65%",
        animation:          { animateRotate: true, duration: 800 },
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

    // Chart 1 — Payment status
    var c1 = document.getElementById("dc-ch1");
    if (c1) {
        new Chart(c1, {
            type: "doughnut",
            data: {
                labels: ["Paid", "Pending"],
                datasets: [{
                    data:            [d.paid, d.total - d.paid],
                    backgroundColor: ["#639922", "#BA7517"],
                    borderWidth:     3,
                    borderColor:     bdr,
                    hoverOffset:     8
                }]
            },
            options: dOpts
        });
    }

    // Chart 2 — Meet generation status
    var c2 = document.getElementById("dc-ch2");
    if (c2) {
        new Chart(c2, {
            type: "doughnut",
            data: {
                labels: ["Success", "Failed", "Pending", "Queued"],
                datasets: [{
                    data:            [d.mOk, d.mFail, d.mPend, d.mQ],
                    backgroundColor: ["#1D9E75", "#E24B4A", "#BA7517", "#378ADD"],
                    borderWidth:     3,
                    borderColor:     bdr,
                    hoverOffset:     8
                }]
            },
            options: dOpts
        });
    }

    // Chart 3 — Gender distribution
    var c3 = document.getElementById("dc-ch3");
    if (c3) {
        var male = d.gMap["Male"] || 0;
        var fem  = d.gMap["Female"] || 0;
        var pnts = d.gMap["Prefer Not to Say"] || 0;
        new Chart(c3, {
            type: "doughnut",
            data: {
                labels: ["Male", "Female", "Prefer not to say"],
                datasets: [{
                    data:            [male, fem, pnts],
                    backgroundColor: ["#378ADD", "#D4537E", "#888780"],
                    borderWidth:     3,
                    borderColor:     bdr,
                    hoverOffset:     8
                }]
            },
            options: dOpts
        });
    }

    // Chart 4 — Specialist horizontal bar (per-bar color)
    var c4 = document.getElementById("dc-ch4");
    if (c4) {
        var spColors  = ["#D85A30","#378ADD","#7F77DD","#1D9E75","#639922","#888780","#D4537E","#BA7517"];
        var spLabels  = d.spList.slice(0, 8).map(function (s) { return s.name; });
        var spData    = d.spList.slice(0, 8).map(function (s) { return s.count; });
        var spBg      = spLabels.map(function (_, i) { return spColors[i % spColors.length]; });

        new Chart(c4, {
            type: "bar",
            data: {
                labels: spLabels,
                datasets: [{
                    label:           "Consultations",
                    data:            spData,
                    backgroundColor: spBg,
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
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return " " + ctx.parsed.x + " consultations";
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks:  { color: lc, font: { size: 11 }, stepSize: 1 },
                        grid:   { color: gc },
                        border: { display: false }
                    },
                    y: {
                        ticks:  { color: lc, font: { size: 11 } },
                        grid:   { display: false },
                        border: { display: false }
                    }
                }
            }
        });
    }

    // Chart 5 — Monthly trend line with filled area
    var c5 = document.getElementById("dc-ch5");
    if (c5) {
        new Chart(c5, {
            type: "line",
            data: {
                labels: d.mLabels.length > 0 ? d.mLabels : ["No data"],
                datasets: [{
                    label:              "Consultations",
                    data:               d.mData.length > 0 ? d.mData : [0],
                    borderColor:        "#7F77DD",
                    backgroundColor:    dark
                                        ? "rgba(127,119,221,0.12)"
                                        : "rgba(127,119,221,0.08)",
                    borderWidth:        2,
                    pointBackgroundColor: "#7F77DD",
                    pointBorderColor:   bdr,
                    pointBorderWidth:   2,
                    pointRadius:        5,
                    pointHoverRadius:   7,
                    tension:            0.4,
                    fill:               true
                }]
            },
            options: {
                responsive:          true,
                maintainAspectRatio: false,
                animation:           { duration: 900 },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return " " + ctx.parsed.y + " consultations";
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks:  {
                            color:       lc,
                            font:        { size: 11 },
                            autoSkip:    false,
                            maxRotation: 30
                        },
                        grid:   { color: gc },
                        border: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        ticks:  { color: lc, font: { size: 11 }, stepSize: 1 },
                        grid:   { color: gc },
                        border: { display: false }
                    }
                }
            }
        });
    }
}