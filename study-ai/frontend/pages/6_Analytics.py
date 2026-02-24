"""StudyAI — Analytics page with Plotly charts."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="StudyAI — Analytics", page_icon="📚", layout="wide")

from streamlit_auth import require_auth, show_user_sidebar
from api_client import api_get

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0b0c14}
section[data-testid="stSidebar"]{background:#0d0e1a!important;border-right:1px solid #1e2135!important}
h1,h2,h3{font-family:Syne,sans-serif!important;color:#e8e9f0!important}
[data-testid="metric-container"]{background:rgba(18,20,31,0.7)!important;border:1px solid #1e2135!important;border-radius:16px!important;border-left:4px solid #1fb89a!important}
[data-testid="stMetricValue"]{font-family:Syne,sans-serif!important;font-size:36px!important;font-weight:800!important}
</style>""", unsafe_allow_html=True)

user = require_auth()

with st.sidebar:
    st.markdown("""<div style='display:flex;align-items:center;gap:12px;padding:16px 8px 24px;border-bottom:1px solid #1e2135;margin-bottom:16px'>
        <span style='font-size:28px'>📚</span>
        <span style='font-family:Syne,sans-serif;font-weight:900;font-size:24px'>
            <span style='color:#1fb89a'>Study</span><span style='color:#e8a020'>AI</span>
        </span></div>""", unsafe_allow_html=True)
    st.page_link("app.py",              label="🏠 Home")
    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_Upload.py",    label="📤 Upload Material")
    st.page_link("pages/3_Quiz.py",      label="❓ Adaptive Quiz")
    st.page_link("pages/4_Summaries.py", label="📝 Summaries")
    st.page_link("pages/5_Revision.py",  label="🔄 Revision Planner")
    st.page_link("pages/6_Analytics.py", label="📈 Analytics")
    show_user_sidebar()

# ── Back button
_back_col, _title_col = st.columns([1, 9])
with _back_col:
    if st.button("← Back", key="back_analytics"):
        st.switch_page("app.py")

st.title("📈 Analytics — StudyAI")

# Fetch all analytics data in parallel
overview_resp = api_get("/analytics/overview")
gaps_resp     = api_get("/analytics/gaps")
heatmap_resp  = api_get("/analytics/heatmap")

ov      = overview_resp.get("data", {})    if overview_resp else {}
gaps    = gaps_resp.get("data", [])        if gaps_resp     else []
heatmap = heatmap_resp.get("data", [])     if heatmap_resp  else []

# ── Metric Cards ──────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("📚 Materials",     ov.get("material_count", 0))
m2.metric("🔍 Concepts",      ov.get("concept_count", 0))
m3.metric("❓ Quizzes",       ov.get("quiz_count", 0))
m4.metric("📊 Avg Score",     f"{ov.get('avg_score', 0):.0f}%")
m5.metric("🔥 Streak",        f"{ov.get('study_streak_days', 0)}d")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Mastery Gauge + Activity Heatmap ───────────────────────────────────
col_gauge, col_heat = st.columns([4, 6], gap="large")

with col_gauge:
    st.markdown("### 🎯 Overall Mastery")
    mastery_pct = ov.get("overall_mastery", 0)
    fig_gauge = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = mastery_pct,
        number = {"suffix": "%", "font": {"color": "#1fb89a", "size": 36, "family": "Syne"}},
        gauge  = {
            "axis":  {"range": [0, 100], "tickcolor": "#7a7f9a", "tickfont": {"size": 11}},
            "bar":   {"color": "#1fb89a", "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 40],  "color": "rgba(239,68,68,0.15)"},
                {"range": [40, 70], "color": "rgba(232,160,32,0.15)"},
                {"range": [70, 100], "color": "rgba(34,197,94,0.15)"},
            ],
            "threshold": {"line": {"color": "#e8a020", "width": 3}, "value": 70},
        },
    ))
    fig_gauge.update_layout(
        template="plotly_dark", height=280,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=10),
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

with col_heat:
    st.markdown("### 🗓️ Study Rhythm (Last 30 Days)")
    if heatmap:
        from datetime import datetime
        # Format dates for display
        display_dates = [datetime.strptime(h["date"], "%Y-%m-%d").strftime("%d %b") for h in heatmap]
        counts        = [h["count"] for h in heatmap]

        fig_heat = go.Figure()
        
        # Add a smooth line with area fill
        fig_heat.add_trace(go.Scatter(
            x      = display_dates,
            y      = counts,
            mode   = 'lines+markers',
            name   = 'Activity',
            line   = dict(color='#1fb89a', width=3, shape='spline'), # Spline makes it smooth
            marker = dict(size=8, color='#1fb89a', symbol='circle'),
            fill   = 'tozeroy',
            fillcolor = 'rgba(31, 184, 154, 0.15)', # Elegant semi-transparent fill
            hovertemplate = "<b>%{x}</b><br>%{y} study events<extra></extra>"
        ))

        fig_heat.update_layout(
            template="plotly_dark", 
            height=280,
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis = dict(
                showgrid=False, 
                showline=True, 
                linecolor='#1e2135',
                dtick=5, # Show a label every 5 days to avoid clutter
            ),
            yaxis = dict(
                showgrid=True, 
                gridcolor='rgba(30, 33, 53, 0.5)', 
                zeroline=False,
                tickmode='linear',
                tick0=0,
                dtick=2 if max(counts + [1]) > 5 else 1
            ),
            margin=dict(l=0, r=0, t=10, b=30),
            showlegend=False
        )
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown("<p style='color:#7a7f9a;margin-top:60px;text-align:center'>No activity yet.</p>", unsafe_allow_html=True)

# ── Row 2: Concept Coverage ───────────────────────────────────────────────────
coverage_resp = api_get("/analytics/coverage")
cov_data = coverage_resp.get("data", {}) if coverage_resp else {}

if cov_data:
    st.markdown("<br>### 📊 Topic Coverage & Listing", unsafe_allow_html=True)
    c1, c2 = st.columns([5, 5], gap="large")
    
    with c1:
        st.markdown("#### 🗺️ Topic Coverage Map")
        topics = cov_data.get("topics", [])
        if not topics:
            st.info("Upload materials with standard academic terms to see topic grouping.")
        else:
            for t in topics:
                pct = t["coverage_pct"]
                color = "#1fb89a" if pct > 70 else "#e8a020" if pct > 40 else "#ef4444"
                st.markdown(f"""
                    <div style='margin-bottom:12px'>
                        <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
                            <span style='color:#e8e9f0;font-size:14px'>{t['topic']}</span>
                            <span style='color:{color};font-weight:bold'>{pct}%</span>
                        </div>
                        <div style='background:#1e2135;height:8px;border-radius:10px'>
                            <div style='background:{color};width:{pct}%;height:100%;border-radius:10px;
                                box-shadow:0 0 10px {color}44'></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("#### 🔗 Quick Overlap List")
        overlap = cov_data.get("overlap", [])
        if not overlap:
            st.markdown("<p style='color:#7a7f9a;text-align:center;margin-top:20px'>Upload more related materials to see concept intersections.</p>", unsafe_allow_html=True)
        else:
            for o in overlap:
                st.markdown(f"""
                    <div style='background:rgba(18,20,31,0.5);border:1px solid #1e2135;
                        border-radius:10px;padding:10px 14px;margin-bottom:8px'>
                        <div style='display:flex;justify-content:space-between;align-items:center'>
                            <span style='color:#1fb89a;font-weight:bold;font-size:14px'>{o['concept']}</span>
                            <span style='background:#1e2135;color:#7a7f9a;padding:2px 8px;border-radius:8px;font-size:11px'>
                                found in {o['count']} files
                            </span>
                        </div>
                        <p style='color:#7a7f9a;font-size:11px;margin:4px 0 0'>
                            📁 {", ".join(o['materials'][:2])} {"..." if len(o['materials']) > 2 else ""}
                        </p>
                    </div>""", unsafe_allow_html=True)

# ── Row 2.5: Concept Overlap (Bubble Chart) ───────────────────────────────────
overlap_resp = api_get("/analytics/overlap")
overlap_data = overlap_resp.get("data", {}) if overlap_resp else {}
concepts_overlap = overlap_data.get("overlapping_concepts", [])

if concepts_overlap:
    st.markdown("<br>### 🔗 Concept Overlap Across Materials", unsafe_allow_html=True)
    st.markdown("<p style='color:#7a7f9a;margin-bottom:20px'>Concepts that appear in multiple study materials. Bubble size indicates your current mastery.</p>", unsafe_allow_html=True)

    import pandas as pd
    df_overlap = pd.DataFrame([{
        "Concept":   c["concept_name"][:25],
        "Materials": c["material_count"],
        "Mastery":   round(c["avg_mastery"] * 100, 1),
        "Files":     "<br>".join([m["filename"][:30] for m in c["materials"][:3]]),
    } for c in concepts_overlap[:15]])

    fig_overlap = px.scatter(
        df_overlap,
        x         = "Concept",
        y         = "Materials",
        size      = "Mastery",
        color     = "Materials",
        hover_data= ["Files", "Mastery"],
        color_continuous_scale = [
            [0.0, "#1e2135"],
            [0.5, "#1fb89a"],
            [1.0, "#e8a020"],
        ],
        size_max  = 40,
        template  = "plotly_dark",
    )
    fig_overlap.update_layout(
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        font_color    = "white",
        height        = 400,
        showlegend    = False,
        margin=dict(l=20, r=20, t=10, b=50),
        xaxis = {
            "tickangle": -30,
            "tickfont":  {"size": 11},
            "showgrid": False
        },
        yaxis = {
            "title": "Number of Files",
            "showgrid": True,
            "gridcolor": "rgba(30,33,53,0.5)"
        }
    )
    st.plotly_chart(fig_overlap, use_container_width=True, config={"displayModeBar": False})

    # Summary insight
    most = overlap_data.get("most_connected", "")
    total = overlap_data.get("total_overlap_count", 0)
    if total > 0:
        st.info(f"🔗 **{total} concepts** appear in multiple materials. Most connected: **{most}**")
else:
    st.info("Upload 2+ materials with overlapping terms to see the connection map.")

# ── Row 3: Knowledge Gaps ────────────────────────────────────────────────────
st.markdown("<br>### 🔍 Knowledge Gaps", unsafe_allow_html=True)

if not gaps:
    st.markdown("""
        <div style='padding:32px;background:rgba(31,184,154,0.06);border-radius:20px;text-align:center;border:1px solid rgba(31,184,154,0.2)'>
            <h3 style='color:#1fb89a'>✨ No significant gaps detected!</h3>
            <p style='color:#7a7f9a'>Keep it up — review more materials to maintain mastery.</p>
        </div>""", unsafe_allow_html=True)
else:
    for group in gaps:
        mat_name  = group.get("material_name", "Unknown material")
        concepts  = group.get("concepts", [])
        avg_m     = sum(c["mastery_score"] for c in concepts) / max(len(concepts), 1)
        urgency   = "🔴 Urgent" if avg_m < 0.3 else "🟡 Review Soon"

        with st.expander(f"{urgency} — {mat_name} ({len(concepts)} weak concepts)"):
            # Horizontal bar chart
            names   = [c["name"] for c in concepts]
            scores  = [c["mastery_score"] * 100 for c in concepts]
            colors  = ["#ef4444" if s < 40 else "#e8a020" for s in scores]

            fig_bar = go.Figure(go.Bar(
                x=scores, y=names, orientation="h",
                marker_color=colors,
                text=[f"{s:.0f}%" for s in scores],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Mastery: %{x:.0f}%<extra></extra>",
            ))
            fig_bar.update_layout(
                template="plotly_dark", height=max(200, len(names) * 36),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(range=[0, 100], showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False),
                margin=dict(l=0, r=60, t=10, b=10),
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

            # Action items
            for c in concepts:
                action_color = "#ef4444" if c["mastery_score"] < 0.3 else "#e8a020"
                st.markdown(f"""
                    <div style='display:flex;justify-content:space-between;padding:8px 12px;
                        background:rgba(18,20,31,0.4);border-radius:8px;margin-bottom:6px'>
                        <span style='color:#e8e9f0'>{c['name']}</span>
                        <span style='color:{action_color};font-size:12px'>{c.get('action','Review')}</span>
                    </div>""", unsafe_allow_html=True)
