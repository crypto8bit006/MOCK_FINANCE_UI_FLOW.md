"""Agent Spend Guard: a mock policy and reconciliation dashboard.

All data is generated in memory with a fixed seed. It is synthetic and represents no real company,
customer or transaction. Run with:  streamlit run app.py
"""
import json

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Agent Spend Guard", layout="wide")

# ---------------- synthetic data ----------------
@st.cache_data
def make_data(seed=11, n_agents=40, n_tx=6000):
    rng = np.random.default_rng(seed)
    agents = [f"agent_{i:03d}" for i in range(n_agents)]
    base = pd.Timestamp("2026-09-01")
    t = base + pd.to_timedelta(np.sort(rng.uniform(0, 7 * 86400, n_tx)), unit="s")
    df = pd.DataFrame({
        "ts": t,
        "agent": rng.choice(agents, n_tx, p=rng.dirichlet(np.ones(n_agents) * 2)),
        "chain": rng.choice(["Base", "Solana"], n_tx, p=[0.55, 0.45]),
        "amount": np.round(rng.lognormal(3.0, 1.1, n_tx), 2),
        "purpose": rng.choice(["api_credits", "data_feed", "compute", "tooling"], n_tx),
    })
    burst = rng.choice(n_tx - 12, 25, replace=False)  # inject rapid repeat calls
    for b in burst:
        df.loc[b:b + 11, "agent"] = df.loc[b, "agent"]
        df.loc[b:b + 11, "ts"] = df.loc[b, "ts"] + pd.to_timedelta(np.arange(12) * 2, unit="s")
    return df.sort_values("ts").reset_index(drop=True)


raw = make_data()

# ---------------- policy rulebook (sidebar) ----------------
st.sidebar.header("Policy rulebook")
cap = st.sidebar.slider("Per-call cap (USD)", 20, 500, 150, 10)
vel = st.sidebar.slider("Max calls per agent per minute", 2, 20, 6)
budget = st.sidebar.slider("Daily budget per agent (USD)", 200, 5000, 1500, 100)
chains = st.sidebar.multiselect("Chains", ["Base", "Solana"], default=["Base", "Solana"])
st.sidebar.caption("Synthetic data only.")


@st.cache_data
def evaluate(cap, vel, budget):
    d = raw.copy()
    d["day"] = d.ts.dt.date
    parts = []
    for _, g in d.groupby("agent"):
        g = g.sort_values("ts").copy()
        g["calls_1m"] = g.set_index("ts")["amount"].rolling("60s").count().values
        g["spent_today"] = g.groupby("day")["amount"].cumsum()
        parts.append(g)
    d = pd.concat(parts).sort_values("ts")
    d["decision"] = "ALLOW"
    d.loc[d.calls_1m > vel, "decision"] = "FLAG_VELOCITY"
    d.loc[d.spent_today > budget, "decision"] = "DENY_BUDGET"
    d.loc[d.amount > cap, "decision"] = "DENY_CAP"
    why = {"ALLOW": "Within all limits", "FLAG_VELOCITY": "Too many calls in one minute",
           "DENY_BUDGET": "Daily budget used up", "DENY_CAP": "Amount above the per-call cap"}
    d["reason"] = d.decision.map(why)
    return d.reset_index(drop=True)


df = evaluate(cap, vel, budget)
df = df[df.chain.isin(chains)]

st.title("Agent Spend Guard")
st.caption("Every payment an autonomous agent requests is checked against a human-approved rulebook before it moves.")

k = st.columns(4)
k[0].metric("Requests", f"{len(df):,}")
k[1].metric("Spend requested", f"${df.amount.sum():,.0f}")
k[2].metric("Allowed", f"{(df.decision == 'ALLOW').mean():.1%}")
k[3].metric("Exceptions", f"{(df.decision != 'ALLOW').sum():,}")

t1, t2, t3, t4, t5 = st.tabs(["Agent metrics", "Velocity exceptions", "Margin variables", "Three personas", "Month-end close"])

with t1:
    a = df.groupby("agent").agg(requests=("amount", "size"), spend=("amount", "sum"),
                                exceptions=("decision", lambda s: (s != "ALLOW").sum())).sort_values("spend", ascending=False)
    a["exception_rate"] = (a.exceptions / a.requests).round(3)
    st.plotly_chart(px.bar(a.head(15).reset_index(), x="agent", y="spend", color="exception_rate",
                           title="Top 15 agents by spend, shaded by exception rate"), use_container_width=True)
    st.dataframe(a.round(2), use_container_width=True)

with t2:
    ex = df[df.decision == "FLAG_VELOCITY"]
    st.write(f"{len(ex):,} requests flagged for more than {vel} calls in a minute.")
    h = df[df.decision != "ALLOW"].groupby([df.ts.dt.floor("6h"), "decision"]).size().reset_index(name="count")
    st.plotly_chart(px.bar(h, x="ts", y="count", color="decision", title="Exceptions per 6 hours"), use_container_width=True)
    st.dataframe(ex[["ts", "agent", "chain", "amount", "calls_1m"]].head(200), use_container_width=True, hide_index=True)

with t3:
    st.write("Net margin per request after processing cost. Adjust the assumptions.")
    c = st.columns(3)
    fee = c[0].slider("Fee (basis points of amount)", 5, 100, 30)
    gas_base = c[1].slider("Cost per request on Base (USD)", 0.0, 1.0, 0.05, 0.01)
    gas_sol = c[2].slider("Cost per request on Solana (USD)", 0.0, 1.0, 0.02, 0.01)
    ok = df[df.decision == "ALLOW"].copy()
    ok["cost"] = np.where(ok.chain == "Base", gas_base, gas_sol)
    ok["margin"] = ok.amount * fee / 10000 - ok.cost
    m = ok.groupby("chain").agg(requests=("amount", "size"), volume=("amount", "sum"), margin=("margin", "sum"))
    m["margin_per_request"] = m.margin / m.requests
    st.dataframe(m.round(3), use_container_width=True)
    st.caption("Small payments can lose money once the fixed processing cost exceeds the fee.")

with t4:
    p = st.radio("View as", ["Developer", "Seller", "Finance"], horizontal=True)
    if p == "Developer":
        st.write("The rulebook is plain JSON, so it can be set up locally in minutes.")
        st.code(json.dumps({"per_call_cap_usd": cap, "max_calls_per_minute": vel, "daily_budget_usd": budget, "chains": chains}, indent=2), language="json")
        st.dataframe(df[["ts", "agent", "amount", "decision"]].tail(15), use_container_width=True, hide_index=True)
    elif p == "Seller":
        st.write("A seller needs to see what happened to each payment, in plain words.")
        st.dataframe(df[["ts", "amount", "decision", "reason"]].tail(25), use_container_width=True, hide_index=True)
    else:
        st.write("Finance needs a readable compliance history it can export.")
        hist = df.groupby(["day", "decision"]).agg(requests=("amount", "size"), amount=("amount", "sum")).reset_index()
        st.dataframe(hist, use_container_width=True, hide_index=True)
        st.download_button("Download audit log (CSV)", df.to_csv(index=False), "audit_log.csv", "text/csv")

with t5:
    st.write("Reconcile the internal ledger against a mock processor statement. The target variance is zero.")
    thr = st.number_input("Variance threshold (USD)", 0.0, 10.0, 0.0, 0.01)
    rng = np.random.default_rng(3)
    led = df[df.decision == "ALLOW"].groupby("day").amount.sum().round(2).rename("ledger")
    stmt = (led + rng.choice([0, 0, 0, 0.01, -0.02, 1.5], len(led))).rename("processor")
    rec = pd.concat([led, stmt], axis=1)
    rec["variance"] = (rec.processor - rec.ledger).round(2)
    rec["status"] = np.where(rec.variance.abs() > thr, "INVESTIGATE", "MATCHED")
    st.dataframe(rec, use_container_width=True)
    st.metric("Days needing investigation", int((rec.status == "INVESTIGATE").sum()))
