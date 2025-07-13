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
            MAX(CASE WHEN pr.ProfileName = 'LoadSurvey' THEN s.SLA_Percentage END) AS LS,
            MAX(CASE WHEN pr.ProfileName = 'Billing' THEN s.SLA_Percentage END) AS Billing,
            MAX(CASE WHEN pr.ProfileName = 'RC' THEN s.SLA_Percentage END) AS RC,
            MAX(CASE WHEN pr.ProfileName = 'DC' THEN s.SLA_Percentage END) AS DC
        FROM ProjectSLA s
        JOIN Projects p ON s.ProjectID = p.ProjectID
        JOIN Profiles pr ON s.ProfileID = pr.ProfileID
        WHERE s.YearMonth = %s AND s.SAT = %s
        GROUP BY p.ProjectName
        ORDER BY p.ProjectName
    """

    cur.execute(query, (month, sat))
    rows = cur.fetchall()

    result = [
        {
            "project": row[0],
            "LS": float(row[1]) if row[1] is not None else "-",
            "Billing": float(row[2]) if row[2] is not None else "-",
            "RC": float(row[3]) if row[3] is not None else "-",
            "DC": float(row[4]) if row[4] is not None else "-",
        }
        for row in rows
    ]

    cur.close()
    conn.close()
    return result

