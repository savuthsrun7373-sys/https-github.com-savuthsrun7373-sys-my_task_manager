import json
import os
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from firebase_admin import credentials, initialize_app, firestore

app = FastAPI()

# តភ្ជាប់ Firebase
firebase_config_str = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if firebase_config_str:
    cred = credentials.Certificate(json.loads(firebase_config_str))
    initialize_app(cred)
else:
    cred = credentials.Certificate("serviceAccountKey.json")
    initialize_app(cred)

db = firestore.client()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.post("/projects")
def add_project(data: dict):
    db.collection("projects").document(data['id']).set({"id": data['id'], "date": data['date']})
    return {"message": "Project created"}

@app.get("/get_projects")
def get_projects():
    return {"projects": [doc.to_dict() for doc in db.collection("projects").stream()]}

@app.post("/tasks")
def add_task(task: dict = Body(...)):
    db.collection("tasks").add({
        "project_id": task.get('project_id'),
        "no": task.get('no'),
        "description": task.get('description'),
        "status": task.get('status'),
        "date": task.get('date'),
        "note": task.get('note')
    })
    return {"message": "Task added"}

@app.get("/tasks")
def get_tasks(project_id: str = Query(...)):
    return {"tasks": [doc.to_dict() for doc in db.collection("tasks").where("project_id", "==", project_id).stream()]}
@app.post("/update_task")
def update_task(task: dict = Body(...)):
    task_id = task.get('id') # អ្នកត្រូវផ្ញើ ID មកពី Frontend
    if not task_id:
        return {"error": "Missing task ID"}, 400
    
    # ប្រើ .document(id).set() ដើម្បី Update ទិន្នន័យចាស់
    db.collection("tasks").document(task_id).set({
        "project_id": task.get('project_id'),
        "no": task.get('no'),
        "description": task.get('description'),
        "status": task.get('status'),
        "date": task.get('date'),
        "note": task.get('note')
    }, merge=True)
    
    return {"message": "Task updated successfully"}