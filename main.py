import json
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from firebase_admin import credentials, initialize_app, firestore

app = FastAPI()

# អានសោ Firebase ពី Environment Variable (សុវត្ថិភាពបំផុត)
firebase_config_str = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if firebase_config_str:
    cred = credentials.Certificate(json.loads(firebase_config_str))
    initialize_app(cred)
else:
    # សម្រាប់អភិវឌ្ឍន៍លើកុំព្យូទ័រ (ទុក file .json ក្នុង Folder)
    cred = credentials.Certificate("serviceAccountKey.json")
    initialize_app(cred)

db = firestore.client()

# ... (កូដ route ផ្សេងទៀតដដែល) ...

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.post("/projects")
def add_project(data: dict):
    # បន្ថែម Project ទៅក្នុង Firestore
    db.collection("projects").document(data['id']).set({
        "id": data['id'],
        "date_project": data['date']
    })
    return {"message": "Project created"}

@app.get("/get_projects")
def get_projects():
    # ទាញយកបញ្ជី Project
    projects = []
    docs = db.collection("projects").stream()
    for doc in docs:
        projects.append(doc.to_dict())
    return {"projects": projects}

from fastapi import FastAPI, Query, Body
# ... (import ផ្សេងៗដដែល) ...

@app.post("/tasks")
def add_task(task: dict = Body(...)):
    # ធានាថា project_id ត្រូវបានរក្សាទុកត្រឹមត្រូវ
    db.collection("tasks").add({
        "project_id": task.get('project_id'),
        "no": task.get('no'),
        "description": task.get('description'),
        "status": task.get('status'),
        "date_submit": task.get('date_submit'),
        "note": task.get('note')
    })
    return {"message": "Task added"}

@app.get("/tasks")
def get_tasks(project_id: str = Query(...)):
    # ទាញយកតែ Tasks ដែលមាន project_id ស្មើនឹងអ្វីដែលយើងកំពុងមើល
    tasks = []
    docs = db.collection("tasks").where("project_id", "==", project_id).stream()
    for doc in docs:
        t = doc.to_dict()
        tasks.append(t)
    return {"tasks": tasks}