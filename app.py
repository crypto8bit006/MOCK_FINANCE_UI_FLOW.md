"""Saifuro Product Suite: an interactive portfolio mock.

Independent, unofficial product-management portfolio piece. Not affiliated with or endorsed by any company.
All data is generated in memory with a fixed seed and represents no real wallet, customer or transaction.
Run with:  streamlit run app.py
"""
import hashlib

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Saifuro Product Suite", layout="wide")

APPROVED = ["Alchemy_LLM_Router", "OpenAI_Context_Refuel", "Data_Feed_A", "Compute_Pool_B"]
ALL_DEST = APPROVED + ["Unknown_Vendor_X"]

# ---------------- sidebar: the corporate mandate ----------------
st.sidebar.header("Corporate mandate")
chain_sel = st.sidebar.multiselect("Settlement chain", ["Base", "Solana"], default=["Base", "Solana"])
scope = st.sidebar.multiselect("Approved scope (vendors)", ALL_DEST, default=APPROVED)
max_tx = st.sidebar.slider("Max Tx limit (USDC)", min_value=10, max_value=200, value=50, step=5)
vel = st.sidebar.slider("Velocity window: max calls per second", min_value=1, max_value=10, value=3)
st.sidebar.caption("Synthetic data. Unofficial portfolio mock.")


@st.cache_data
def make_events(seed=21, n=3000):
    rng = np.random.default_rng(seed)
    agents = [f"0x{rng.integers(16**4):04x}...{rng.integers(16**4):04x}" for _ in range(8)]
    t = pd.Timestamp("2026-09-21") + pd.to_timedelta(np.sort(rng.uniform(0, 30 * 86400, n)), unit="s")
    d = pd.DataFrame({"ts": t, "agent": rng.choice(agents, n), "chain": rng.choice(["Base", "Solana"], n, p=[.6, .4]),
                      "dest": rng.choice(ALL_DEST, n, p=[.35, .25, .17, .17, .06]),
                      "usdc": np.round(rng.lognormal(2.2, 0.9, n), 2)})
    for b in rng.choice(n - 10, 30, replace=False):  # runaway-loop bursts
        d.loc[b:b + 9, "agent"] = d.loc[b, "agent"]
        d.loc[b:b + 9, "ts"] = d.loc[b, "ts"] + pd.to_timedelta(np.arange(10) * 0.2, unit="s")
    return d.sort_values("ts").reset_index(drop=True)


def verdict(d, max_tx, vel, scope):
    d = d.copy()
    d["calls_1s"] = 0
    parts = []
    for _, g in d.groupby("agent"):
        g = g.sort_values("ts").copy()
        g["calls_1s"] = g.set_index("ts")["usdc"].rolling("1s").count().values
        parts.append(g)
    d = pd.concat(parts).sort_values("ts")
    d["verdict"], d["exception"] = "ALLOWED", ""
    m = d.calls_1s > vel
    d.loc[m, ["verdict", "exception"]] = ["BLOCKED", "Velocity violation"]
    m = ~d.dest.isin(scope)
    d.loc[m, ["verdict", "exception"]] = ["BLOCKED", "Out of approved scope"]
    m = d.usdc > max_tx
    d.loc[m, ["verdict", "exception"]] = ["BLOCKED", "Mandate exceeded"]
    d["proof"] = ["0x" + hashlib.sha256(f"{r.ts}|{r.agent}|{r.usdc}|{r.verdict}".encode()).hexdigest() for r in d.itertuples()]
    return d.reset_index(drop=True)


ev = verdict(make_events(), max_tx, vel, scope)
ev = ev[ev.chain.isin(chain_sel)]

st.title("Saifuro Product Suite")
st.caption("Machine-to-machine payments validation: every agent payment is checked against a human-approved mandate before it settles.")
k = st.columns(4)
k[0].metric("Payment requests", f"{len(ev):,}")
k[1].metric("Allowed", f"{(ev.verdict == 'ALLOWED').mean():.1%}")
k[2].metric("Blocked", f"{(ev.verdict == 'BLOCKED').sum():,}")
k[3].metric("USDC protected", f"{ev.loc[ev.verdict == 'BLOCKED', 'usdc'].sum():,.0f}")

t1, t2, t3, t4, t5 = st.tabs(["Spend guard", "Developer discovery", "Escrow incident", "Month-end close", "Impact and KPIs"])

with t1:
    st.subheader("Test a payment against the mandate")
    c = st.columns(3)
    amt = c[0].number_input("Value (USDC)", min_value=0.0, max_value=500.0, value=75.0)
    dest = c[1].selectbox("Destination", ALL_DEST)
    cps = c[2].number_input("Calls in the last second", min_value=1, max_value=30, value=1)
    reasons = []
    if cps > vel: reasons.append(f"Velocity violation ({cps} calls/sec against a maximum of {vel})")
    if dest not in scope: reasons.append("Out of approved scope")
    if amt > max_tx: reasons.append(f"Mandate exceeded ({amt:.2f} against the {max_tx:.2f} USDC single-call limit)")
    if reasons:
        st.error("BLOCKED. " + "; ".join(reasons) + ". Payload discarded, no network transaction processed.")
    else:
        st.success("ALLOWED. Within every limit. A signed verdict would be issued.")
    st.subheader("Live interception ledger")
    h = ev[ev.verdict == "BLOCKED"].groupby([ev.ts.dt.floor("D"), "exception"]).size().reset_index(name="blocked")
    st.plotly_chart(px.bar(h, x="ts", y="blocked", color="exception", title="Blocked requests per day"), use_container_width=True)
    st.dataframe(ev[ev.verdict == "BLOCKED"][["ts", "agent", "dest", "usdc", "exception"]].tail(40), use_container_width=True, hide_index=True)

with t2:
    st.subheader("Weekly developer discovery protocol")
    LOOPS = {
        "Sandbox friction": ("Walk me through the moment your team set up the local sandbox. Where did the console output confuse you, and did the logs explain why a test transaction tripped a policy cap?",
                             "Reduce integration drop-off by matching setup to developer expectations."),
        "Execution latency": ("What lag are your agents seeing from the synchronous policy check during peak traffic?",
                              "Keep latency low enough to stay the preferred validation layer."),
        "Escrow fallback confidence": ("If a counterparty agent crashes mid-trade, how comfortable is your team with the fallback timeout?",
                                       "Refine contract conditions to ease worry about temporary locks."),
        "Diagnostic logging": ("When a script fails a validation check, which missing diagnostic fields would cut your triage time most?",
                               "Move from generic errors to contextual ones and lower support volume."),
    }
    pick = st.selectbox("Interview loop", list(LOOPS))
    st.info("Question: " + LOOPS[pick][0])
    st.write("Product goal: " + LOOPS[pick][1])
    st.caption("Capture answers in a tracker each week and feed recurring themes into the roadmap.")

with t3:
    st.subheader("Escrow stall: customer-safe resolution")
    c = st.columns(3)
    amount = c[0].number_input("Locked amount (USDC)", min_value=100, max_value=100000, value=2500)
    left = c[1].slider("Minutes left in the timeout window", min_value=0, max_value=30, value=11)
    revived = c[2].checkbox("Counterparty agent revived and completed", value=False)
    state = "SETTLED" if revived else ("REFUND AVAILABLE" if left == 0 else "LOCKED, timeout running")
    st.metric("Escrow state", state, f"{left} min left" if not revived else "settled normally")
    name = st.text_input("Developer name", value="Alex")
    st.text_area("Outbound message", height=260, value=(
        f"Subject: Settlement loop triage, escrow reference BASE-ESC-0001\n\nHi {name},\n\n"
        f"Your agent loop is paused at the block layer on Base because a counterparty agent failed. Your {amount:,} USDC is secure in the non-custodial escrow contract, locked only by onchain logic.\n\n"
        f"Status: {state}. {'' if revived else f'If the counterparty does not complete within {left} minutes, the fallback opens and your mandate can issue a clean refund.'}\n\n"
        "A direct channel with our engineers is open for live updates.\n\nBest regards,\nProduct Manager"))

with t4:
    st.subheader("Automated month-end close")
    led = ev[ev.verdict == "ALLOWED"].copy()
    led["day"] = led.ts.dt.date
    inject = st.checkbox("Inject a mismatch to see detection", value=False)
    led["onchain_usdc"] = led.usdc
    if inject and len(led):
        led.loc[led.index[len(led) // 2], "onchain_usdc"] += 0.01
    led["match"] = (led.usdc - led.onchain_usdc).abs() < 1e-9
    parity = led.match.mean() if len(led) else 1.0
    m = st.columns(3)
    m[0].metric("Line items", f"{len(led):,}")
    m[1].metric("Data parity", f"{parity:.2%}")
    m[2].metric("Discrepancies", int((~led.match).sum()))
    by_client = led.groupby("agent").agg(requests=("usdc", "size"), usdc=("usdc", "sum")).round(2)
    st.write("Usage grouped by client agent (seller view)")
    st.dataframe(by_client, use_container_width=True)
    st.download_button("Download reconciled export (CSV)", led[["ts", "agent", "chain", "dest", "usdc", "onchain_usdc", "match", "proof"]].to_csv(index=False),
                       "reconciliation_export.csv", "text/csv")
    st.caption("Each line carries a proof hash. Here it is a demo SHA-256, not a real signed verdict or onchain transaction hash.")

with t5:
    st.subheader("Impact model (assumptions you can change)")
    c = st.columns(3)
    before = c[0].number_input("Manual close hours per month", min_value=1, max_value=200, value=48)
    after = c[1].number_input("Automated close minutes", min_value=1, max_value=240, value=5)
    rate = c[2].number_input("Loaded hourly cost (USD)", min_value=10, max_value=300, value=60)
    saved = before - after / 60
    st.metric("Hours saved per month", f"{saved:.1f}", f"{saved / before:.1%} of manual time")
    st.metric("Annual cost avoided per finance team", f"${saved * 12 * rate:,.0f}")
    st.markdown("**KPIs:** close time 48h to under 5 min; more than 80% of sandboxes generate a mock report in 14 days; 0.00% discrepancy between local logs, exports and onchain events.")
