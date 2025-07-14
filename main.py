from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT", 5432)
ORIGIN = os.getenv("ORIGIN")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN],  # or use your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

@app.get("/api/sla")
def get_sla_data(month: str = Query(...), sat: str = Query(...)):
    conn = get_connection()
    cur = conn.cursor()

    query = """
                    SELECT 
                p.ProjectName AS project,

                MAX(CASE WHEN pr.ProfileName = 'Load Survey (8Hrs)' THEN s.SLA_Percentage END) AS "Load Survey (8Hrs)",
                MAX(CASE WHEN pr.ProfileName = 'Load Survey (12Hrs)' THEN s.SLA_Percentage END) AS "Load Survey (12Hrs)",
                MAX(CASE WHEN pr.ProfileName = 'Load Survey (24Hrs)' THEN s.SLA_Percentage END) AS "Load Survey (24Hrs)",
                MAX(CASE WHEN pr.ProfileName = 'Daily Profile' THEN s.SLA_Percentage END) AS "Daily Profile",

                MAX(CASE WHEN pr.ProfileName = 'Billing Profile (72 Hrs)' THEN s.SLA_Percentage END) AS "Billing Profile (72 Hrs)",
                MAX(CASE WHEN pr.ProfileName = 'Billing Profile (120 Hrs)' THEN s.SLA_Percentage END) AS "Billing Profile (120 Hrs)",
                MAX(CASE WHEN pr.ProfileName = 'Billing Profile (168 Hrs)' THEN s.SLA_Percentage END) AS "Billing Profile (168 Hrs)",

                MAX(CASE WHEN pr.ProfileName = 'Reconnect (15 min)' THEN s.SLA_Percentage END) AS "Reconnect (15 min)",
                MAX(CASE WHEN pr.ProfileName = 'Reconnect (6 Hrs)' THEN s.SLA_Percentage END) AS "Reconnect (6 Hrs)",

                MAX(CASE WHEN pr.ProfileName = 'Disconnect (15 min)' THEN s.SLA_Percentage END) AS "Disconnect (15 min)",
                MAX(CASE WHEN pr.ProfileName = 'Disconnect (6 Hrs)' THEN s.SLA_Percentage END) AS "Disconnect (6 Hrs)"

            FROM ProjectSLA s
            JOIN Projects p ON s.ProjectID = p.ProjectID
            JOIN Profiles pr ON s.ProfileID = pr.ProfileID
            WHERE s.YearMonth = %s AND s.SAT = %s
            GROUP BY p.ProjectName
            ORDER BY p.ProjectName;

    """

    cur.execute(query, (month, sat))
    rows = cur.fetchall()

    result = [
    {
        "project": row[0],
        "Load Survey (8Hrs)": float(row[1]) if row[1] is not None else "-",
        "Load Survey (12Hrs)": float(row[2]) if row[2] is not None else "-",
        "Load Survey (24Hrs)": float(row[3]) if row[3] is not None else "-",
        "Daily Profile": float(row[4]) if row[4] is not None else "-",
        "Billing Profile (72 Hrs)": float(row[5]) if row[5] is not None else "-",
        "Billing Profile (120 Hrs)": float(row[6]) if row[6] is not None else "-",
        "Billing Profile (168 Hrs)": float(row[7]) if row[7] is not None else "-",
        "Reconnect (15 min)": float(row[8]) if row[8] is not None else "-",
        "Reconnect (6 Hrs)": float(row[9]) if row[9] is not None else "-",
        "Disconnect (15 min)": float(row[10]) if row[10] is not None else "-",
        "Disconnect (6 Hrs)": float(row[11]) if row[11] is not None else "-",
    }
    for row in rows
    ]

    cur.close()
    conn.close()
    return result

