# 🎓 Rahbar AI

**Verified admission decision-support for Pakistani FSc students.**

Rahbar AI helps students decide **where** and **when** to apply for university admission — using verified admission data and clear next actions instead of guesswork.

Built for the PakAngel Mid-Hackathon (Week 3).

---

## The Problem

Pakistani FSc students often miss admission deadlines because:

- University information is scattered across portals, PDFs, and notices.
- Many students don't know they can apply with **FSc Part-I marks** before their final result.
- Aggregate formulas differ across universities and are easy to miscalculate.
- Generic AI tools guess — they can't be trusted with critical deadlines or eligibility.

**Rahbar exists to prevent avoidable missed opportunities.**

---

## The Solution

A Streamlit app that turns verified admission data into a personalized decision:

1. **Aggregate Calculator** — Correct formula for each university, with a transparent breakdown.
2. **Deadline Status** — Dynamically computed (Open / Approaching / Closed / Extended).
3. **Document Checklist** — Exactly what each university requires.
4. **AI Explanation** — Plain-language explanation of the result and next action.
5. **What Should I Do Next?** — Prioritized actions grounded in verified rules.

**Core principle:** Verified data → Deterministic rules → AI explanation. The AI never calculates; it only explains.

---

## Supported Universities (Mid-Hackathon Scope)

| University | Formula |
|---|---|
| **NUST** | NET 75% + HSSC 15% + SSC 10% |
| **UET Taxila** | HSSC-I 50% + ECAT 33% + SSC 17% |
| **FAST** | Test 50% + HSSC 40% + SSC 10% |

---

## Architecture
app.py → Streamlit UI + Gemini call (orchestration only)
engine.py → Deterministic logic (validation, aggregate, deadline, checklist)
data/universities.py → Verified university data registry
requirements.txt → Dependencies
.streamlit/secrets.toml → API keys (never committed)

text

**Design rules:**
- `engine.py` never imports Streamlit.
- `app.py` never defines business logic or university data.
- Every public function returns `{ok, error, raw, summary}`.
- Graceful degradation: if Gemini fails, the rule-based output still renders.
- No classes. Type hints everywhere.

---

## Tech Stack

- **Python 3.10+**
- **Streamlit** — UI
- **Google Gemini** (`google-genai` SDK, model `gemini-3.6-flash`) — AI explanation
- **Streamlit Community Cloud** — Hosting

---

## Run Locally

```bash
# 1. Clone
git clone https://github.com/nisaruddin-dev/rahbar-ai.git
cd rahbar-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your GEMINI_API_KEY

# 4. Run
python -m streamlit run app.py
What's in Scope (Mid-Hackathon)
✅ Aggregate calculator for 3 universities
✅ Dynamic deadline status (computed from date, not hardcoded)
✅ Document checklist per university
✅ AI explanation via Gemini
✅ "What should I do next?" action engine
✅ Source + verification date for every result
✅ Graceful degradation if Gemini fails

What's Not Yet in Scope (Final Hackathon)
🔄 Merit prediction (evidence-based competitiveness)
🔄 2 more universities (COMSATS, QAU)
🔄 RAG-based Q&A on official admission PDFs
🔄 Account system and saved profiles
🔄 Multi-language UI beyond English
🔄 Gap-year action planning

We are building trust first, features second.

The Product Principle
AI = Communication & Personalization Layer
Verified Data = Knowledge Layer
Rules Engine = Decision Layer
Action Engine = Value Layer
Official University = Authority

Live Demo
👉 Live App (will be added post-deployment)

Important
Admission requirements can change. If the official university portal differs from what this app shows, follow the university's current instructions. Rahbar AI is a decision-support tool, not an admission authority.
