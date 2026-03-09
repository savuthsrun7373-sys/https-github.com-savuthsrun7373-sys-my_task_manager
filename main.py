import json
import os
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from firebase_admin import credentials, initialize_app, firestore

app = FastAPI()

# ១. ការកំណត់រចនាសម្ព័ន្ធ Firebase
firebase_config_str = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if firebase_config_str:
    # សម្រាប់ប្រើលើ Render (អានពី Environment Variable)
    cred = credentials.Certificate(json.loads(firebase_config_str))
    initialize_app(cred)
else:
    # សម្រាប់ប្រើលើកុំព្យូទ័រផ្ទាល់ខ្លួន
    cred = credentials.Certificate("serviceAccountKey.json")
    initialize_app(cred)

db = firestore.client()

# ២. ការកំណត់ Middleware
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# --- ផ្នែក Routes ---

@app.get("/")
async def read_index():
    return FileResponse("index.html")

# គ្រប់គ្រង Projects
@app.post("/projects")
def add_project(data: dict):
    db.collection("projects").document(data['id']).set({
        "id": data['id'],
        "date_project": data['date']
    })
    return {"message": "Project created"}

@app.get("/get_projects")
def get_projects():
    projects = []
    docs = db.collection("projects").stream()
    for doc in docs:
        projects.append(doc.to_dict())
    return {"projects": projects}

# គ្រប់គ្រង Tasks
@app.post("/tasks")
def add_task(task: dict = Body(...)):
    # រក្សាទុក Task ដោយភ្ជាប់ជាមួយ project_id
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
    """
    ទាញយកបញ្ជី Tasks តាមរយៈ project_id
    """
    tasks = []
    try:
        # ស្វែងរកតែ Tasks ណាដែលមាន project_id ដូចអ្វីដែលបានផ្ញើមក
        docs = db.collection("tasks").where("project_id", "==", project_id).stream()
        
        for doc in docs:
            task_data = doc.to_dict()
            task_data["id"] = doc.id  # បន្ថែម ID របស់ Document ងាយស្រួលគ្រប់គ្រង
            tasks.append(task_data)
            
        return {"tasks": tasks}
    except Exception as e:
        return {"error": str(e), "tasks": []}