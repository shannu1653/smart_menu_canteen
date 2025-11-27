from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector

app = FastAPI()

# serve static files (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# templates folder setup
templates = Jinja2Templates(directory="templates")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # change this to your MySQL user
        password="1234",   # change this to your MySQL password
        database="myapp"
    )

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/submit")
def submit_form(name: str = Form(...), email: str = Form(...), message: str = Form("")):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO users (name, email, message) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, email, message))
        conn.commit()
        cursor.close()
        conn.close()
        return HTMLResponse(
            content=f"""
                <h3>Thank you, {name}! Your data has been saved.</h3>
                <a href='/'>Add Another</a> | <a href='/users'>View Users</a>
            """,
            status_code=200
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<h3>Database error: {e}</h3><a href='/'>Try Again</a>",
            status_code=500
        )

# ✅ NEW: View all users
@app.get("/users", response_class=HTMLResponse)
def view_users(request: Request):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users ORDER BY id DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return templates.TemplateResponse("users.html", {"request": request, "users": users})
    except Exception as e:
        return HTMLResponse(content=f"<h3>Error: {e}</h3>", status_code=500)
