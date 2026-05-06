import pandas as pd

def attendance_zone(attendance):
    if attendance >= 75:
        return "Eligible"
    if attendance >= 60:
        return "Second Chance"
    return "Defaulter"


def calculate_risk_score(attendance, g1, g2, failures, pass_prob):
    score = 0

    if attendance < 60:
        score += 40
    elif attendance < 75:
        score += 25
    else:
        score += 5

    if g1 < 10:
        score += 15

    if g2 < 10:
        score += 20

    if failures > 0:
        score += failures * 10

    score += int((1 - pass_prob) * 25)

    return min(score, 100)


def risk_badge(score):
    if score >= 70:
        return "CRITICAL"
    if score >= 40:
        return "WATCHLIST"
    return "SAFE"


def make_input_row(
    absences,
    g1,
    g2,
    studytime,
    failures,
    department,
    core_subject,
    semester,
    admission_type,
    hostel_status
):
    attendance_pct = max(0, min(100, 100 - absences))

    return {
        "age": 18,
        "Medu": 3,
        "Fedu": 3,
        "traveltime": 1,
        "studytime": studytime,
        "failures": failures,
        "famrel": 4,
        "freetime": 3,
        "goout": 3,
        "Dalc": 1,
        "Walc": 1,
        "health": 4,
        "absences": absences,
        "G1": g1,
        "G2": g2,
        "attendance_pct": attendance_pct,
        "grade_progress": g2 - g1,
        "backlog_count": failures,

        "school": "GP",
        "sex": "F",
        "address": "U",
        "famsize": "GT3",
        "Pstatus": "T",
        "Mjob": "teacher",
        "Fjob": "services",
        "reason": "course",
        "guardian": "mother",
        "schoolsup": "no",
        "famsup": "yes",
        "paid": "no",
        "activities": "yes",
        "nursery": "yes",
        "higher": "yes",
        "internet": "yes",
        "romantic": "no",
        "attendance_zone": attendance_zone(attendance_pct),
        "department": department,
        "core_subject": core_subject,
        "semester": semester,
        "admission_type": admission_type,
        "hostel_status": hostel_status
    }


def generate_ai_insights(row, prediction, risk, risk_score, pass_prob):
    insights = []

    if row["attendance_pct"] < 60:
        insights.append("Attendance is below 60%, placing the student in the defaulter category.")
    elif row["attendance_pct"] < 75:
        insights.append("Attendance is below the standard 75% rule, so second-chance approval is required.")
    else:
        insights.append("Attendance is above the eligibility threshold, which improves academic stability.")

    if row["G2"] < row["G1"]:
        insights.append("Performance has declined from internal assessment to midterm, indicating a negative academic trend.")
    elif row["G2"] > row["G1"]:
        insights.append("Performance improved from internal assessment to midterm, showing positive academic momentum.")

    if row["failures"] > 0:
        insights.append("Previous backlog/failure history increases the academic risk score.")

    if pass_prob >= 0.75:
        insights.append("The ML model shows strong confidence that the student can pass.")
    elif pass_prob >= 0.50:
        insights.append("The ML model shows moderate confidence, so monitoring is recommended.")
    else:
        insights.append("The ML model shows low pass confidence, so intervention should start immediately.")

    if risk_score >= 70:
        insights.append("This student should be prioritized for immediate mentor and guardian intervention.")
    elif risk_score >= 40:
        insights.append("This student should be kept on a watchlist with weekly academic tracking.")
    else:
        insights.append("This student is currently stable and requires only routine monitoring.")

    return insights


def predict_student(model, row):
    input_df = pd.DataFrame([row])

    pass_prob = float(model.predict_proba(input_df)[0][1])
    fail_prob = 1 - pass_prob
    ml_pred = int(model.predict(input_df)[0])

    attendance = row["attendance_pct"]

    if attendance < 60:
        risk = "High Risk"
        final_status = "Defaulter"
        prediction = "Fail"
    elif attendance < 75:
        risk = "Medium Risk"
        final_status = "Second Chance / Guardian Approval Required"
        prediction = "Pass" if ml_pred == 1 else "Fail"
    elif ml_pred == 0:
        risk = "High Risk"
        final_status = "Academically At Risk"
        prediction = "Fail"
    elif pass_prob < 0.70:
        risk = "Medium Risk"
        final_status = "Needs Monitoring"
        prediction = "Pass"
    else:
        risk = "Low Risk"
        final_status = "Eligible"
        prediction = "Pass"

    risk_score_value = calculate_risk_score(
        attendance,
        row["G1"],
        row["G2"],
        row["failures"],
        pass_prob
    )

    badge = risk_badge(risk_score_value)

    reasons = []
    interventions = []

    if attendance < 60:
        reasons.append("Attendance is below 60%, so the student is a real defaulter.")
        interventions.append("Immediate guardian call and academic authority review required.")
    elif attendance < 75:
        reasons.append("Attendance is below 75%, so the student needs second-chance approval.")
        interventions.append("Guardian consent, valid reason verification, and attendance recovery plan required.")
    else:
        reasons.append("Attendance satisfies the standard 75% eligibility rule.")

    if row["G1"] < 10:
        reasons.append("Internal assessment score is weak.")
        interventions.append("Weekly internal assessment improvement plan.")

    if row["G2"] < 10:
        reasons.append("Midterm score is below passing level.")
        interventions.append("Mentoring and practice test series recommended.")

    if row["failures"] > 0:
        reasons.append("Backlog/failure history is present.")
        interventions.append("Backlog recovery and academic monitoring required.")

    if row["grade_progress"] < 0:
        reasons.append("Performance dropped from G1 to G2.")
        interventions.append("Immediate subject-wise improvement plan required.")

    if risk_score_value >= 70:
        interventions.append("Mark student as priority case for department-level review.")
    elif risk_score_value >= 40:
        interventions.append("Add student to weekly watchlist and track attendance recovery.")
    else:
        interventions.append("Student is stable. Continue routine monitoring.")

    ai_insights = generate_ai_insights(
        row,
        prediction,
        risk,
        risk_score_value,
        pass_prob
    )

    return {
        "prediction": prediction,
        "risk": risk,
        "risk_score": risk_score_value,
        "risk_badge": badge,
        "attendance_pct": attendance,
        "attendance_zone": row["attendance_zone"],
        "final_status": final_status,
        "pass_prob": pass_prob,
        "fail_prob": fail_prob,
        "guardian_call_required": "Yes" if attendance < 75 or row["failures"] > 0 else "No",
        "reasons": reasons,
        "interventions": interventions,
        "ai_insights": ai_insights
    }