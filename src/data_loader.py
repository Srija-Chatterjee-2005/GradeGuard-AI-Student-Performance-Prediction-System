import numpy as np
import pandas as pd
from pathlib import Path
from ucimlrepo import fetch_ucirepo

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

ENGINEERING_DEPARTMENTS = [
    "CSE",
    "IT",
    "ECE",
    "EE",
    "ME",
    "Civil",
    "AI & ML",
    "CSBS",
    "CSDS",
    "Food Tech"
]

SUBJECT_GROUPS = [
    "Programming",
    "Data Structures",
    "DBMS",
    "Operating Systems",
    "Mathematics",
    "Electronics",
    "Mechanics",
    "Thermodynamics",
    "Food Processing",
    "Machine Learning"
]

def attendance_zone(attendance: float) -> str:
    if attendance >= 75:
        return "Eligible"
    if attendance >= 60:
        return "Second Chance"
    return "Defaulter"

def risk_segment(attendance: float, passed: int) -> str:
    if attendance < 60 or passed == 0:
        return "High Risk"
    if attendance < 75:
        return "Medium Risk"
    return "Low Risk"

def load_student_data() -> pd.DataFrame:
    dataset = fetch_ucirepo(id=320)

    X = dataset.data.features.copy()
    y = dataset.data.targets.copy()

    df = pd.concat([X, y], axis=1)

    df["passed"] = (df["G3"] >= 10).astype(int)
    df["attendance_pct"] = (100 - df["absences"]).clip(0, 100)
    df["attendance_zone"] = df["attendance_pct"].apply(attendance_zone)
    df["grade_progress"] = df["G2"] - df["G1"]

    np.random.seed(42)
    df["department"] = np.random.choice(ENGINEERING_DEPARTMENTS, size=len(df))
    df["core_subject"] = np.random.choice(SUBJECT_GROUPS, size=len(df))
    df["semester"] = np.random.choice(["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"], size=len(df))
    df["admission_type"] = np.random.choice(["Merit", "Entrance", "Management", "Lateral Entry"], size=len(df))
    df["hostel_status"] = np.random.choice(["Hosteller", "Day Scholar"], size=len(df))
    df["backlog_count"] = np.where(df["failures"] > 0, df["failures"], 0)
    df["guardian_call_required"] = np.where(
        (df["attendance_pct"] < 75) | (df["failures"] > 0) | (df["G2"] < 10),
        "Yes",
        "No"
    )
    df["risk_segment"] = df.apply(lambda x: risk_segment(x["attendance_pct"], x["passed"]), axis=1)

    df.to_csv(DATA_DIR / "processed_students.csv", index=False)
    return df