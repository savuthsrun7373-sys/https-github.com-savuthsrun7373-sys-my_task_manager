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

# --- Projects ---
@app.post("/projects")
def add_project(data: dict):
    db.collection("projects").document(data['id']).set({"id": data['id'], "date": data['date']})
    return {"message": "Project created"}

@app.get("/get_projects")
def get_projects():
    return {"projects": [doc.to_dict() for doc in db.collection("projects").stream()]}

# --- Tasks ---
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
    tasks = []
    # ប្រើ .where() ត្រឹមត្រូវដើម្បីទាញយកតាម project_id
    for doc in db.collection("tasks").where("project_id", "==", project_id).stream():
        t = doc.to_dict()
        t['id'] = doc.id
        tasks.append(t)
    return {"tasks": tasks}

@app.post("/update_task")
def update_task(task: dict = Body(...)):
    task_id = task.get('id')
    if not task_id:
        return {"error": "Missing task ID"}
    
    db.collection("tasks").document(task_id).set({
        "project_id": task.get('project_id'),
        "no": task.get('no'),
        "description": task.get('description'),
        "status": task.get('status'),
        "date": task.get('date'),
        "note": task.get('note')
    }, merge=True)
    return {"message": "Task updated"}
@app.route('/tasks', methods=['PUT'])
def update_task():
    data = request.json

    project_id = data['project_id']
    no = data['no']

    # update database
    cursor.execute("""
        UPDATE tasks
        SET description=%s, status=%s, date=%s, note=%s
        WHERE project_id=%s AND no=%s
    """, (data['description'], data['status'], data['date'], data['note'], project_id, no))

    conn.commit()

    return jsonify({"status":"updated"})
