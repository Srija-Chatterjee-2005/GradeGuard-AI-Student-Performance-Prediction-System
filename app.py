import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_student_data, ENGINEERING_DEPARTMENTS, SUBJECT_GROUPS
from src.model_training import train_model
from src.prediction import make_input_row, predict_student
from src.ui_components import (
    load_premium_css,
    hero,
    kpi_card,
    insight_box,
    premium_divider,
    progress_bar,
    page_header,
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="GradeGuard AI",
    page_icon="🎓",
    layout="wide"
)

load_premium_css()


# ==========================================================
# DATA + MODEL LOADING
# ==========================================================

@st.cache_data
def get_data():
    return load_student_data()


@st.cache_resource
def get_model(df):
    return train_model(df)


df = get_data()
model, metrics = get_model(df)


# ==========================================================
# EXTRA DATA ENRICHMENT SAFETY
# ==========================================================

if "guardian_call_required" not in df.columns:
    df["guardian_call_required"] = np.where(
        (df["attendance_pct"] < 75) | (df["failures"] > 0) | (df["G2"] < 10),
        "Yes",
        "No"
    )

if "risk_segment" not in df.columns:
    df["risk_segment"] = np.where(
        df["attendance_pct"] < 60,
        "High Risk",
        np.where(df["attendance_pct"] < 75, "Medium Risk", "Low Risk")
    )

if "backlog_count" not in df.columns:
    df["backlog_count"] = df["failures"]


# ==========================================================
# UI HELPERS
# ==========================================================

def apply_plot_style(fig, height=430):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
    )
    return fig


def safe_dataframe_message():
    if filtered_df.empty:
        st.warning("No data available for the selected filters. Adjust filters from the sidebar.")
        return False
    return True


def build_priority_table(data):
    temp = data.copy()
    temp["risk_priority_score"] = (
        (100 - temp["attendance_pct"]) * 0.45
        + (20 - temp["G3"]) * 2.2
        + temp["failures"] * 12
    )
    temp["risk_priority_score"] = temp["risk_priority_score"].round(1)
    return temp.sort_values(by="risk_priority_score", ascending=False)


def premium_metric(title, value, accent="#22d3ee"):
    st.markdown(f"""
    <div style="
        padding:24px;
        border-radius:26px;
        background:
            radial-gradient(circle at top right, {accent}33, transparent 34%),
            linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.72));
        border:1px solid rgba(255,255,255,0.13);
        box-shadow:0 20px 65px rgba(0,0,0,0.40), 0 0 28px {accent}22;
        min-height:120px;
        margin-bottom:14px;
    ">
        <div style="color:#cbd5e1; font-size:13px; letter-spacing:0.3px;">{title}</div>
        <div style="font-size:34px; font-weight:900; color:white; margin-top:8px;">{value}</div>
        <div style="height:4px; width:58px; border-radius:999px; background:{accent}; margin-top:12px;"></div>
    </div>
    """, unsafe_allow_html=True)


def chart_card(fig):
    st.markdown("""
    <div style="
        padding:18px;
        border-radius:28px;
        background:rgba(15,23,42,0.72);
        border:1px solid rgba(255,255,255,0.10);
        box-shadow:0 22px 70px rgba(0,0,0,0.35);
        margin-bottom:18px;
    ">
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def auto_fix_uploaded_csv(batch_df):
    fixed_df = batch_df.copy()

    default_values = {
        "department": "CSE",
        "core_subject": "Programming",
        "semester": "Sem 3",
        "admission_type": "Entrance",
        "hostel_status": "Day Scholar",
        "studytime": 2,
        "failures": 0,
        "absences": 0,
        "G1": 10,
        "G2": 10,
    }

    for col, default in default_values.items():
        if col not in fixed_df.columns:
            fixed_df[col] = default

    numeric_cols = ["absences", "G1", "G2", "studytime", "failures"]

    for col in numeric_cols:
        fixed_df[col] = pd.to_numeric(fixed_df[col], errors="coerce")
        fixed_df[col] = fixed_df[col].fillna(default_values[col])

    fixed_df["absences"] = fixed_df["absences"].clip(0, 80).astype(int)
    fixed_df["G1"] = fixed_df["G1"].clip(0, 20).astype(int)
    fixed_df["G2"] = fixed_df["G2"].clip(0, 20).astype(int)
    fixed_df["studytime"] = fixed_df["studytime"].clip(1, 4).astype(int)
    fixed_df["failures"] = fixed_df["failures"].clip(0, 3).astype(int)

    fixed_df["department"] = fixed_df["department"].fillna("CSE").astype(str)
    fixed_df["core_subject"] = fixed_df["core_subject"].fillna("Programming").astype(str)
    fixed_df["semester"] = fixed_df["semester"].fillna("Sem 3").astype(str)
    fixed_df["admission_type"] = fixed_df["admission_type"].fillna("Entrance").astype(str)
    fixed_df["hostel_status"] = fixed_df["hostel_status"].fillna("Day Scholar").astype(str)

    return fixed_df


# ==========================================================
# HERO SECTION
# ==========================================================

hero()

st.markdown("""
<h3 style="text-align:center; color:#cbd5e1; font-weight:500; margin-top:18px;">
A next-generation academic intelligence system powered by machine learning, attendance governance, and intervention analytics.
</h3>
""", unsafe_allow_html=True)

premium_divider()


# ==========================================================
# SIDEBAR NAVIGATION + FILTERS
# ==========================================================

st.sidebar.markdown("## 🚀 GradeGuard Control Panel")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Command Center",
        "🔮 Live Predictor",
        "📊 Department Analytics",
        "📈 Performance Intelligence",
        "📂 CSV Studio",
        "🧠 Model Insights",
        "📌 Intervention Playbook"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🎛 Smart Filters")

selected_department = st.sidebar.multiselect(
    "Engineering Department",
    sorted(df["department"].unique()),
    default=list(sorted(df["department"].unique()))
)

selected_zone = st.sidebar.multiselect(
    "Attendance Zone",
    sorted(df["attendance_zone"].unique()),
    default=list(sorted(df["attendance_zone"].unique()))
)

selected_risk = st.sidebar.multiselect(
    "Risk Segment",
    sorted(df["risk_segment"].unique()),
    default=list(sorted(df["risk_segment"].unique()))
)

selected_semester = st.sidebar.multiselect(
    "Semester",
    sorted(df["semester"].unique()),
    default=list(sorted(df["semester"].unique()))
)

selected_subject = st.sidebar.multiselect(
    "Core Subject",
    sorted(df["core_subject"].unique()),
    default=list(sorted(df["core_subject"].unique()))
)

score_range = st.sidebar.slider(
    "Final Score Range",
    0,
    20,
    (0, 20)
)

attendance_range = st.sidebar.slider(
    "Attendance Range",
    0,
    100,
    (0, 100)
)

show_only_guardian = st.sidebar.checkbox("Show only Guardian Call cases", value=False)


# ==========================================================
# FILTERED DATA
# ==========================================================

filtered_df = df[
    (df["department"].isin(selected_department)) &
    (df["attendance_zone"].isin(selected_zone)) &
    (df["risk_segment"].isin(selected_risk)) &
    (df["semester"].isin(selected_semester)) &
    (df["core_subject"].isin(selected_subject)) &
    (df["G3"].between(score_range[0], score_range[1])) &
    (df["attendance_pct"].between(attendance_range[0], attendance_range[1]))
].copy()

if show_only_guardian:
    filtered_df = filtered_df[filtered_df["guardian_call_required"] == "Yes"].copy()


# ==========================================================
# TOP KPI STRIP
# ==========================================================

total_students = len(filtered_df)
eligible_students = (filtered_df["attendance_zone"] == "Eligible").sum()
second_chance_students = (filtered_df["attendance_zone"] == "Second Chance").sum()
defaulter_students = (filtered_df["attendance_zone"] == "Defaulter").sum()
pass_rate = filtered_df["passed"].mean() * 100 if len(filtered_df) else 0
guardian_calls = (filtered_df["guardian_call_required"] == "Yes").sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    premium_metric("Students", total_students, "#22d3ee")
with k2:
    premium_metric("Eligible", eligible_students, "#10b981")
with k3:
    premium_metric("Second Chance", second_chance_students, "#facc15")
with k4:
    premium_metric("Defaulters", defaulter_students, "#a78bfa")
with k5:
    premium_metric("Pass Rate", f"{pass_rate:.1f}%", "#8b5cf6")
with k6:
    premium_metric("Guardian Calls", guardian_calls, "#f472b6")

premium_divider()


# ==========================================================
# PAGE 1: COMMAND CENTER
# ==========================================================

if page == "🏠 Command Center":

    page_header(
        "🏠 Campus Academic Command Center",
        "A central academic intelligence dashboard for attendance compliance, risk segmentation, and intervention planning.",
        "rose"
    )

    if safe_dataframe_message():

        a1, a2 = st.columns(2)

        with a1:
            att_counts = filtered_df["attendance_zone"].value_counts().reset_index()
            att_counts.columns = ["Attendance Zone", "Students"]

            fig = px.bar(
                att_counts,
                x="Attendance Zone",
                y="Students",
                color="Attendance Zone",
                title="75% Attendance Compliance System",
                color_discrete_sequence=["#22d3ee", "#facc15", "#a78bfa"]
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)

        with a2:
            risk_counts = filtered_df["risk_segment"].value_counts().reset_index()
            risk_counts.columns = ["Risk Segment", "Students"]

            fig = px.pie(
                risk_counts,
                names="Risk Segment",
                values="Students",
                hole=0.52,
                title="Academic Risk Segmentation",
                color_discrete_sequence=["#22d3ee", "#facc15", "#c084fc"]
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)

        x1, x2, x3 = st.columns(3)

        with x1:
            insight_box(
                "Second Chance Policy",
                "Students between 60% and 75% attendance require guardian approval and valid reason verification."
            )

        with x2:
            insight_box(
                "Backlog Intelligence",
                "Students with previous failures are automatically placed under academic monitoring."
            )

        with x3:
            insight_box(
                "Department View",
                "Department filters help compare CSE, ECE, AI & ML, CSDS, ME, Civil, EE, IT and other streams."
            )

        premium_divider()

        st.markdown("## 🏆 Department Performance Leaderboard")

        leaderboard = (
            filtered_df.groupby("department")
            .agg(
                students=("passed", "count"),
                pass_rate=("passed", "mean"),
                avg_attendance=("attendance_pct", "mean"),
                avg_score=("G3", "mean"),
                high_risk=("risk_segment", lambda x: (x == "High Risk").sum()),
                guardian_cases=("guardian_call_required", lambda x: (x == "Yes").sum())
            )
            .reset_index()
        )

        leaderboard["pass_rate"] = (leaderboard["pass_rate"] * 100).round(1)
        leaderboard["avg_attendance"] = leaderboard["avg_attendance"].round(1)
        leaderboard["avg_score"] = leaderboard["avg_score"].round(1)
        leaderboard = leaderboard.sort_values(by=["pass_rate", "avg_attendance"], ascending=False)

        st.dataframe(leaderboard, use_container_width=True, hide_index=True)

        l1, l2 = st.columns(2)

        with l1:
            fig = px.bar(
                leaderboard,
                x="department",
                y="pass_rate",
                color="department",
                title="Department Leaderboard by Pass Rate",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)

        with l2:
            fig = px.bar(
                leaderboard,
                x="department",
                y="guardian_cases",
                color="department",
                title="Guardian Call Cases by Department",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)

        premium_divider()

        st.markdown("## ⚠️ Top At-Risk Students")

        top_risk = build_priority_table(filtered_df).head(10)

        display_cols = [
            "department", "semester", "core_subject", "attendance_pct",
            "attendance_zone", "G1", "G2", "G3", "failures",
            "risk_segment", "guardian_call_required", "risk_priority_score"
        ]

        st.dataframe(top_risk[display_cols], use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Download Top Risk Students",
            top_risk[display_cols].to_csv(index=False),
            "top_at_risk_students.csv",
            "text/csv"
        )

        premium_divider()

        st.markdown("## 🏅 Student Ranking System")

        ranking_df = filtered_df.copy()
        ranking_df["student_rank_score"] = (
            ranking_df["G3"] * 3
            + ranking_df["attendance_pct"] * 0.4
            - ranking_df["failures"] * 8
        )
        ranking_df["student_rank_score"] = ranking_df["student_rank_score"].round(1)
        ranking_df = ranking_df.sort_values(by="student_rank_score", ascending=False)

        top_students = ranking_df.head(10)
        weak_students = ranking_df.tail(10)

        r1, r2 = st.columns(2)

        with r1:
            st.markdown("### 🏆 Top 10 Performers")
            st.dataframe(
                top_students[
                    ["department", "semester", "core_subject", "attendance_pct", "G1", "G2", "G3", "student_rank_score"]
                ],
                use_container_width=True,
                hide_index=True
            )

        with r2:
            st.markdown("### ⚠️ Bottom 10 Students")
            st.dataframe(
                weak_students[
                    ["department", "semester", "core_subject", "attendance_pct", "G1", "G2", "G3", "student_rank_score"]
                ],
                use_container_width=True,
                hide_index=True
            )


# ==========================================================
# PAGE 2: LIVE PREDICTOR
# ==========================================================

elif page == "🔮 Live Predictor":

    page_header(
        "🔮 Real-Time Student Prediction Engine",
        "Move the sliders and instantly update prediction, risk score, guardian call status, and interventions.",
        "sunset"
    )

    p1, p2, p3 = st.columns(3)

    with p1:
        absences = st.slider("Absences", 0, 80, 25)
        g1 = st.slider("Internal Marks G1", 0, 20, 9)

    with p2:
        g2 = st.slider("Midterm Marks G2", 0, 20, 10)
        studytime = st.selectbox("Study Time Level", [1, 2, 3, 4], index=1)

    with p3:
        failures = st.selectbox("Previous Backlogs / Failures", [0, 1, 2, 3], index=0)
        department = st.selectbox("Engineering Department", ENGINEERING_DEPARTMENTS)
        core_subject = st.selectbox("Core Subject", SUBJECT_GROUPS)
        semester = st.selectbox("Semester", ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"])
        admission_type = st.selectbox("Admission Type", ["Merit", "Entrance", "Management", "Lateral Entry"])
        hostel_status = st.selectbox("Student Type", ["Hosteller", "Day Scholar"])

    row = make_input_row(
        absences, g1, g2, studytime, failures, department,
        core_subject, semester, admission_type, hostel_status
    )

    pred = predict_student(model, row)

    m1, m2, m3, m4, m5, m6 = st.columns(6)

    with m1:
        premium_metric("Prediction", pred["prediction"], "#22d3ee")
    with m2:
        premium_metric("Risk", pred["risk"], "#ec4899")
    with m3:
        premium_metric("Risk Score", f'{pred["risk_score"]}/100', "#8b5cf6")
    with m4:
        premium_metric("Badge", pred["risk_badge"], "#facc15")
    with m5:
        premium_metric("Attendance", f'{pred["attendance_pct"]}%', "#10b981")
    with m6:
        premium_metric("Guardian Call", pred["guardian_call_required"], "#c084fc")

    premium_divider()

    st.markdown("## 🚨 Early Warning System")

    early_warnings = []

    if pred["attendance_pct"] < 60:
        early_warnings.append("Student is already in defaulter zone (attendance < 60%).")
    elif pred["attendance_pct"] < 75:
        early_warnings.append("Student falls under second-chance attendance policy (60–75%).")

    if row["G2"] < 10:
        early_warnings.append("Midterm marks are below passing level.")

    if row["G2"] < row["G1"]:
        early_warnings.append("Performance trend is declining from G1 to G2.")

    if row["failures"] > 0:
        early_warnings.append("Previous backlog/failure history increases risk.")

    if not early_warnings:
        early_warnings.append("No critical warning detected. Student is stable.")

    for warning in early_warnings:
        st.markdown(f"""
        <div style="
            padding:14px;
            margin-bottom:10px;
            border-radius:18px;
            background:rgba(15,23,42,0.85);
            border-left:5px solid #facc15;
            color:#e2e8f0;
            box-shadow:0 12px 30px rgba(0,0,0,0.25);
        ">
            🚨 {warning}
        </div>
        """, unsafe_allow_html=True)

    premium_divider()

    g1c, g2c = st.columns(2)

    with g1c:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred["pass_prob"] * 100,
            title={"text": "🚀 Pass Confidence"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#22d3ee"},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 2,
                "bordercolor": "#22d3ee",
                "steps": [
                    {"range": [0, 50], "color": "rgba(168,85,247,0.20)"},
                    {"range": [50, 75], "color": "rgba(250,204,21,0.20)"},
                    {"range": [75, 100], "color": "rgba(34,211,238,0.28)"}
                ],
            }
        ))
        fig.update_layout(height=330, paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        chart_card(fig)

    with g2c:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred["risk_score"],
            title={"text": "⚠️ Risk Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#c084fc"},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 2,
                "bordercolor": "#c084fc",
                "steps": [
                    {"range": [0, 40], "color": "rgba(34,197,94,0.18)"},
                    {"range": [40, 70], "color": "rgba(250,204,21,0.18)"},
                    {"range": [70, 100], "color": "rgba(192,132,252,0.28)"}
                ],
            }
        ))
        fig.update_layout(height=330, paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        chart_card(fig)

    premium_divider()

    st.markdown("### 🎯 Risk & Confidence Monitor")
    progress_bar("Pass Confidence", pred["pass_prob"] * 100)
    progress_bar("Fail Probability", pred["fail_prob"] * 100)
    progress_bar("Risk Score", pred["risk_score"])

    premium_divider()

    st.markdown("### ⚡ AI Insight Engine")

    for insight in pred["ai_insights"]:
        color = "#22d3ee"

        if "defaulter" in insight.lower():
            color = "#c084fc"
        elif "low" in insight.lower():
            color = "#facc15"
        elif "immediate" in insight.lower():
            color = "#a78bfa"

        st.markdown(f"""
        <div style="
            padding:14px;
            margin-bottom:10px;
            border-radius:18px;
            background: rgba(15,23,42,0.85);
            border-left: 5px solid {color};
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            font-size:15px;
            color:#e2e8f0;
        ">
            ⚡ {insight}
        </div>
        """, unsafe_allow_html=True)

    premium_divider()

    st.markdown("## 🧠 AI Explanation Panel")

    explanation_text = f"""
    ### Decision Breakdown

    - Prediction: **{pred["prediction"]}**
    - Risk Level: **{pred["risk"]}**
    - Risk Score: **{pred["risk_score"]}/100**

    ### Key Factors

    - Attendance: **{pred["attendance_pct"]}%**
    - Attendance Zone: **{pred["attendance_zone"]}**
    - G1: **{row["G1"]}**
    - G2: **{row["G2"]}**
    - Failures: **{row["failures"]}**

    ### Model Confidence

    - Pass Probability: **{pred["pass_prob"] * 100:.1f}%**
    - Fail Probability: **{pred["fail_prob"] * 100:.1f}%**

    ### Action

    - Guardian Call: **{pred["guardian_call_required"]}**
    - Final Status: **{pred["final_status"]}**
    """

    st.markdown(explanation_text)

    premium_divider()

    st.markdown("### 🧠 Why this prediction?")
    for reason in pred["reasons"]:
        insight_box("Reason", reason)

    st.markdown("### 🚀 Recommended Academic Actions")
    for action in pred["interventions"]:
        insight_box("Action", action)

    premium_divider()

    st.markdown("## 🔄 What-If Simulator")
    st.caption("Test how improving attendance, marks, or backlog status changes the student outcome.")

    sim1, sim2, sim3 = st.columns(3)

    with sim1:
        new_attendance = st.slider(
            "Improve Attendance (%)",
            int(pred["attendance_pct"]),
            100,
            int(pred["attendance_pct"])
        )

    with sim2:
        new_g2 = st.slider(
            "Improve Midterm Marks (G2)",
            0,
            20,
            int(row["G2"])
        )

    with sim3:
        current_failures = int(row["failures"])
        if current_failures > 0:
            new_failures = st.slider(
                "Reduce Backlogs",
                0,
                current_failures,
                current_failures
            )
        else:
            st.info("No existing backlogs to reduce.")
            new_failures = 0

    new_absences = max(0, 100 - new_attendance)

    new_row = make_input_row(
        new_absences,
        row["G1"],
        new_g2,
        row["studytime"],
        new_failures,
        row["department"],
        row["core_subject"],
        row["semester"],
        row["admission_type"],
        row["hostel_status"]
    )

    new_pred = predict_student(model, new_row)

    s1, s2 = st.columns(2)

    with s1:
        st.markdown("### Current Status")
        st.metric("Prediction", pred["prediction"])
        st.metric("Risk Score", f'{pred["risk_score"]}/100')
        st.metric("Status", pred["final_status"])

    with s2:
        st.markdown("### Improved Scenario")
        st.metric("Prediction", new_pred["prediction"])
        st.metric("Risk Score", f'{new_pred["risk_score"]}/100')
        st.metric("Status", new_pred["final_status"])

    if pred["prediction"] != new_pred["prediction"]:
        st.success("🎉 Improvement detected! Student outcome changed after adjustments.")
    elif new_pred["risk_score"] < pred["risk_score"]:
        st.success("✅ Risk score improved. Student is moving in the right direction.")
    else:
        st.warning("⚠️ No major improvement yet. Try improving attendance or marks further.")

    report_df = pd.DataFrame([{
        "prediction": pred["prediction"],
        "risk": pred["risk"],
        "risk_score": pred["risk_score"],
        "risk_badge": pred["risk_badge"],
        "attendance_pct": pred["attendance_pct"],
        "final_status": pred["final_status"],
        "guardian_call_required": pred["guardian_call_required"],
        "pass_probability": round(pred["pass_prob"] * 100, 1),
        "fail_probability": round(pred["fail_prob"] * 100, 1),
        "department": department,
        "core_subject": core_subject,
        "semester": semester
    }])

    st.download_button(
        "⬇️ Download This Student Report",
        report_df.to_csv(index=False),
        "student_risk_report.csv",
        "text/csv"
    )


# ==========================================================
# PAGE 3: DEPARTMENT ANALYTICS
# ==========================================================

elif page == "📊 Department Analytics":

    page_header(
        "📊 Department-Level Academic Analytics",
        "Compare performance, risk composition, guardian call burden, and pass rate across engineering departments.",
        "mint"
    )

    if safe_dataframe_message():

        d1, d2 = st.columns(2)

        with d1:
            dept_pass = filtered_df.groupby("department")["passed"].mean().reset_index()
            dept_pass["Pass Rate"] = dept_pass["passed"] * 100

            fig = px.bar(
                dept_pass,
                x="department",
                y="Pass Rate",
                color="department",
                title="Department-wise Pass Rate",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig = apply_plot_style(fig, 450)
            chart_card(fig)

        with d2:
            dept_risk = filtered_df.groupby(["department", "risk_segment"]).size().reset_index(name="Students")

            fig = px.bar(
                dept_risk,
                x="department",
                y="Students",
                color="risk_segment",
                barmode="stack",
                title="Department-wise Risk Composition",
                color_discrete_sequence=["#22d3ee", "#facc15", "#c084fc"]
            )
            fig = apply_plot_style(fig, 450)
            chart_card(fig)

        d3, d4 = st.columns(2)

        with d3:
            fig = px.sunburst(
                filtered_df,
                path=["department", "attendance_zone", "risk_segment"],
                values="passed",
                title="Department → Attendance → Risk Drilldown",
                color="attendance_zone",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig = apply_plot_style(fig, 500)
            chart_card(fig)

        with d4:
            fig = px.treemap(
                filtered_df,
                path=["semester", "department", "risk_segment"],
                values="G3",
                title="Semester & Department Performance Map",
                color="G3",
                color_continuous_scale="Turbo"
            )
            fig = apply_plot_style(fig, 500)
            chart_card(fig)

        premium_divider()

        st.markdown("## 🧩 Department Comparison Matrix")

        dept_matrix = filtered_df.groupby("department").agg(
            students=("passed", "count"),
            pass_rate=("passed", "mean"),
            avg_score=("G3", "mean"),
            avg_attendance=("attendance_pct", "mean"),
            backlogs=("failures", "sum")
        ).reset_index()

        dept_matrix["pass_rate"] = (dept_matrix["pass_rate"] * 100).round(1)
        dept_matrix["avg_score"] = dept_matrix["avg_score"].round(1)
        dept_matrix["avg_attendance"] = dept_matrix["avg_attendance"].round(1)

        st.dataframe(dept_matrix, use_container_width=True, hide_index=True)

        premium_divider()

        page_header(
            "👤 Advanced Student Profile Intelligence",
            "Deep academic profile, risk reasoning, score movement, and intervention intelligence.",
            "sunset"
        )

        student_index = st.selectbox(
            "Select Student Record",
            filtered_df.index,
            key="advanced_profile"
        )

        student = filtered_df.loc[student_index]

        profile_row = make_input_row(
            int(student["absences"]),
            int(student["G1"]),
            int(student["G2"]),
            int(student["studytime"]),
            int(student["failures"]),
            str(student["department"]),
            str(student["core_subject"]),
            str(student["semester"]),
            str(student["admission_type"]),
            str(student["hostel_status"])
        )

        profile_pred = predict_student(model, profile_row)

        p1, p2, p3, p4 = st.columns(4)

        with p1:
            premium_metric("Department", student["department"], "#ec4899")
        with p2:
            premium_metric("Attendance", f"{student['attendance_pct']}%", "#22d3ee")
        with p3:
            premium_metric("Risk Score", f"{profile_pred['risk_score']}/100", "#8b5cf6")
        with p4:
            premium_metric("Guardian Call", profile_pred["guardian_call_required"], "#facc15")

        s1, s2 = st.columns(2)

        with s1:
            score_trend = pd.DataFrame({
                "Assessment": ["G1 Internal", "G2 Midterm", "G3 Final"],
                "Score": [student["G1"], student["G2"], student["G3"]]
            })

            fig = px.line(
                score_trend,
                x="Assessment",
                y="Score",
                markers=True,
                title="Student Score Movement",
                color_discrete_sequence=["#ec4899"]
            )
            fig.update_traces(line=dict(width=5), marker=dict(size=12))
            fig = apply_plot_style(fig, 420)
            chart_card(fig)

        with s2:
            profile_summary = pd.DataFrame({
                "Signal": [
                    "Pass Probability",
                    "Fail Probability",
                    "Risk Score",
                    "Attendance"
                ],
                "Value": [
                    profile_pred["pass_prob"] * 100,
                    profile_pred["fail_prob"] * 100,
                    profile_pred["risk_score"],
                    student["attendance_pct"]
                ]
            })

            fig = px.bar(
                profile_summary,
                x="Signal",
                y="Value",
                color="Signal",
                title="Student Risk Signal Breakdown",
                color_discrete_sequence=[
                    "#22d3ee",
                    "#8b5cf6",
                    "#ec4899",
                    "#facc15"
                ]
            )
            fig = apply_plot_style(fig, 420)
            chart_card(fig)

        st.markdown("### 🧠 Profile-Based Intervention Notes")
        for action in profile_pred["interventions"]:
            insight_box("Recommended Action", action)

        premium_divider()

        page_header(
            "🔥 Advanced Risk Heatmap",
            "Identify high-risk academic zones across departments and semesters.",
            "galaxy"
        )

        heatmap_score_df = (
            filtered_df
            .groupby(["department", "semester"])
            .agg(
                high_risk_count=("risk_segment", lambda x: (x == "High Risk").sum()),
                avg_attendance=("attendance_pct", "mean"),
                avg_score=("G3", "mean")
            )
            .reset_index()
        )

        heatmap_score_df["risk_intensity"] = (
            heatmap_score_df["high_risk_count"] * 12
            + (100 - heatmap_score_df["avg_attendance"]) * 0.4
            + (20 - heatmap_score_df["avg_score"]) * 1.5
        )

        risk_pivot = heatmap_score_df.pivot(
            index="department",
            columns="semester",
            values="risk_intensity"
        ).fillna(0)

        fig = px.imshow(
            risk_pivot,
            text_auto=True,
            color_continuous_scale="Plasma",
            title="Department vs Semester Risk Intensity"
        )
        fig = apply_plot_style(fig, 560)
        chart_card(fig)

        premium_divider()

        page_header(
            "🏆 Department Benchmarking Engine",
            "Compare academic strength, pass rate, attendance, and intervention pressure.",
            "mint"
        )

        benchmark = (
            filtered_df
            .groupby("department")
            .agg(
                students=("passed", "count"),
                pass_rate=("passed", "mean"),
                avg_attendance=("attendance_pct", "mean"),
                avg_score=("G3", "mean"),
                backlog_load=("failures", "sum"),
                guardian_cases=("guardian_call_required", lambda x: (x == "Yes").sum())
            )
            .reset_index()
        )

        benchmark["pass_rate"] = (benchmark["pass_rate"] * 100).round(1)
        benchmark["avg_attendance"] = benchmark["avg_attendance"].round(1)
        benchmark["avg_score"] = benchmark["avg_score"].round(1)

        benchmark["department_health_score"] = (
            benchmark["pass_rate"] * 0.45
            + benchmark["avg_attendance"] * 0.35
            + benchmark["avg_score"] * 2
            - benchmark["backlog_load"] * 1.5
            - benchmark["guardian_cases"] * 1.2
        ).round(1)

        benchmark = benchmark.sort_values("department_health_score", ascending=False)

        st.dataframe(benchmark, use_container_width=True, hide_index=True)

        fig = px.bar(
            benchmark,
            x="department",
            y="department_health_score",
            color="department",
            title="Department Health Score Ranking",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig = apply_plot_style(fig, 460)
        chart_card(fig)

        premium_divider()

        page_header(
            "📌 Intervention Scoring Matrix",
            "Prioritize students requiring urgent academic intervention.",
            "gold"
        )

        intervention_df = filtered_df.copy()

        intervention_df["intervention_score"] = (
            (100 - intervention_df["attendance_pct"]) * 0.35
            + (20 - intervention_df["G3"]) * 2
            + intervention_df["failures"] * 10
            + np.where(
                intervention_df["guardian_call_required"] == "Yes",
                12,
                0
            )
        ).round(1)

        intervention_df["intervention_priority"] = np.where(
            intervention_df["intervention_score"] >= 70,
            "Critical",
            np.where(
                intervention_df["intervention_score"] >= 40,
                "High",
                np.where(
                    intervention_df["intervention_score"] >= 20,
                    "Moderate",
                    "Low"
                )
            )
        )

        priority_counts = intervention_df["intervention_priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Students"]

        c1, c2 = st.columns(2)

        with c1:
            st.dataframe(
                intervention_df[
                    [
                        "department",
                        "semester",
                        "core_subject",
                        "attendance_pct",
                        "G3",
                        "failures",
                        "guardian_call_required",
                        "intervention_score",
                        "intervention_priority"
                    ]
                ].sort_values("intervention_score", ascending=False).head(15),
                use_container_width=True,
                hide_index=True
            )

        with c2:
            fig = px.pie(
                priority_counts,
                names="Priority",
                values="Students",
                hole=0.45,
                title="Intervention Priority Distribution",
                color_discrete_sequence=[
                    "#ec4899",
                    "#8b5cf6",
                    "#facc15",
                    "#22d3ee"
                ]
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)


# ==========================================================
# PAGE 4: PERFORMANCE INTELLIGENCE
# ==========================================================

elif page == "📈 Performance Intelligence":

    page_header(
        "📈 Performance Intelligence Dashboard",
        "Analyze academic drivers such as attendance, study time, score movement, subject, backlog, and risk segment.",
        "gold"
    )

    if safe_dataframe_message():

        a1, a2 = st.columns(2)

        with a1:
            fig = px.scatter(
                filtered_df,
                x="attendance_pct",
                y="G3",
                color="department",
                size="studytime",
                title="Attendance vs Final Score",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)

        with a2:
            fig = px.box(
                filtered_df,
                x="studytime",
                y="G3",
                color="studytime",
                title="Study Time Impact on Final Score",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)

        b1, b2 = st.columns(2)

        with b1:
            fig = px.violin(
                filtered_df,
                x="risk_segment",
                y="G3",
                color="risk_segment",
                box=True,
                title="Score Spread by Risk Segment",
                color_discrete_sequence=["#22d3ee", "#facc15", "#c084fc"]
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)

        with b2:
            corr = filtered_df[
                [
                    "G1",
                    "G2",
                    "G3",
                    "absences",
                    "attendance_pct",
                    "studytime",
                    "failures",
                    "backlog_count"
                ]
            ].corr()

            fig = px.imshow(
                corr,
                text_auto=True,
                title="Academic Signal Correlation Heatmap",
                color_continuous_scale="Turbo"
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)

        c1, c2 = st.columns(2)

        with c1:
            subject_perf = filtered_df.groupby("core_subject")["G3"].mean().reset_index()
            subject_perf["G3"] = subject_perf["G3"].round(1)

            fig = px.bar(
                subject_perf,
                x="core_subject",
                y="G3",
                color="core_subject",
                title="Core Subject Average Final Score",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)

        with c2:
            fig = px.histogram(
                filtered_df,
                x="G3",
                color="attendance_zone",
                title="Final Score Distribution by Attendance Zone",
                color_discrete_sequence=["#22d3ee", "#facc15", "#c084fc"]
            )
            fig = apply_plot_style(fig, 430)
            chart_card(fig)


# ==========================================================
# PAGE 5: CSV STUDIO
# ==========================================================

elif page == "📂 CSV Studio":

    page_header(
        "📂 CSV Studio",
        "Upload a real student CSV, generate instant ML predictions, visualize risk, and download results.",
        "galaxy"
    )

    sample = pd.DataFrame({
        "absences": [30, 10, 50, 20, 5, 45],
        "G1": [8, 12, 5, 10, 15, 6],
        "G2": [9, 14, 6, 11, 16, 7],
        "studytime": [2, 3, 1, 2, 4, 1],
        "failures": [0, 0, 1, 0, 0, 2],
        "department": ["CSE", "ECE", "IT", "ME", "AI & ML", "Civil"],
        "core_subject": ["Programming", "Electronics", "DBMS", "Mechanics", "Machine Learning", "Thermodynamics"],
        "semester": ["Sem 3", "Sem 4", "Sem 2", "Sem 5", "Sem 6", "Sem 3"],
        "admission_type": ["Entrance", "Merit", "Management", "Entrance", "Merit", "Lateral Entry"],
        "hostel_status": ["Day Scholar", "Hosteller", "Day Scholar", "Hosteller", "Day Scholar", "Hosteller"]
    })

    st.download_button(
        "⬇️ Download Sample CSV Format",
        sample.to_csv(index=False),
        "gradeguard_sample_students.csv",
        "text/csv"
    )

    st.download_button(
        "⬇️ Download Real Processed Dataset",
        df.to_csv(index=False),
        "processed_students_real_dataset.csv",
        "text/csv"
    )

    uploaded = st.file_uploader("Upload Student CSV", type=["csv"])

    required_cols = [
        "absences",
        "G1",
        "G2",
        "studytime",
        "failures",
        "department",
        "core_subject",
        "semester",
        "admission_type",
        "hostel_status"
    ]

    if uploaded is not None:
        batch_df = pd.read_csv(uploaded)

        original_columns = list(batch_df.columns)
        batch_df = auto_fix_uploaded_csv(batch_df)

        added_columns = [col for col in required_cols if col not in original_columns]

        if added_columns:
            st.info(f"Auto-fixed missing columns: {added_columns}")

        st.markdown("### 🔍 Uploaded CSV Preview")
        st.dataframe(batch_df.head(20), use_container_width=True)

        results = []

        for _, row_data in batch_df.iterrows():
            row = make_input_row(
                int(row_data["absences"]),
                int(row_data["G1"]),
                int(row_data["G2"]),
                int(row_data["studytime"]),
                int(row_data["failures"]),
                str(row_data["department"]),
                str(row_data["core_subject"]),
                str(row_data["semester"]),
                str(row_data["admission_type"]),
                str(row_data["hostel_status"])
            )

            pred = predict_student(model, row)

            results.append({
                "department": row_data["department"],
                "core_subject": row_data["core_subject"],
                "semester": row_data["semester"],
                "prediction": pred["prediction"],
                "risk": pred["risk"],
                "risk_score": pred["risk_score"],
                "risk_badge": pred["risk_badge"],
                "attendance_pct": pred["attendance_pct"],
                "attendance_zone": pred["attendance_zone"],
                "final_status": pred["final_status"],
                "guardian_call_required": pred["guardian_call_required"],
                "pass_probability": round(pred["pass_prob"] * 100, 1),
                "fail_probability": round(pred["fail_prob"] * 100, 1)
            })

        result_df = pd.DataFrame(results)

        st.success("CSV processed successfully. Predictions generated instantly.")

        st.markdown("### 📊 Prediction Result Table")
        st.dataframe(result_df, use_container_width=True)

        st.download_button(
            "⬇️ Download Prediction Results",
            result_df.to_csv(index=False),
            "gradeguard_prediction_results.csv",
            "text/csv"
        )

        u1, u2 = st.columns(2)

        with u1:
            fig = px.histogram(
                result_df,
                x="risk",
                color="risk",
                title="Uploaded Batch Risk Distribution",
                color_discrete_sequence=["#22d3ee", "#facc15", "#c084fc"]
            )
            fig = apply_plot_style(fig, 420)
            chart_card(fig)

        with u2:
            fig = px.bar(
                result_df,
                x="department",
                y="pass_probability",
                color="prediction",
                title="Batch Pass Probability by Department",
                color_discrete_sequence=["#22d3ee", "#c084fc"]
            )
            fig = apply_plot_style(fig, 420)
            chart_card(fig)


# ==========================================================
# PAGE 6: MODEL INSIGHTS
# ==========================================================

elif page == "🧠 Model Insights":

    page_header(
        "🧠 Model & Explainability",
        "Model quality, classification metrics, project logic, and interview-ready explanation.",
        "ocean"
    )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Model", "Random Forest")
    m2.metric("Accuracy", f"{metrics['accuracy']:.2f}")
    m3.metric("F1 Score", f"{metrics['f1']:.2f}")
    m4.metric("ROC-AUC", f"{metrics['roc_auc']:.2f}")

    premium_divider()

    st.markdown("""
    ### What this system does

    GradeGuard AI predicts whether a student is likely to pass or fail using:

    - Attendance
    - Internal marks
    - Midterm marks
    - Study time
    - Backlog/failure history
    - Department
    - Semester
    - Academic engagement-style features

    ### Attendance policy logic

    - **Attendance ≥ 75%** → Eligible
    - **60% ≤ Attendance < 75%** → Second Chance / Guardian Approval
    - **Attendance < 60%** → Defaulter / High Risk

    ### Why this is industry-relevant

    Colleges, EdTech companies, and learning platforms use this type of early-alert system to identify at-risk learners, reduce dropouts, and recommend targeted interventions.
    """)

    premium_divider()

    st.markdown("### Classification Report")
    st.code(metrics["report"])


# ==========================================================
# PAGE 7: INTERVENTION PLAYBOOK
# ==========================================================

elif page == "📌 Intervention Playbook":

    page_header(
        "📌 Academic Intervention Playbook",
        "Operational strategy for colleges, mentors, academic advisors, and guardian communication.",
        "emerald"
    )

    i1, i2, i3 = st.columns(3)

    with i1:
        st.markdown("""
        ### 🟢 Low Risk

        - Continue normal monitoring
        - Maintain attendance above 75%
        - Encourage consistent learning
        - Recommend peer learning groups
        - Monthly progress review
        """)

    with i2:
        st.markdown("""
        ### 🟡 Second Chance / Medium Risk

        - Guardian approval required
        - Valid reason verification
        - Attendance recovery plan
        - Weekly mentoring
        - Subject-wise practice schedule
        - Department mentor follow-up
        """)

    with i3:
        st.markdown("""
        ### 🟣 High Risk / Defaulter

        - Immediate guardian call
        - Academic support plan
        - Backlog recovery strategy
        - Practice test series
        - Department-level monitoring
        - Exam eligibility review
        """)

    premium_divider()

    st.markdown("## 🧩 Intervention Mapping")

    playbook = pd.DataFrame({
        "Risk Condition": [
            "Attendance below 60%",
            "Attendance between 60% and 75%",
            "G1 below 10",
            "G2 below 10",
            "Previous failures/backlogs",
            "Performance declining from G1 to G2"
        ],
        "Action": [
            "Immediate guardian call + authority review",
            "Second chance approval + attendance recovery plan",
            "Internal marks improvement plan",
            "Mentoring + practice tests",
            "Backlog recovery tracking",
            "Subject-wise improvement plan"
        ],
        "Priority": [
            "Critical",
            "Medium",
            "Medium",
            "High",
            "High",
            "High"
        ]
    })

    st.dataframe(playbook, use_container_width=True, hide_index=True)
