"""
Rahbar AI — Main Streamlit Application (v2 — UX-improved)

Architecture rule:
    UI + orchestration ONLY. Calls engine.py. Never defines business logic.

Pipeline:
    Sidebar input -> validate -> calculate -> deadline -> checklist -> next action
                 -> Gemini explanation -> display
"""

import streamlit as st
from google import genai

from data.universities import UNIVERSITIES, SUPPORTED_UNIVERSITIES
import engine


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Rahbar AI",
    page_icon="🎓",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Test max per university — for dynamic hint
# ---------------------------------------------------------------------------

TEST_MAX = {
    "NUST": 200,
    "UET Taxila": 400,
    "FAST": 100,
}

MATRIC_MAX = 1100
HSSC_MAX = 550


# ---------------------------------------------------------------------------
# Cached wrappers
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def cached_validate(university: str, matric: float, hssc: float, test: float) -> dict:
    return engine.validate_inputs(university, matric, hssc, test)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_aggregate(university: str, matric: float, hssc: float, test: float) -> dict:
    return engine.calculate_aggregate(university, matric, hssc, test)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_deadline(university: str) -> dict:
    return engine.get_deadline_status(university)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_checklist(university: str) -> dict:
    return engine.get_document_checklist(university)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_next_action(university: str, aggregate: float, deadline_status: str) -> dict:
    return engine.get_next_action(university, aggregate, deadline_status)


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------

def call_gemini(
    university: str,
    aggregate: float,
    formula_string: str,
    deadline_status: str,
    deadline_date: str,
    documents: list,
    source_url: str,
    last_verified: str,
) -> str | None:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            print("GEMINI ERROR: API key missing.")
            return None

        client = genai.Client(api_key=api_key)

        prompt = f"""You are an admission counselor for Pakistani FSc students.

Student context:
- University: {university}
- Aggregate: {aggregate}%
- Formula used: {formula_string}
- Deadline: {deadline_date} (Status: {deadline_status})
- Documents required: {', '.join(documents)}
- Official source: {source_url}
- Last verified: {last_verified}

Explain in simple English (max 150 words):
1. What this aggregate means for the student.
2. Why the deadline status matters.
3. The single most important next action.

Rules:
- Do not invent facts.
- If the deadline is Closed, tell them to check for extension notices.
- End with: "Always confirm at the official portal."
- Be honest, not flattering."""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        if response and response.text:
            return response.text.strip()
        return None

    except Exception as e:
        print(f"GEMINI ERROR: {type(e).__name__}: {str(e)[:200]}")
        return None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🎓 Rahbar AI")
    st.caption("Verified admission guidance for Pakistani FSc students.")

    university = st.selectbox(
        "Target University",
        options=SUPPORTED_UNIVERSITIES,
        index=0,
    )

    test_max_current = TEST_MAX.get(university, 100)

    st.markdown("**Your Marks**")
    st.caption("Defaults are examples — change to yours.")

    matric = st.number_input(
        f"Matric / SSC (max {MATRIC_MAX})",
        min_value=0,
        max_value=MATRIC_MAX,
        value=850,
        step=1,
    )

    hssc = st.number_input(
        f"FSc Part-I / HSSC (max {HSSC_MAX})",
        min_value=0,
        max_value=HSSC_MAX,
        value=450,
        step=1,
    )

    test = st.number_input(
        f"Entry Test (max {test_max_current} for {university})",
        min_value=0,
        max_value=1000,
        value=min(140, test_max_current),
        step=1,
        help=f"{university} test maximum is {test_max_current}.",
    )

    analyze = st.button(
        "🔍 Analyze My Chances",
        type="primary",
        use_container_width=True,
    )

# ---------------------------------------------------------------------------
# Main — Landing (before analyze)
# ---------------------------------------------------------------------------

st.title("Your Admission Decision")
st.caption(
    "Rahbar AI converts verified admission data into a clear decision and next actions."
)

if not analyze:
    st.info(
        "👈 Enter your marks and select a university in the sidebar, "
        "then click **Analyze My Chances**."
    )

    # Show all-university status preview
    st.subheader("📅 Current Deadline Snapshot")
    preview_cols = st.columns(3)
    for i, uni in enumerate(SUPPORTED_UNIVERSITIES):
        d = cached_deadline(uni)
        status = d["summary"]["status"]
        with preview_cols[i]:
            if status == "Open":
                st.success(f"**{uni}**\n\n✅ Open")
            elif status == "Approaching":
                st.warning(f"**{uni}**\n\n⚠️ Approaching")
            elif status == "Closed":
                st.error(f"**{uni}**\n\n🔒 Closed")
            else:
                st.info(f"**{uni}**\n\nℹ️ {status}")

    st.stop()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

validation = cached_validate(university, matric, hssc, test)
if not validation["ok"]:
    st.error(f"⚠️ {validation['error']}")
    st.stop()


# ---------------------------------------------------------------------------
# Compute
# ---------------------------------------------------------------------------

aggregate_result = cached_aggregate(university, matric, hssc, test)
if not aggregate_result["ok"]:
    st.error(f"⚠️ Aggregate calculation failed: {aggregate_result['error']}")
    st.stop()

aggregate = aggregate_result["summary"]["aggregate"]
formula_string = aggregate_result["summary"]["formula_string"]
weighted = aggregate_result["raw"]["components_weighted"]
components_pct = aggregate_result["raw"]["components_pct"]

deadline_result = cached_deadline(university)
deadline_status = deadline_result["summary"]["status"]
deadline_message = deadline_result["summary"]["message"]
deadline_date = deadline_result["summary"]["deadline"]

checklist_result = cached_checklist(university)
documents = checklist_result["summary"]["documents"]

next_action_result = cached_next_action(university, aggregate, deadline_status)
actions = next_action_result["summary"]["actions"]
portal_url = next_action_result["summary"]["portal_url"]


# ---------------------------------------------------------------------------
# Summary decision card
# ---------------------------------------------------------------------------

st.subheader("📌 Your Decision at a Glance")

summary_cols = st.columns(3)
with summary_cols[0]:
    st.metric(f"{university} Aggregate", f"{aggregate}%")
with summary_cols[1]:
    if deadline_status == "Open":
        st.metric("Deadline Status", "✅ Open")
    elif deadline_status == "Approaching":
        st.metric("Deadline Status", "⚠️ Approaching")
    elif deadline_status == "Closed":
        st.metric("Deadline Status", "🔒 Closed")
    else:
        st.metric("Deadline Status", deadline_status)
with summary_cols[2]:
    st.metric("Documents Required", len(documents))

st.divider()


# ---------------------------------------------------------------------------
# Aggregate details
# ---------------------------------------------------------------------------

st.header("📊 Your Aggregate")

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label=f"{university} Aggregate", value=f"{aggregate}%")

with col2:
    st.markdown(f"**Formula used:** `{formula_string}`")
    with st.expander("See component breakdown"):
        for key, weighted_value in weighted.items():
            pct = components_pct.get(key, 0)
            st.write(f"**{key.upper()}**: {pct}% × weight = **{weighted_value}**")
        st.caption(f"Sum of weighted components = {aggregate}%")


# ---------------------------------------------------------------------------
# Deadline status
# ---------------------------------------------------------------------------

st.header("⏰ Deadline Status")

if deadline_status == "Open":
    st.success(f"✅ **{deadline_status}** — {deadline_message}")
elif deadline_status == "Approaching":
    st.warning(f"⚠️ **{deadline_status}** — {deadline_message}")
elif deadline_status == "Closed":
    st.error(f"🔒 **{deadline_status}** — {deadline_message}")
elif deadline_status == "Extended":
    st.info(f"📅 **{deadline_status}** — {deadline_message}")
else:
    st.info(f"ℹ️ **{deadline_status}** — {deadline_message}")


# ---------------------------------------------------------------------------
# Alternative universities if selected one is Closed
# ---------------------------------------------------------------------------

if deadline_status == "Closed":
    st.subheader("🔀 Also Consider These Universities")

    alternatives = [
        u for u in SUPPORTED_UNIVERSITIES
        if u != university and cached_deadline(u)["summary"]["status"] != "Closed"
    ]

    if alternatives:
        alt_cols = st.columns(len(alternatives))
        for i, alt_uni in enumerate(alternatives):
            alt_deadline = cached_deadline(alt_uni)
            alt_status = alt_deadline["summary"]["status"]
            with alt_cols[i]:
                if alt_status == "Open":
                    st.success(f"**{alt_uni}**\n\n✅ Open")
                elif alt_status == "Approaching":
                    st.warning(f"**{alt_uni}**\n\n⚠️ Approaching")
                else:
                    st.info(f"**{alt_uni}**\n\nℹ️ {alt_status}")
                st.caption(f"Deadline: {alt_deadline['summary']['deadline']}")
    else:
        st.warning(
            "All supported universities have closed deadlines for the current cycle. "
            "Check each official portal for extension notices or next-cycle dates."
        )


# ---------------------------------------------------------------------------
# Document checklist
# ---------------------------------------------------------------------------

st.header("📄 Required Documents")
for doc in documents:
    st.checkbox(doc, value=False, key=f"doc_{university}_{doc}")


# ---------------------------------------------------------------------------
# Next action
# ---------------------------------------------------------------------------

st.header("🎯 What Should I Do Next?")
for i, action in enumerate(actions, start=1):
    st.markdown(f"**{i}.** {action}")

st.markdown(f"👉 [Open the official {university} portal]({portal_url})")


# ---------------------------------------------------------------------------
# AI explanation
# ---------------------------------------------------------------------------

st.header("🤖 AI Explanation")

with st.spinner("Gemini is writing your explanation..."):
    explanation = call_gemini(
        university=university,
        aggregate=aggregate,
        formula_string=formula_string,
        deadline_status=deadline_status,
        deadline_date=deadline_date,
        documents=documents,
        source_url=portal_url,
        last_verified=UNIVERSITIES[university]["last_verified"],
    )

if explanation:
    with st.container(border=True):
        st.markdown(explanation)
else:
    st.warning(
        "⚠️ AI explanation is temporarily unavailable. "
        "Your aggregate, deadline status, and checklist above are still accurate."
    )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    f"**Source:** {portal_url} · "
    f"**Last verified:** {UNIVERSITIES[university]['last_verified']} · "
    f"**Status:** Verified"
)

note = UNIVERSITIES[university].get("verification_note")
if note:
    st.caption(f"⚠️ {note}")

st.caption(
    "Admission requirements can change. If the official university portal differs "
    "from this information, follow the university's current instructions."
)