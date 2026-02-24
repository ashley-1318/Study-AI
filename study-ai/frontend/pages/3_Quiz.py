"""StudyAI — Adaptive Quiz page."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

st.set_page_config(page_title="StudyAI — Quiz", page_icon="📚", layout="wide")

from streamlit_auth import require_auth, show_user_sidebar
from api_client import api_get, api_post

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0b0c14}
section[data-testid="stSidebar"]{background:#0d0e1a!important;border-right:1px solid #1e2135!important}
h1,h2,h3{font-family:Syne,sans-serif!important;color:#e8e9f0!important}
.stButton>button{background:rgba(31,184,154,0.08)!important;border:1px solid rgba(31,184,154,0.4)!important;color:#1fb89a!important;border-radius:12px!important;font-family:Syne,sans-serif!important;font-weight:700!important;transition:all 0.3s!important}
.stButton>button:hover{background:#1fb89a!important;color:#0b0c14!important}
.stRadio>div>label{color:#e8e9f0!important}
</style>""", unsafe_allow_html=True)

user = require_auth()

with st.sidebar:
    st.markdown("""<div style='display:flex;align-items:center;gap:12px;padding:16px 8px 24px;border-bottom:1px solid #1e2135;margin-bottom:16px'>
        <span style='font-size:28px'>📚</span>
        <span style='font-family:Syne,sans-serif;font-weight:900;font-size:24px'>
            <span style='color:#1fb89a'>Study</span><span style='color:#e8a020'>AI</span>
        </span></div>""", unsafe_allow_html=True)
    st.page_link("app.py",              label="🏠 Home")
    st.page_link("pages/1_dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_upload.py",    label="📤 Upload Material")
    st.page_link("pages/3_quiz.py",      label="❓ Adaptive Quiz")
    st.page_link("pages/4_summaries.py", label="📝 Summaries")
    st.page_link("pages/5_revision.py",  label="🔄 Revision Planner")
    st.page_link("pages/6_analytics.py", label="📈 Analytics")
    show_user_sidebar()

# ── Back button
_back_col, _title_col = st.columns([1, 9])
with _back_col:
    if st.button("← Back", key="back_quiz"):
        # Clear any active quiz state before going back
        for k in ("active_quiz", "current_q_idx", "quiz_answers", "answered_current", "show_result"):
            st.session_state.pop(k, None)
        st.switch_page("app.py")

st.title("❓ Adaptive Quiz — StudyAI")

# ── Quiz Setup ─────────────────────────────────────────────────────────────

if "active_quiz" not in st.session_state:
    mats_resp  = api_get("/materials/")
    materials  = mats_resp.get("data", []) if mats_resp else []
    done_mats  = [m for m in materials if m.get("status") == "done"]

    with st.container():
        st.markdown("""
            <div style='background:rgba(18,20,31,0.7);border-radius:20px;padding:32px;border:1px solid #1e2135;max-width:700px'>
                <h2 style='margin-top:0;color:#e8e9f0'>🎯 Configure Your Quiz</h2>
            </div>""", unsafe_allow_html=True)

        material_options = {"All Materials (Weakest Concepts)": None}
        for m in done_mats:
            material_options[m["filename"]] = m["id"]

        selected_mat_name = st.selectbox("📚 Source Material", list(material_options.keys()), key="quiz_mat_selector")
        selected_mat_id   = material_options[selected_mat_name]

        # Override if coming from upload page
        if st.session_state.get("quiz_material_id"):
            selected_mat_id = st.session_state.pop("quiz_material_id")

        col1, col2 = st.columns(2)
        with col1:
            difficulty = st.selectbox("⚡ Difficulty", ["adaptive", "easy", "medium", "hard"], index=0, key="quiz_diff")
        with col2:
            q_count = st.slider("🔢 Questions", min_value=5, max_value=20, value=10, key="quiz_count")

        if st.button("🎯 Generate Quiz", type="primary", use_container_width=True, key="gen_quiz_btn"):
            if not done_mats and not selected_mat_id:
                st.warning("Upload and process at least one material first.")
            else:
                with st.spinner("Generating adaptive questions with AI…"):
                    resp = api_post("/quiz/generate", json={
                        "material_id":    selected_mat_id,
                        "difficulty":     difficulty,
                        "question_count": q_count,
                    })
                if resp and resp.get("success"):
                    st.session_state["active_quiz"]       = resp["data"]
                    st.session_state["current_q_idx"]     = 0
                    st.session_state["quiz_answers"]      = []
                    st.session_state["answered_current"]  = False
                    st.session_state["show_result"]       = False
                    st.session_state["submitted"]         = False
                    st.rerun()
                else:
                    st.error("Quiz generation failed. Check backend connection.")

    # Quiz history
    st.markdown("<br>### 📋 Quiz History", unsafe_allow_html=True)
    hist_resp = api_get("/quiz/history")
    history   = hist_resp.get("data", []) if hist_resp else []
    if history:
        for q in history:
            score_color = "#22c55e" if (q.get("score") or 0) >= 70 else "#e8a020" if (q.get("score") or 0) >= 40 else "#ef4444"
            score_str   = f"{q['score']:.0f}%" if q.get("score") is not None else "Pending"
            st.markdown(f"""
                <div style='padding:14px;background:rgba(18,20,31,0.6);border-radius:12px;
                    margin-bottom:8px;border:1px solid #1e2135;display:flex;justify-content:space-between'>
                    <div>
                        <b style='color:#e8e9f0'>{q.get('material_name','All materials')}</b>
                        <br><small style='color:#7a7f9a'>{q.get('difficulty','').upper()} · {q.get('question_count',0)} Qs · {(q.get('taken_at') or q.get('created_at',''))[:10]}</small>
                    </div>
                    <span style='color:{score_color};font-family:Syne,sans-serif;font-weight:800;font-size:22px'>{score_str}</span>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#7a7f9a'>No quizzes taken yet.</p>", unsafe_allow_html=True)

else:
    # ── Active Quiz ──────────────────────────────────────────────────────────
    quiz      = st.session_state["active_quiz"]
    questions = quiz.get("questions", [])
    idx       = st.session_state["current_q_idx"]
    total     = len(questions)

    if st.session_state.get("show_result"):
        # ── End Screen ──────────────────────────────────────────────────────
        answers   = st.session_state.get("quiz_answers", [])
        quiz_id   = quiz.get("quiz_id")

        # Submit to backend if not already done
        if quiz_id and not st.session_state.get("submitted"):
            from api_client import api_post
            payload = {
                "answers": [
                    {"question_index": a["question_index"], "answer": a["user_answer"]}
                    for a in answers
                ]
            }
            api_post(f"/quiz/{quiz_id}/submit", json=payload)
            st.session_state["submitted"] = True

        correct   = sum(1 for a in answers if a.get("correct"))
        total     = len(questions)
        score_pct = correct / max(total, 1) * 100

        score_color = "#22c55e" if score_pct >= 70 else "#e8a020" if score_pct >= 40 else "#ef4444"
        st.markdown(f"""
            <div style='text-align:center;padding:48px;background:rgba(18,20,31,0.8);
                border-radius:24px;border:1px solid #1e2135;margin-bottom:32px'>
                <div style='font-size:80px;font-family:Syne,sans-serif;font-weight:900;color:{score_color}'>{score_pct:.0f}%</div>
                <div style='font-size:24px;color:#e8e9f0;margin-top:8px'>
                    {correct}/{total} Correct
                </div>
                <p style='color:#7a7f9a;margin-top:16px;font-style:italic'>
                    {'🎉 Excellent! Keep it up!' if score_pct >= 70 else '📚 Good effort! Review weak areas.' if score_pct >= 40 else '💪 Keep studying — practice makes perfect!'}
                </p>
            </div>""", unsafe_allow_html=True)

        # Breakdown
        st.markdown("#### 📋 Answer Breakdown")
        for i, a in enumerate(answers):
            ok_icon = "✅" if a.get("correct") else "❌"
            st.markdown(f"""
                <div style='padding:12px 16px;background:rgba(18,20,31,0.5);border-radius:10px;
                    margin-bottom:8px;border-left:3px solid {"#22c55e" if a.get("correct") else "#ef4444"}'>
                    <b style='color:#e8e9f0'>{ok_icon} Q{i+1}: {a.get("question","")[:100]}</b><br>
                    <small style='color:#7a7f9a'>Your answer: <b style='color:#e8e9f0'>{a.get("user_answer","—")}</b> · Correct: <b style='color:#1fb89a'>{a.get("correct_ans","")}</b></small>
                    {f"<br><small style='color:#5a6080;font-style:italic'>{a.get('explanation','')[:150]}</small>" if a.get("explanation") else ""}
                </div>""", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔁 Try Again", use_container_width=True, key="retry_quiz"):
                for k in ("active_quiz", "current_q_idx", "quiz_answers", "answered_current", "show_result", "submitted"):
                    st.session_state.pop(k, None)
                st.rerun()
        with col_b:
            if st.button("🔄 Create Revision Plan", use_container_width=True, key="to_revision"):
                st.switch_page("pages/5_revision.py")

    elif idx < total:
        # ── Question View ─────────────────────────────────────────────────
        q = questions[idx]

        # Progress
        progress_val = (idx) / total
        st.progress(progress_val)
        st.markdown(f"<p style='color:#7a7f9a;text-align:right'>{idx+1} / {total}</p>", unsafe_allow_html=True)

        # Question Card
        st.markdown(f"""
            <div style='background:rgba(18,20,31,0.8);border:1px solid #1e2135;border-radius:20px;
                padding:32px;margin-bottom:24px'>
                <p style='color:#7a7f9a;font-size:12px;text-transform:uppercase;letter-spacing:2px'>{q.get("type","mcq").upper()} · {q.get("concept","")}</p>
                <h3 style='color:#e8e9f0;margin:8px 0 0'>{q.get("question","")}</h3>
            </div>""", unsafe_allow_html=True)

        user_answer = None
        answered    = st.session_state.get("answered_current", False)

        if q.get("type") == "mcq":
            opts = q.get("options", [])
            if opts:
                chosen = st.radio("Select your answer:", opts, key=f"mcq_{idx}", index=None)
                user_answer = chosen

        elif q.get("type") == "truefalse":
            tf_col1, tf_col2 = st.columns(2)
            with tf_col1:
                if st.button("✅ True", key=f"tf_t_{idx}", use_container_width=True):
                    user_answer = "True"
                    st.session_state[f"tf_ans_{idx}"] = "True"
            with tf_col2:
                if st.button("❌ False", key=f"tf_f_{idx}", use_container_width=True):
                    user_answer = "False"
                    st.session_state[f"tf_ans_{idx}"] = "False"
            user_answer = st.session_state.get(f"tf_ans_{idx}", user_answer)

        else:  # fillblank
            user_answer = st.text_input("✍️ Your answer:", placeholder="Type your answer here…", key=f"fill_{idx}")

        if not answered:
            if st.button("Submit Answer", key=f"submit_{idx}", use_container_width=True):
                if user_answer:
                    # Grade locally against masked answer
                    correct_ans = q.get("answer", "")
                    is_correct  = str(user_answer).strip().lower() == str(correct_ans).strip().lower()

                    st.session_state["quiz_answers"].append({
                        "question_index": idx,
                        "question":       q.get("question", ""),
                        "user_answer":    str(user_answer),
                        "correct_ans":    correct_ans,
                        "correct":        is_correct,
                        "explanation":    q.get("explanation", ""),
                    })
                    st.session_state["answered_current"] = True

                    if is_correct:
                        st.success(f"✅ Correct! {q.get('explanation','')}")
                    else:
                        st.error(f"❌ Incorrect. Correct answer: **{correct_ans}**\n\n*{q.get('explanation','')}*")
                else:
                    st.warning("Please enter an answer before submitting.")

        if st.session_state.get("answered_current"):
            label = "Next Question →" if idx < total - 1 else "🏁 Finish Quiz"
            if st.button(label, key=f"next_{idx}", use_container_width=True):
                st.session_state["current_q_idx"]    = idx + 1
                st.session_state["answered_current"] = False
                if idx >= total - 1:
                    st.session_state["show_result"] = True
                st.rerun()
