from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from pyrus import client
import pyrus.models
from collections import defaultdict

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Pyrus Tasks API")

# Инициализация клиента Pyrus
pyrus_client = client.PyrusAPI(
    login=os.getenv("PYRUS_LOGIN"),
    security_key=os.getenv("PYRUS_SECURITY_KEY")
)

# Авторизация при запуске
try:
    auth_response = pyrus_client.auth()
    if not auth_response.success:
        print(f"Ошибка авторизации: {auth_response.error}")
        raise Exception(f"Ошибка авторизации в Pyrus: {auth_response.error}")
except Exception as e:
    print(f"Исключение при авторизации: {str(e)}")
    raise

class TaskResponse(BaseModel):
    id: int
    text: Optional[str]
    subject: Optional[str]
    create_date: datetime
    author: dict
    responsible: Optional[dict]
    due_date: Optional[datetime]

class TaskCommentRequest(BaseModel):
    text: str
    action: Optional[str]
    field_updates: Optional[List[Dict[str, Any]]]

@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks():
    """
    Получить список всех задач
    """
    try:
        # Получаем все формы
        forms_response = pyrus_client.get_forms()
        if not forms_response.forms:
            return []
            
        all_tasks = []
        
        # Для каждой формы получаем задачи
        for form in forms_response.forms:
            request = pyrus.models.requests.FormRegisterRequest(
                include_archived=False
            )
            tasks_response = pyrus_client.get_registry(form.id, request)
            if tasks_response.tasks:
                all_tasks.extend(tasks_response.tasks)
                
        return all_tasks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    """
    Получить конкретную задачу по ID
    """
    try:
        task_response = pyrus_client.get_task(task_id)
        if not task_response.task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return task_response.task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inbox")
async def get_inbox(tasks_count: int = 50):
    """
    Получить задачи из входящих
    """
    try:
        inbox_response = pyrus_client.get_inbox(tasks_count=tasks_count)
        # print("[DEBUG] Pyrus inbox_response.tasks:")
        # for t in inbox_response.tasks:
        #     print(t)
        return inbox_response.tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inbox_full")
async def get_inbox_full(tasks_count: int = 100):
    """
    Получить inbox с расширенной информацией (дедлайн, этап, заморозка, цвет)
    """
    try:
        inbox_response = pyrus_client.get_inbox(tasks_count=tasks_count)
        tasks = inbox_response.tasks

        task_ids = [t.id for t in tasks]
        if not task_ids:
            return []

        form_id = 829354

        # Получаем структуру формы и нужные field_ids
        form = pyrus_client.get_form(form_id)
        field_map = {f.name: f.id for f in form.fields}
        description_id = field_map.get("Описание/ Description")
        due_id = field_map.get("Срок/Term")
        step_id = field_map.get("Этап/Stage")

        req = pyrus.models.requests.FormRegisterRequest(
            task_ids=task_ids,
            field_ids=[description_id, due_id, step_id]
        )
        reg_resp = pyrus_client.get_registry(form_id, req)
        detailed_tasks = reg_resp.tasks if reg_resp.tasks else []

        result = []
        now = datetime.now(timezone.utc)
        for task in detailed_tasks:
            fields = {f.id: f.value for f in getattr(task, 'fields', [])}
            text = fields.get(description_id)
            due = fields.get(due_id)
            step = fields.get(step_id)

            due_dt = None
            if due:
                if isinstance(due, str):
                    try:
                        due_dt = datetime.fromisoformat(due)
                    except Exception:
                        due_dt = None
                else:
                    due_dt = due

            if due_dt:
                time_left = (due_dt - now).total_seconds()
                if time_left < 0:
                    color = 'red'
                elif time_left < 2 * 3600:
                    color = 'yellow'
                else:
                    color = 'white'
            else:
                color = 'white'

            # step — это номер этапа (int или str)
            try:
                step_num = int(step) if step is not None else None
            except Exception:
                step_num = None

            # # Для фронта: если этап 2 — пишем "Пауза", иначе None
            # if step_num == 2:
            #     step_name = "Пауза"
            # else:
            #     step_name = None
            step_name = step

            # Заморожена: если этап == 2 и нет срока
            is_frozen = (step_num == 2 and due_dt is None)

            result.append({
                "id": task.id,
                "text": text,
                "due": due_dt.isoformat() if due_dt else None,
                "step": step_name,
                "is_frozen": is_frozen,
                "color": color,
                "last_modified_date": task.last_modified_date.isoformat() if getattr(task, "last_modified_date", None) else None,
            })

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/{task_id}/comment")
async def comment_task(task_id: int, comment_request: TaskCommentRequest):
    """
    Добавить комментарий к задаче
    """
    try:
        request = pyrus.models.requests.TaskCommentRequest(
            text=comment_request.text,
            action=comment_request.action,
            field_updates=comment_request.field_updates
        )
        response = pyrus_client.comment_task(task_id, request)
        return response.task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 