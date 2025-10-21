from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from pyrus import client
import pyrus.models
from collections import defaultdict
from sqlalchemy.orm import Session

from database import get_db, User
from auth_routes import router as auth_router
from auth_utils import get_current_active_user, get_current_active_user_from_cookie
from schemas import CatalogsListResponse, CatalogResponse, CatalogSummary, CatalogHeader, CatalogItem, TaskFormResponse, TaskForm, TaskFormField, TaskCreateRequest

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Pyrus Tasks API")

# Настройка CORS для работы с frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://localhost",
        "http://localhost:8081",  # Frontend контейнер
        "http://localhost:8082",   # Nginx прокси
        "http://frontend:80",      # Внутренний адрес frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов авторизации
app.include_router(auth_router, prefix="/api")

def get_pyrus_client(current_user: User = Depends(get_current_active_user_from_cookie)):
    """Получение клиента Pyrus для текущего пользователя"""
    # Используем учетные данные из базы данных
    login = current_user.login
    security_key = current_user.security_key
    
    pyrus_client = client.PyrusAPI(login=login, security_key=security_key)
    
    # Проверяем авторизацию
    try:
        auth_response = pyrus_client.auth()
        if not auth_response.success:
            raise HTTPException(status_code=401, detail=f"Ошибка авторизации в Pyrus: {auth_response.error}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Ошибка подключения к Pyrus: {str(e)}")
    
    return pyrus_client

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

@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks(pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
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

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: int, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
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

@app.get("/api/inbox")
async def get_inbox(tasks_count: int = 50, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
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

@app.get("/api/inbox_full")
async def get_inbox_full(tasks_count: int = 100, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
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

@app.post("/api/tasks/{task_id}/comment")
async def comment_task(task_id: int, comment_request: TaskCommentRequest, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
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

@app.get("/api/forms")
async def get_forms(pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
    """
    Получить все формы
    """
    try:
        forms_response = pyrus_client.get_forms()
        return forms_response.forms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _build_task_form(form_id: int, pyrus_client: client.PyrusAPI) -> TaskFormResponse:
    """
    Внутренняя функция для построения структуры формы задачи
    """
    # Получаем структуру формы
    form_response = pyrus_client.get_form(form_id)
    if not form_response:
        raise HTTPException(status_code=404, detail="Форма не найдена")
    
    # Собираем информацию о полях
    task_form_fields = []
    catalog_ids_to_load = set()
    
    # Проверяем наличие полей
    fields = getattr(form_response, 'fields', [])
    if not fields:
        raise HTTPException(status_code=404, detail="Поля формы не найдены")
    
    for field in fields:
        field_info = TaskFormField(
            id=field.id,
            name=field.name,
            type=field.type,
            required=getattr(field, 'required', False)
        )
        
        # Обрабатываем специфичную информацию для разных типов полей
        field_pyrus_info = getattr(field, 'info', None)
        
        if field.type == 'catalog' and field_pyrus_info:
            # Для каталогов сохраняем catalog_id
            catalog_id = getattr(field_pyrus_info, 'catalog_id', None)
            if catalog_id:
                field_info.catalog_id = catalog_id
                catalog_ids_to_load.add(catalog_id)
        
        elif field.type in ['status', 'checkmark', 'multiple_choice'] and field_pyrus_info:
            # Для полей с выбором сохраняем варианты
            options = getattr(field_pyrus_info, 'options', [])
            if options:
                catalog_items = []
                for idx, option in enumerate(options):
                    choice_id = idx + 1  # choice_id начинается с 1
                    choice_value = getattr(option, 'choice_value', option) if hasattr(option, 'choice_value') else str(option)
                    catalog_items.append(CatalogItem(
                        item_id=choice_id,
                        values=[choice_value],
                        headers=[choice_value]
                    ))
                field_info.catalog_items = catalog_items
        
        task_form_fields.append(field_info)
    
    # Загружаем данные каталогов (после цикла по полям)
    catalogs = []
    for catalog_id in catalog_ids_to_load:
        try:
            catalog_response = pyrus_client.get_catalog(catalog_id)
            if catalog_response and not getattr(catalog_response, 'error_code', None):
                # Получаем элементы каталога
                catalog_items = []
                if catalog_response.items:
                    for item in catalog_response.items:
                        catalog_items.append(CatalogItem(
                            item_id=item.item_id,
                            values=item.values if hasattr(item, 'values') else None,
                            headers=item.headers if hasattr(item, 'headers') else None,
                            rows=item.rows if hasattr(item, 'rows') else None
                        ))
                
                # Добавляем catalog_items к соответствующему полю
                for field in task_form_fields:
                    if field.catalog_id == catalog_id:
                        field.catalog_items = catalog_items
                
        except Exception as e:
            print(f"Ошибка загрузки каталога {catalog_id}: {str(e)}")
            continue
    
    # Создаем объект TaskForm
    task_form = TaskForm(
        form_id=getattr(form_response, 'id', form_id),
        form_name=getattr(form_response, 'name', f'Форма {form_id}'),
        fields=task_form_fields
    )
    
    return TaskFormResponse(
        form=task_form,
        catalogs=[]
    )

@app.get("/api/forms/{form_id}/task-form", response_model=TaskFormResponse)
async def get_task_form(form_id: int, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
    """
    Получить структуру формы для создания/редактирования задачи
    """
    try:
        return _build_task_form(form_id, pyrus_client)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] Exception in get_task_form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}/form")
async def get_task_form_data(task_id: int, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
    """
    Получить форму задачи с текущими значениями полей
    """
    try:
        # Получаем задачу
        task_response = pyrus_client.get_task(task_id)
        if not task_response or not task_response.task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        task = task_response.task
        form_id = task.form_id
        
        # Получаем структуру формы через внутреннюю функцию
        form_data = _build_task_form(form_id, pyrus_client)
        
        # Извлекаем текущие значения полей из задачи
        current_values = {}
        if hasattr(task, 'fields') and task.fields:
            for field in task.fields:
                field_id = str(field.id)
                field_value = field.value
                
                # Обрабатываем разные типы полей
                if hasattr(field, 'type'):
                    if field.type == 'catalog':
                        # Для каталогов извлекаем item_id
                        if hasattr(field_value, 'item_id'):
                            current_values[field_id] = field_value.item_id
                        elif isinstance(field_value, dict) and 'item_id' in field_value:
                            current_values[field_id] = field_value['item_id']
                        else:
                            current_values[field_id] = field_value
                    elif field.type in ['checkmark', 'multiple_choice']:
                        # Для множественного выбора извлекаем choice_ids
                        if hasattr(field_value, 'choice_ids'):
                            current_values[field_id] = field_value.choice_ids
                        elif isinstance(field_value, dict) and 'choice_ids' in field_value:
                            current_values[field_id] = field_value['choice_ids']
                        else:
                            current_values[field_id] = field_value
                    elif field.type == 'status':
                        # Для статуса извлекаем choice_id
                        if hasattr(field_value, 'choice_id'):
                            current_values[field_id] = field_value.choice_id
                        elif isinstance(field_value, dict) and 'choice_id' in field_value:
                            current_values[field_id] = field_value['choice_id']
                        else:
                            current_values[field_id] = field_value
                    else:
                        current_values[field_id] = field_value
                else:
                    current_values[field_id] = field_value
        
        # Добавляем subject и text если есть
        if hasattr(task, 'subject'):
            current_values['subject'] = task.subject
        if hasattr(task, 'text'):
            current_values['text'] = task.text
        
        # Собираем информацию о комментариях
        comments = []
        if hasattr(task, 'comments') and task.comments:
            for comment in task.comments:
                # Извлекаем информацию об авторе
                author_name = "Система"
                if hasattr(comment, 'author') and comment.author:
                    author = comment.author
                    first_name = getattr(author, 'first_name', '') or ''
                    last_name = getattr(author, 'last_name', '') or ''
                    email = getattr(author, 'email', None)
                    person_type = getattr(author, 'type', '')
                    
                    # Проверяем email (может быть None или строка 'None')
                    if email and str(email) not in ['None', 'null', '']:
                        email = str(email)
                    else:
                        email = ''
                    
                    # Формируем имя автора
                    if person_type == 'bot':
                        author_name = "Бот Pyrus"
                    elif person_type == 'role':
                        author_name = last_name if last_name else "Роль"
                    elif first_name and last_name:
                        # Есть и имя и фамилия
                        author_name = f"{first_name} {last_name}"
                    elif first_name:
                        # Только имя
                        author_name = first_name
                    elif last_name and last_name not in ['Pyrus.com', 'System', 'Bot']:
                        # Фамилия, но не системная
                        author_name = last_name
                    elif email:
                        # Используем email
                        author_name = email
                    else:
                        # Ничего нет - оставляем "Система"
                        author_name = "Система"
                
                comment_data = {
                    "author": author_name,
                    "text": getattr(comment, 'text', ''),
                    "create_date": getattr(comment, 'create_date', ''),
                    "approval_choice": getattr(comment, 'approval_choice', None),
                }
                # Добавляем вложения если есть
                if hasattr(comment, 'attachments') and comment.attachments:
                    comment_data['attachments'] = [
                        {
                            "id": att.id,
                            "name": att.name,
                            "size": getattr(att, 'size', 0),
                            "url": getattr(att, 'url', '')
                        }
                        for att in comment.attachments
                    ]
                comments.append(comment_data)
        
        # Собираем вложения задачи
        attachments = []
        if hasattr(task, 'attachments') and task.attachments:
            for att in task.attachments:
                attachments.append({
                    "id": att.id,
                    "name": att.name,
                    "size": getattr(att, 'size', 0),
                    "url": getattr(att, 'url', ''),
                    "version": getattr(att, 'version', 1)
                })
        
        return {
            "form": form_data.form,
            "current_values": current_values,
            "comments": comments,
            "attachments": attachments,
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] Exception in get_task_form_data: {str(e)}")
        print(f"[ERROR] form_data type: {type(form_data)}")
        print(f"[ERROR] form_data attributes: {dir(form_data) if hasattr(form_data, '__dict__') else 'N/A'}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalogs", response_model=CatalogsListResponse)
async def get_catalogs(pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
    """
    Получить список всех доступных каталогов с их структурой
    """
    try:
        # Получаем все формы для определения доступных каталогов
        forms_response = pyrus_client.get_forms()
        if forms_response.error_code:
            raise HTTPException(status_code=500, detail=f"Ошибка получения форм: {forms_response.error_code}")
        
        if not forms_response.forms:
            return CatalogsListResponse(catalogs=[], total_count=0)
        
        # Собираем все уникальные catalog_ids из форм
        catalog_ids = set()
        catalog_names = {}
        
        print(f"[DEBUG] Найдено форм: {len(forms_response.forms)}")
        
        for form in forms_response.forms:
            print(f"[DEBUG] Форма {form.id}: {form.name}")
            if hasattr(form, 'fields') and form.fields:
                print(f"[DEBUG] Поля формы: {len(form.fields)}")
                for field in form.fields:
                    print(f"[DEBUG] Поле: {field.name}, тип: {getattr(field, 'type', 'N/A')}")
                    if hasattr(field, 'type') and field.type == 'catalog':
                        catalog_info = getattr(field, 'info', {})
                        catalog_id = getattr(catalog_info, 'catalog_id', None) if catalog_info else None
                        print(f"[DEBUG] Найден каталог: {catalog_id} для поля {field.name}")
                        if catalog_id:
                            catalog_ids.add(catalog_id)
                            catalog_names[catalog_id] = field.name
        
        print(f"[DEBUG] Итого найдено каталогов: {len(catalog_ids)}")
        print(f"[DEBUG] ID каталогов: {list(catalog_ids)}")
        
        if not catalog_ids:
            print("[DEBUG] Возвращаем пустой список каталогов")
            return CatalogsListResponse(catalogs=[], total_count=0)
        
        # Получаем информацию о каталогах
        catalogs = []
        
        for catalog_id in catalog_ids:
            try:
                catalog_response = pyrus_client.get_catalog(catalog_id)
                if catalog_response.error_code:
                    print(f"Ошибка получения каталога {catalog_id}: {catalog_response.error_code}")
                    continue
                
                catalog = catalog_response
                items_count = len(catalog.items) if catalog.items else 0
                headers_count = len(catalog.catalog_headers) if catalog.catalog_headers else 0
                
                # Преобразуем заголовки в наши схемы
                headers = []
                if catalog.catalog_headers:
                    headers = [
                        CatalogHeader(name=header.name, type=header.type)
                        for header in catalog.catalog_headers
                    ]
                
                catalog_summary = CatalogSummary(
                    id=catalog.catalog_id,
                    name=catalog_names.get(catalog_id, f"Каталог {catalog_id}"),
                    items_count=items_count,
                    headers_count=headers_count,
                    source_type=catalog.source_type or "default",
                    headers=headers
                )
                
                catalogs.append(catalog_summary)
                
            except Exception as e:
                print(f"Ошибка получения каталога {catalog_id}: {str(e)}")
                continue
        
        return CatalogsListResponse(
            catalogs=catalogs,
            total_count=len(catalogs)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalogs/{catalog_id}", response_model=CatalogResponse)
async def get_catalog_by_id(catalog_id: int, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
    """
    Получить конкретный каталог по ID с полной информацией
    """
    try:
        catalog_response = pyrus_client.get_catalog(catalog_id)
        if catalog_response.error_code:
            raise HTTPException(status_code=404, detail=f"Каталог не найден: {catalog_response.error_code}")
        
        catalog = catalog_response
        
        # Преобразуем заголовки
        headers = []
        if catalog.catalog_headers:
            headers = [
                CatalogHeader(name=header.name, type=header.type)
                for header in catalog.catalog_headers
            ]
        
        # Преобразуем элементы
        items = []
        if catalog.items:
            items = [
                CatalogItem(
                    item_id=item.item_id if hasattr(item, 'item_id') else None,
                    values=item.values if hasattr(item, 'values') else None,
                    headers=item.headers if hasattr(item, 'headers') else None,
                    rows=item.rows if hasattr(item, 'rows') else None
                )
                for item in catalog.items
            ]
        
        return CatalogResponse(
            catalog_id=catalog.catalog_id,
            items=items,
            catalog_headers=headers,
            source_type=catalog.source_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task/{task_id}/full")
async def get_task_full(task_id: int, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
    """
    Получить полную информацию о задаче включая все каталоги
    """
    try:
        # Получаем задачу
        task_response = pyrus_client.get_task(task_id)
        if task_response.error_code:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        task = task_response.task
        
        # Получаем все каталоги
        catalogs_response = await get_catalogs(pyrus_client)
        
        return {
            "task": task,
            "catalogs": catalogs_response.catalogs,
            "total_catalogs": catalogs_response.total_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forms/{form_id}/task-form", response_model=TaskFormResponse)
async def get_task_form(form_id: int, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
    """
    Получить форму задачи с заполненными каталогами для выпадающих списков
    """
    try:
        # Получаем форму
        form_response = pyrus_client.get_form(form_id)
        if form_response.error_code:
            raise HTTPException(status_code=404, detail=f"Форма не найдена: {form_response.error_code}")
        
        form = form_response.form
        
        # Получаем все каталоги
        catalogs_response = await get_catalogs(pyrus_client)
        
        # Создаем мапу каталогов для быстрого поиска
        catalogs_map = {catalog.id: catalog for catalog in catalogs_response.catalogs}
        
        # Обрабатываем поля формы
        form_fields = []
        
        for field in form.fields:
            field_data = TaskFormField(
                id=field.id,
                name=field.name,
                type=field.type,
                required=getattr(field, 'required', False)
            )
            
            # Если поле типа catalog, получаем элементы каталога
            if field.type == 'catalog' and hasattr(field, 'info'):
                catalog_info = getattr(field, 'info', {})
                catalog_id = getattr(catalog_info, 'catalog_id', None) if catalog_info else None
                
                if catalog_id:
                    field_data.catalog_id = catalog_id
                    
                    # Получаем элементы каталога
                    try:
                        catalog_response = pyrus_client.get_catalog(catalog_id)
                        if catalog_response.items:
                            catalog_items = [
                                CatalogItem(
                                    item_id=item.item_id if hasattr(item, 'item_id') else None,
                                    values=item.values if hasattr(item, 'values') else None,
                                    headers=item.headers if hasattr(item, 'headers') else None,
                                    rows=item.rows if hasattr(item, 'rows') else None
                                )
                                for item in catalog_response.items
                            ]
                            field_data.catalog_items = catalog_items
                    except Exception as e:
                        print(f"Ошибка получения каталога {catalog_id}: {str(e)}")
            
            form_fields.append(field_data)
        
        task_form = TaskForm(
            form_id=form.id,
            form_name=form.name,
            fields=form_fields
        )
        
        return TaskFormResponse(
            form=task_form,
            catalogs=catalogs_response.catalogs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks/create")
async def create_task(task_request: TaskCreateRequest, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
    """
    Создать новую задачу с заполненными полями
    """
    try:
        # Создаем запрос на создание задачи
        create_request = pyrus.models.requests.TaskCreateRequest(
            form_id=task_request.form_id,
            field_values=task_request.field_values,
            subject=task_request.subject,
            text=task_request.text
        )
        
        response = pyrus_client.create_task(create_request)
        
        if response.error_code:
            raise HTTPException(status_code=400, detail=f"Ошибка создания задачи: {response.error_code}")
        
        return {
            "task_id": response.task_id,
            "message": "Задача успешно создана"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}/form")
async def get_task_form_data(task_id: int, pyrus_client: client.PyrusAPI = Depends(get_pyrus_client)):
    """
    Получить данные формы для редактирования существующей задачи
    """
    try:
        # Получаем задачу
        task_response = pyrus_client.get_task(task_id)
        if task_response.error_code:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        task = task_response.task
        form_id = task.form_id
        
        # Получаем форму с каталогами
        form_response = await get_task_form(form_id, pyrus_client)
        
        # Добавляем текущие значения полей задачи
        task_field_values = {}
        if hasattr(task, 'fields') and task.fields:
            for field in task.fields:
                task_field_values[field.id] = field.value
        
        return {
            "form": form_response.form,
            "catalogs": form_response.catalogs,
            "current_values": task_field_values,
            "task_id": task_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
