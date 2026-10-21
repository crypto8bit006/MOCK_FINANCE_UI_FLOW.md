"""Saifuro Product Suite: strategy and operational playbook, presented as a dashboard.

Independent portfolio piece by Anirban Majumder. Not affiliated with or endorsed by any company.
All ledger events, figures and examples are illustrative. Run with:  streamlit run app.py
"""
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

PAGES = ["Overview", "1 Governance layer", "2 Live interceptions", "3 Developer discovery", "4 Crisis response", "5 Month-end close spec", "6 KPIs and scope"]
page = st.sidebar.radio("Playbook sections", PAGES)
st.sidebar.caption("Unofficial portfolio piece. Illustrative examples only.")

if page == "Overview":
    c = st.columns(3)
    c[0].markdown('<div class="card"><div class="big">48h to 5min</div><div class="bigsub">Target time to close monthly agent accounting records</div></div>', unsafe_allow_html=True)
    c[1].markdown('<div class="card"><div class="big">3</div><div class="bigsub">Personas served: developer, seller, finance team</div></div>', unsafe_allow_html=True)
    c[2].markdown('<div class="card"><div class="big">0.00%</div><div class="bigsub">Target discrepancy between local logs, exports and onchain events</div></div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("The problem")
    st.write("Corporate accounting is not built to reconcile fluid, sub-second machine-to-machine micro-transactions. "
             "Saifuro turns cryptographic assertions into explicit financial guardrails, so enterprises can let autonomous agents spend without losing control.")
    row([card("Govern", "A human administrator sets an offchain spending rulebook before any agent can act.", "Part 1"),
         card("Delight", "Weekly developer discovery and a calm, transparent crisis playbook keep builders confident.", "Part 1"),
         card("Close the books", "A one-click engine reconciles multi-chain activity into clean, auditable accounting files.", "Part 2")])

elif page == "1 Governance layer":
    st.subheader("The corporate mandate governance layer")
    st.write("Before an agent can change state on an external network, a human sets five absolute thresholds.")
    row([card("Agent Wallet ID", "EIP-55 hexadecimal public address. The verifiable identity of the automated worker node.", "Identity"),
         card("Settlement Chain", "Base or Solana. The native rails where capital locks and moves.", "Network"),
         card("Approved Scope", "Target contract function-signature arrays. Restricts the agent to specific, safe vendors.", "Scope")])
    st.write("")
    row([card("Max Tx Limit", "A rigid USDC ceiling per verification call. Protects against runaway loops.", "Limit"),
         card("Velocity Window", "A sliding-scale rate-limit check. Prevents rapid drainage through low-value script errors.", "Rate"),
         card("Why it matters", "Every rule is checked synchronously. A broken parameter returns an explicit error code and no network transaction is processed.", "Outcome")])

elif page == "2 Live interceptions":
    st.subheader("Production ledger sample: real-time interceptions")
    st.write("The spend guard evaluates each payload synchronously and drops an explicit error code when a parameter breaks.")
    EV = [
        ("TX-9041", "2026-10-21 14:02:11", "Alchemy_LLM_Router", "5.00", "Velocity Violation",
         "12 calls/sec detected against a maximum rule of 3 calls/sec.", "System auto-throttled. Payload discarded. Alert sent to developer log.", 12, 3, "calls per second"),
        ("TX-9042", "2026-10-21 14:05:00", "OpenAI_Context_Refuel", "75.00", "Mandate Exceeded",
         "Value request surpasses the 50.00 USDC single-call limit.", "Transaction frozen. Signed override request sent to the Financial Controller.", 75, 50, "USDC"),
    ]
    for eid, ts, dest, val, exc, detail, action, observed, limit, unit in EV:
        a, b = st.columns([3, 2])
        with a:
            st.markdown(f'<div class="card"><div class="tag">{eid} · {ts} UTC</div><h4>{dest} · {val} USDC &nbsp;<span class="blocked">BLOCKED</span></h4>'
                        f'<p><b>{exc}.</b> {detail}<br><br><b>Next step:</b> {action}<br><span style="opacity:.6">Agent 0x7a8b...321f</span></p></div>', unsafe_allow_html=True)
        with b:
            fig = go.Figure(go.Bar(x=[observed, limit], y=["Observed", "Rule limit"], orientation="h", marker_color=["#D92D20", "#0E7C86"], text=[observed, limit], textposition="outside"))
            fig.update_layout(height=170, margin=dict(l=0, r=30, t=10, b=0), xaxis_title=unit, xaxis_range=[0, max(observed, limit) * 1.25], showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.write("")

elif page == "3 Developer discovery":
    st.subheader("Developer discovery and product optimization")
    st.write("Run discovery loops every week, capture developer patterns, and feed them into the roadmap. Four loops isolate deployment friction.")
    LOOPS = {
        "Sandbox friction": ("Walk me through the exact moment your team initialized the local self-serve sandbox. At what point did the console output confuse you, and did the error logs clearly explain why an experimental transaction tripped a policy cap?",
                             "Check that local setup matches onboarding expectations, to reduce integration drop-off."),
        "Execution latency": ("Because the validation engine runs synchronous policy checks against human mandates before producing a signed verdict, what execution lag are your agents seeing during peak traffic?",
                              "Keep latency low enough to remain the preferred validation layer for high-speed agent networks."),
        "Escrow fallback confidence": ("Your workloads use our onchain Base escrow for counterparty settlement. If a counterparty agent hits an uncaught exception mid-trade, how comfortable is your operations team with the fallback timeout mechanics?",
                                       "Refine contract conditions to ease developer worry about temporary block-level locks."),
        "Diagnostic logging": ("When a deployment script fails a validation check, which missing diagnostic data would most reduce your engineering team's triage time?",
                               "Move from generic errors to contextual insight, lowering support ticket volume."),
    }
    tabs = st.tabs(list(LOOPS))
    for t, (name, (q, goal)) in zip(tabs, LOOPS.items()):
        with t:
            row([card("PM question", q, "Ask"), card("Product goal", goal, "Why")])

elif page == "4 Crisis response":
    st.subheader("High-value crisis management: escrow stall")
    row([card("Incident", "Onchain settlement escrow stall.", "Profile"),
         card("Customer", "Lead core engineer at a tier-1 autonomous API aggregator.", "Profile"),
         card("Problem", "A counterparty agent crashed mid-transaction, locking 2,500 USDC in the non-custodial Base escrow fallback window. The customer is anxious about capital security.", "Situation")])
    st.write("")
    st.markdown("**Response principles:** full transparency, a precise explanation, and an immediate next step.")
    for title, body in [("System isolation", "The counterparty agent exited with a non-zero code mid-execution, so the escrow contract engaged its safety lock to protect the customer's capital."),
                        ("Asset security verification", "The 2,500 USDC stays in the non-custodial contract. Funds are locked only by immutable smart contract logic onchain."),
                        ("Path to resolution", "The timeout window is ticking. If the counterparty does not complete within 11 minutes, the fallback opens automatically and the mandate can issue a clean refund.")]:
        st.markdown(f'<div class="step"><b>{title}</b><br>{body}</div>', unsafe_allow_html=True)
    st.markdown("**Outbound response template**")
    st.code("""Subject: URGENT: Settlement Loop Triage - Escrow Reference #BASE-ESC-9982

Hi [Developer Name],

I see your automated procurement loop is currently locked at the block layer on Base due to a counterparty agent failure. I completely understand how critical this 2,500 USDC settlement timeline is for your operational pipeline. Our core priority is keeping your agent workflows safe and predictable.

1. System Isolation: The counterparty agent encountered a non-zero exit code mid-execution. To protect your capital, our Base escrow contract automatically engaged its safety lock.
2. Asset Security Verification: Your 2,500 USDC remains secure within the non-custodial escrow contract. Funds are locked strictly by immutable smart contract logic onchain.
3. The Path to Resolution: The contract's timeout window is ticking down. If the counterparty loop does not safely complete within the next 11 minutes, the fallback mechanism opens automatically and your mandate can issue a clean refund.

I have set up a direct channel with our engineering team: [Slack/Telegram War-Room Link]. You can follow live updates until your funds are back in your primary wallet. We have your back.

Best regards,
Anirban Majumder
Product Manager""", language="text")

elif page == "5 Month-end close spec":
    st.subheader("Feature spec: automated month-end close and financial reconciliation engine")
    st.write("Saifuro operates across Base and Solana, where thousands of autonomous transactions run daily. At month end, finance teams manually pull logs from several explorers, match them to developer API keys, verify mandate boundaries and build accounting files. That takes 48 to 72 hours, adds data-entry risk and delays reporting, which makes enterprises hesitant to deploy agents at scale.")
    st.markdown("**The solution:** a one-click engine that pulls multi-chain data, validates it against historical mandates, and outputs clean, compliant accounting files.")
    fig = go.Figure(go.Bar(x=["Manual close (today)", "Automated close (target)"], y=[48, 5 / 60], marker_color=["#98A2B3", "#0E7C86"], text=["48 hours", "under 5 minutes"], textposition="outside"))
    fig.update_layout(height=300, yaxis_title="Hours", showlegend=False, margin=dict(t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**Impact by persona**")
    row([card("Developer", "No custom tracking scripts. A new endpoint, GET /v1/reconciliation/export, returns pre-reconciled records straight into their systems.", "Integrating agents"),
         card("Seller", "Instant clarity on monthly API usage revenue from autonomous buyers, grouped by client API key, removing billing discrepancies and chargeback disputes.", "Selling APIs to agents"),
         card("Finance team", "A clean web view instead of block-explorer research, and one spreadsheet that works with QuickBooks or NetSuite. Every line links to its onchain verification hash.", "Compliance and auditing")])

else:
    st.subheader("Success metrics and engineering scope")
    row([card("Reconciliation friction velocity", "Cut monthly close time from 48 hours to under 5 minutes.", "Primary metric"),
         card("Sandbox onboarding engagement", "More than 80% of testing sandboxes generate at least one mock month-end report within 14 days.", "Adoption"),
         card("Data parity accuracy", "0.00% discrepancy between local logs, exported spreadsheets and onchain events across Base and Solana.", "Guardrail")])
    st.write("")
    st.markdown("**Engineering scope for the next sprint**")
    row([card("Data aggregation layer", "Scrape internal event logs by Agent_Wallet_ID, and cache locally to avoid public RPC rate limits during month-end spikes.", "Build"),
         card("Cryptographic proof matrix", "Bundle each line item with a verification signature matching the V2 signed verdict spec, so auditors can trace validity without block explorers.", "Build"),
         card("Export pipeline", "A resilient streaming CSV/XLSX worker that handles more than 100,000 transaction objects without timeouts or memory exhaustion.", "Build")])

st.markdown('<div class="foot">Independent portfolio piece by Anirban Majumder. Illustrative examples, not affiliated with or endorsed by any company.</div>', unsafe_allow_html=True)
