"""Saifuro Product Suite: strategy and operational playbook, presented as a dashboard.

Independent portfolio piece by Anirban Majumder. Not affiliated with or endorsed by any company.
All ledger events, figures and examples are illustrative. Run with:  streamlit run app.py
"""
import hashlib

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Saifuro Product Suite Playbook", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=DM+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif !important; letter-spacing:-0.02em;}
.block-container {padding-top:1.6rem; max-width:1150px;}
.hero {background:linear-gradient(135deg,#0B1B3A 0%,#12356B 55%,#0E7C86 100%); border-radius:20px; padding:42px 44px; color:#fff; margin-bottom:26px;}
.hero .eyebrow {font-size:12px; letter-spacing:.16em; text-transform:uppercase; color:#8FD3D8; margin-bottom:10px;}
.hero h1 {color:#fff; font-size:44px; margin:0 0 10px 0; line-height:1.05;}
.hero p {color:#CFE3EE; font-size:17px; max-width:760px; margin:0 0 18px 0;}
.pill {display:inline-block; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.22); color:#fff; padding:5px 13px; border-radius:999px; font-size:13px; margin:0 8px 8px 0;}
.card {border:1px solid rgba(128,138,160,.28); border-radius:16px; padding:20px 22px; height:100%; background:rgba(128,138,160,.07);}
.card h4 {font-family:'Space Grotesk',sans-serif; margin:0 0 6px 0; font-size:18px;}
.card .tag {font-size:11px; letter-spacing:.12em; text-transform:uppercase; color:#0E7C86; font-weight:600; margin-bottom:6px;}
.card p {margin:0; font-size:14.5px; line-height:1.55; opacity:.92;}
.big {font-family:'Space Grotesk',sans-serif; font-size:54px; font-weight:700; line-height:1; letter-spacing:-.03em;}
.bigsub {font-size:14px; opacity:.75; margin-top:6px;}
.blocked {display:inline-block; background:#FDE3E1; color:#B42318; font-weight:700; font-size:12px; padding:3px 10px; border-radius:999px;}
.step {border-left:3px solid #0E7C86; padding:4px 0 4px 16px; margin-bottom:16px;}
.step b {font-family:'Space Grotesk',sans-serif; font-size:16px;}
.kpi {border:1px solid rgba(128,138,160,.28); border-radius:16px; padding:16px 20px; background:rgba(128,138,160,.07);}
.foot {font-size:12px; opacity:.6; margin-top:30px;}
</style>
""", unsafe_allow_html=True)


def card(title, body, tag=""):
    t = f'<div class="tag">{tag}</div>' if tag else ""
    return f'<div class="card">{t}<h4>{title}</h4><p>{body}</p></div>'


def row(cards):
    cols = st.columns(len(cards))
    for c, html in zip(cols, cards):
        c.markdown(html, unsafe_allow_html=True)


st.markdown("""
<div class="hero">
  <div class="eyebrow">Product strategy and operational playbook</div>
  <h1>Saifuro Product Suite</h1>
  <p>How a machine-to-machine payments validation layer keeps autonomous agents inside human-approved spending rules, and how product, support and finance fit around it.</p>
  <span class="pill">Payments validation</span><span class="pill">Onchain settlement</span><span class="pill">x402 protocol alignment</span>
  <span class="pill">Multi-persona customer happiness</span><span class="pill">Automated reconciliation</span>
  <div style="margin-top:14px;font-size:14px;color:#9FC3D6">Author: Anirban Majumder</div>
</div>
""", unsafe_allow_html=True)


GREEN, RED, GREY, NAVY = "#0E7C86", "#D92D20", "#98A2B3", "#12356B"
APPROVED = ["Alchemy_LLM_Router", "OpenAI_Context_Refuel", "Data_Feed_A", "Compute_Pool_B"]
ALL_DEST = APPROVED + ["Unknown_Vendor_X"]


@st.cache_data
def make_events(seed=21, n=2500):
    rng = np.random.default_rng(seed)
    agents = [f"0x{rng.integers(16**4):04x}...{rng.integers(16**4):04x}" for _ in range(8)]
    t = pd.Timestamp("2026-09-21") + pd.to_timedelta(np.sort(rng.uniform(0, 30 * 86400, n)), unit="s")
    d = pd.DataFrame({"ts": t, "agent": rng.choice(agents, n), "chain": rng.choice(["Base", "Solana"], n, p=[.6, .4]),
                      "dest": rng.choice(ALL_DEST, n, p=[.35, .25, .17, .17, .06]), "usdc": np.round(rng.lognormal(2.2, 0.9, n), 2)})
    for b in rng.choice(n - 10, 25, replace=False):
        d.loc[b:b + 9, "agent"] = d.loc[b, "agent"]
        d.loc[b:b + 9, "ts"] = d.loc[b, "ts"] + pd.to_timedelta(np.arange(10) * 0.2, unit="s")
    return d.sort_values("ts").reset_index(drop=True)


def judge(d, max_tx, vel, scope):
    parts = []
    for _, g in d.groupby("agent"):
        g = g.sort_values("ts").copy()
        g["cps"] = g.set_index("ts")["usdc"].rolling("1s").count().values
        parts.append(g)
    d = pd.concat(parts).sort_values("ts")
    d["verdict"], d["exception"] = "ALLOWED", "None"
    for mask, label in [(d.cps > vel, "Velocity violation"), (~d.dest.isin(scope), "Out of approved scope"), (d.usdc > max_tx, "Mandate exceeded")]:
        d.loc[mask, ["verdict", "exception"]] = ["BLOCKED", label]
    d["proof"] = ["0x" + hashlib.sha256(f"{r.ts}|{r.agent}|{r.usdc}|{r.verdict}".encode()).hexdigest() for r in d.itertuples()]
    return d.reset_index(drop=True)


def gauge(value, title, target_text, rng, color):
    f = go.Figure(go.Indicator(mode="gauge+number", value=value, title={"text": title, "font": {"size": 15}},
                               gauge={"axis": {"range": rng}, "bar": {"color": color}}))
    f.update_layout(height=230, margin=dict(l=20, r=20, t=50, b=10))
    return f


PAGES = ["Overview", "Mandate lab", "Live interceptions", "Developer discovery", "Escrow command center", "Month-end close engine", "KPIs and scope"]
page = st.sidebar.radio("Explore the playbook", PAGES)
st.sidebar.caption("Unofficial portfolio piece. Illustrative data only.")

if page == "Overview":
    c = st.columns(3)
    for col, big, sub in zip(c, ["48h to 5min", "3 personas", "0.00%"], ["Target time to close monthly agent accounting", "Developer, seller and finance team", "Target discrepancy between logs, exports and onchain events"]):
        col.markdown(f'<div class="card"><div class="big">{big}</div><div class="bigsub">{sub}</div></div>', unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([3, 2])
    with left:
        st.subheader("From manual reconciliation to one click")
        st.write("Corporate accounting cannot keep up with sub-second machine-to-machine micro-transactions. Saifuro turns cryptographic assertions into explicit guardrails, so enterprises can let agents spend without losing control.")
        hrs = st.slider("Manual close hours per month", min_value=48, max_value=72, value=48)
        saved = 100 * (1 - (5 / 60) / hrs)
        st.metric("Time saved by automating the close", f"{saved:.1f}%", f"{hrs} hours to under 5 minutes")
    with right:
        f = go.Figure(go.Scatterpolar(r=[5, 5, 4, 4, 5], theta=["Control", "Transparency", "Speed", "Auditability", "Safety"], fill="toself", line_color=GREEN))
        f.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 5])), showlegend=False, height=300, margin=dict(t=30, b=20), title="Design goals (illustrative)")
        st.plotly_chart(f, use_container_width=True)

elif page == "Mandate lab":
    st.subheader("Set the corporate mandate, watch the guard respond")
    s = st.columns(4)
    max_tx = s[0].slider("Max Tx limit (USDC)", min_value=10, max_value=200, value=50, step=5)
    vel = s[1].slider("Velocity: calls per second", min_value=1, max_value=10, value=3)
    scope = s[2].multiselect("Approved scope", ALL_DEST, default=APPROVED)
    chains = s[3].multiselect("Settlement chain", ["Base", "Solana"], default=["Base", "Solana"])
    ev = judge(make_events(), max_tx, vel, scope)
    ev = ev[ev.chain.isin(chains)]
    k = st.columns(4)
    k[0].metric("Requests", f"{len(ev):,}")
    k[1].metric("Allowed", f"{(ev.verdict == 'ALLOWED').mean():.1%}")
    k[2].metric("Blocked", f"{(ev.verdict == 'BLOCKED').sum():,}")
    k[3].metric("USDC protected", f"{ev.loc[ev.verdict == 'BLOCKED', 'usdc'].sum():,.0f}")
    a, b = st.columns([3, 2])
    with a:
        f = go.Figure()
        for v, col in [("ALLOWED", GREY), ("BLOCKED", RED)]:
            x = ev[ev.verdict == v]
            f.add_trace(go.Scatter(x=x.ts, y=x.usdc, mode="markers", name=v, marker=dict(color=col, size=5 if v == "ALLOWED" else 8, opacity=.5 if v == "ALLOWED" else .9)))
        f.add_hline(y=max_tx, line_dash="dash", line_color=GREEN, annotation_text=f"Max Tx {max_tx} USDC")
        f.update_layout(height=360, title="Every request, by value and verdict", yaxis_title="USDC", margin=dict(t=50, b=10))
        st.plotly_chart(f, use_container_width=True)
    with b:
        ex = ev[ev.verdict == "BLOCKED"].exception.value_counts()
        f = go.Figure(go.Pie(labels=list(ex.index), values=list(ex.values), hole=.55, marker_colors=[RED, "#F79009", NAVY]))
        f.update_layout(height=360, title="Why requests were blocked", margin=dict(t=50, b=10))
        st.plotly_chart(f, use_container_width=True)
    st.markdown("**Test a single payment**")
    t = st.columns(3)
    amt = t[0].number_input("Value (USDC)", min_value=0.0, max_value=500.0, value=75.0)
    dest = t[1].selectbox("Destination", ALL_DEST)
    cps = t[2].number_input("Calls in the last second", min_value=1, max_value=30, value=1)
    why = [m for ok, m in [(cps > vel, f"Velocity violation ({cps} calls/sec against {vel})"), (dest not in scope, "Out of approved scope"), (amt > max_tx, f"Mandate exceeded ({amt:.2f} against {max_tx:.2f} USDC)")] if ok]
    (st.error("BLOCKED. " + "; ".join(why) + ". Payload discarded, no network transaction processed.") if why else st.success("ALLOWED. Within every limit."))

elif page == "Live interceptions":
    st.subheader("Production ledger sample: real-time interceptions")
    EV = [("TX-9041", "2026-10-21 14:02:11", "Alchemy_LLM_Router", "5.00", "Velocity Violation", "12 calls/sec detected against a maximum rule of 3 calls/sec.", "System auto-throttled. Payload discarded. Alert sent to developer log.", 12, 3, "calls per second"),
          ("TX-9042", "2026-10-21 14:05:00", "OpenAI_Context_Refuel", "75.00", "Mandate Exceeded", "Value request surpasses the 50.00 USDC single-call limit.", "Transaction frozen. Signed override request sent to the Financial Controller.", 75, 50, "USDC")]
    for eid, ts, dest, val, exc, detail, action, obs, lim, unit in EV:
        a, b = st.columns([3, 2])
        a.markdown(f'<div class="card"><div class="tag">{eid} · {ts} UTC</div><h4>{dest} · {val} USDC &nbsp;<span class="blocked">BLOCKED</span></h4><p><b>{exc}.</b> {detail}<br><br><b>Next step:</b> {action}<br><span style="opacity:.6">Agent 0x7a8b...321f</span></p></div>', unsafe_allow_html=True)
        f = go.Figure(go.Bar(x=[obs, lim], y=["Observed", "Rule limit"], orientation="h", marker_color=[RED, GREEN], text=[obs, lim], textposition="outside"))
        f.update_layout(height=170, margin=dict(l=0, r=30, t=10, b=0), xaxis_title=unit, xaxis_range=[0, max(obs, lim) * 1.25], showlegend=False)
        b.plotly_chart(f, use_container_width=True)
        st.write("")

elif page == "Developer discovery":
    st.subheader("Weekly developer discovery loops")
    st.write("Pick a loop, capture what you hear, and score the friction. Scores are yours to enter and stay on this page only.")
    LOOPS = {
        "Sandbox friction": ("Walk me through the exact moment your team initialized the local self-serve sandbox. At what point did the console output confuse you, and did the error logs clearly explain why an experimental transaction tripped a policy cap?", "Check that local setup matches onboarding expectations, to reduce integration drop-off."),
        "Execution latency": ("Because the validation engine runs synchronous policy checks against human mandates before producing a signed verdict, what execution lag are your agents seeing during peak traffic?", "Keep latency low enough to remain the preferred validation layer for high-speed agent networks."),
        "Escrow fallback confidence": ("Your workloads use our onchain Base escrow for counterparty settlement. If a counterparty agent hits an uncaught exception mid-trade, how comfortable is your operations team with the fallback timeout mechanics?", "Refine contract conditions to ease developer worry about temporary block-level locks."),
        "Diagnostic logging": ("When a deployment script fails a validation check, which missing diagnostic data would most reduce your engineering team's triage time?", "Move from generic errors to contextual insight, lowering support ticket volume."),
    }
    scores = {}
    tabs = st.tabs(list(LOOPS))
    for t, (name, (q, goal)) in zip(tabs, LOOPS.items()):
        with t:
            row([card("PM question", q, "Ask"), card("Product goal", goal, "Why")])
            scores[name] = st.slider(f"Friction heard in this loop: {name}", min_value=0, max_value=10, value=5)
    f = go.Figure(go.Bar(x=list(scores.values()), y=list(scores), orientation="h", marker_color=NAVY))
    f.update_layout(height=260, title="Friction scorecard (your inputs)", xaxis_range=[0, 10], margin=dict(t=50, b=10))
    st.plotly_chart(f, use_container_width=True)

elif page == "Escrow command center":
    st.subheader("Escrow stall: customer-safe resolution")
    c = st.columns(4)
    amount = c[0].number_input("Locked amount (USDC)", min_value=100, max_value=100000, value=2500)
    left = c[1].slider("Minutes left in timeout", min_value=0, max_value=30, value=11)
    revived = c[2].checkbox("Counterparty revived and completed", value=False)
    name = c[3].text_input("Developer name", value="Alex")
    state = "SETTLED" if revived else ("REFUND AVAILABLE" if left == 0 else "LOCKED, timeout running")
    a, b = st.columns([2, 3])
    with a:
        st.plotly_chart(gauge(left, "Minutes until fallback opens", "", [0, 30], GREEN if not revived else GREY), use_container_width=True)
        st.metric("Escrow state", state)
        for title, body in [("System isolation", "The counterparty agent exited with a non-zero code, so the escrow contract engaged its safety lock."),
                            ("Asset security", f"The {amount:,} USDC stays in the non-custodial contract, locked only by onchain logic."),
                            ("Path to resolution", "If the counterparty does not complete in time, the fallback opens and the mandate can issue a clean refund.")]:
            st.markdown(f'<div class="step"><b>{title}</b><br>{body}</div>', unsafe_allow_html=True)
    with b:
        st.text_area("Outbound message (updates live)", height=380, value=(
            f"Subject: URGENT: Settlement Loop Triage - Escrow Reference #BASE-ESC-9982\n\nHi {name},\n\n"
            f"Your automated procurement loop is paused at the block layer on Base because a counterparty agent failed. I understand how critical this {amount:,} USDC settlement is for your pipeline.\n\n"
            f"1. System isolation: the escrow contract engaged its safety lock to protect your capital.\n"
            f"2. Asset security: your {amount:,} USDC is secure in the non-custodial contract. Funds are locked strictly by immutable smart contract logic onchain.\n"
            f"3. Path to resolution: current status is {state}. "
            + ("The transaction has completed normally." if revived else f"If the counterparty does not complete within {left} minutes, the fallback opens automatically and your mandate can issue a clean refund.")
            + "\n\nWe have opened a direct channel with our engineers: [War-Room Link]. We have your back.\n\nBest regards,\nAnirban Majumder\nProduct Manager"))

elif page == "Month-end close engine":
    st.subheader("Automated month-end close and reconciliation")
    nodes = ["Base logs", "Solana logs", "Aggregation layer", "Mandate validation", "Proof matrix", "CSV / XLSX export", "Developer API", "Seller view", "Finance team"]
    links = [(0, 2, 6), (1, 2, 4), (2, 3, 10), (3, 4, 10), (4, 5, 10), (5, 6, 3), (5, 7, 3), (5, 8, 4)]
    f = go.Figure(go.Sankey(node=dict(label=nodes, pad=18, thickness=16, color=[NAVY, NAVY, GREEN, GREEN, GREEN, GREEN, GREY, GREY, GREY]),
                            link=dict(source=[l[0] for l in links], target=[l[1] for l in links], value=[l[2] for l in links])))
    f.update_layout(height=340, title="The pipeline (illustrative flow)", margin=dict(t=50, b=10))
    st.plotly_chart(f, use_container_width=True)
    led = judge(make_events(), 50, 3, APPROVED)
    led = led[led.verdict == "ALLOWED"].copy()
    inject = st.checkbox("Inject a one-cent mismatch to see detection", value=False)
    led["onchain"] = led.usdc
    if inject:
        led.loc[led.index[len(led) // 2], "onchain"] += 0.01
    led["match"] = (led.usdc - led.onchain).abs() < 1e-9
    m = st.columns(3)
    m[0].metric("Line items", f"{len(led):,}")
    m[1].metric("Data parity", f"{led.match.mean():.2%}")
    m[2].metric("Discrepancies", int((~led.match).sum()))
    p1, p2, p3 = st.columns(3)
    p1.markdown(card("Developer", "GET /v1/reconciliation/export returns pre-reconciled records, so no custom tracking scripts.", "Integrating agents"), unsafe_allow_html=True)
    p2.markdown(card("Seller", "Usage and fees grouped by client API key, ending billing discrepancies and chargeback disputes.", "Selling APIs to agents"), unsafe_allow_html=True)
    p3.markdown(card("Finance team", "One spreadsheet for QuickBooks or NetSuite, each line linked to its onchain verification hash.", "Compliance"), unsafe_allow_html=True)
    st.write("")
    st.download_button("Download reconciled export (CSV, demo hashes)", led[["ts", "agent", "chain", "dest", "usdc", "onchain", "match", "proof"]].to_csv(index=False), "reconciliation_export.csv", "text/csv")
    st.caption("Proof values are demo SHA-256 hashes, not real signed verdicts or onchain transaction hashes.")

else:
    st.subheader("Success metrics and engineering scope")
    g = st.columns(3)
    g[0].plotly_chart(gauge(5, "Close time target (minutes, from 2,880)", "", [0, 60], GREEN), use_container_width=True)
    g[1].plotly_chart(gauge(80, "Sandboxes with a mock report in 14 days (target %)", "", [0, 100], NAVY), use_container_width=True)
    g[2].plotly_chart(gauge(0.0, "Data discrepancy rate (target %)", "", [0, 1], RED), use_container_width=True)
    row([card("Reconciliation friction velocity", "Cut monthly close from 48 hours to under 5 minutes.", "Primary metric"),
         card("Sandbox onboarding engagement", "More than 80% of testing sandboxes produce a mock month-end report within 14 days.", "Adoption"),
         card("Data parity accuracy", "0.00% discrepancy between local logs, exports and onchain events across Base and Solana.", "Guardrail")])
    st.write("")
    st.markdown("**Engineering scope for the next sprint**")
    row([card("Data aggregation layer", "Scrape internal event logs by Agent_Wallet_ID and cache locally to avoid public RPC rate limits.", "Build"),
         card("Cryptographic proof matrix", "Bundle each line with a V2 signed verdict signature so auditors trace validity without block explorers.", "Build"),
         card("Export pipeline", "A streaming CSV/XLSX worker for more than 100,000 transaction objects without timeouts or memory exhaustion.", "Build")])

st.markdown('<div class="foot">Independent portfolio piece by Anirban Majumder. Illustrative data, not affiliated with or endorsed by any company.</div>', unsafe_allow_html=True)
