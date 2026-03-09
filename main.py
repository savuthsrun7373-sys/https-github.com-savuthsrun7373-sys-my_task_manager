import json
import os
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from firebase_admin import credentials, initialize_app, firestore

app = FastAPI()

# 1. ការតភ្ជាប់ Firebase
firebase_config_str = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if firebase_config_str:
    cred = credentials.Certificate(json.loads(firebase_config_str))
    initialize_app(cred)
else:
    # សម្រាប់អភិវឌ្ឍន៍លើកុំព្យូទ័រផ្ទាល់ខ្លួន
    cred = credentials.Certificate("serviceAccountKey.json")
    initialize_app(cred)

db = firestore.client()

# 2. បើកការអនុញ្ញាតឱ្យចូលប្រើ (CORS)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def read_index():
    return FileResponse("index.html")

# 3. មុខងារសម្រាប់ Project
@app.post("/projects")
def add_project(data: dict):
    db.collection("projects").document(data['id']).set({
        "id": data['id'],
        "date": data['date']
    })
    return {"message": "Project created"}

@app.get("/get_projects")
def get_projects():
    projects = []
    docs = db.collection("projects").stream()
    for doc in docs:
        projects.append(doc.to_dict())
    return {"projects": projects}

# 4. មុខងារសម្រាប់ Task
# ត្រូវប្រាកដថា Field ឈ្មោះ date_project ត្រូវបានរក្សាទុកក្នុង Firestore
    @app.post("/tasks")
    def add_task(task: dict = Body(...)):
        # បន្ថែមការ Print ដើម្បីពិនិត្យក្នុង Server Logs
        print(f"Adding task: {task}") 
        db.collection("tasks").add({
            "project_id": task.get('project_id'),
            "no": task.get('no'),
            "description": task.get('description'),
            "status": task.get('status'),
            "date_project": task.get('date_project'), # ត្រូវប្រាកដថាមានតម្លៃ
            "note": task.get('note')
        })
        return {"message": "Task added"}

@app.get("/tasks")
def get_tasks(project_id: str = Query(...)):
    tasks = []
    # ស្វែងរកតាម project_id
    docs = db.collection("tasks").where("project_id", "==", project_id).stream()
    for doc in docs:
        tasks.append(doc.to_dict())
    
    # ត្រូវប្រាកដថាត្រឡប់ជា Dictionary ដែលមាន Key "tasks"
    return {"tasks": tasks}