from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime

class UserCreate(BaseModel):
    login: str
    security_key: str

class UserLogin(BaseModel):
    login: str
    security_key: str

class UserResponse(BaseModel):
    id: int
    login: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    login: Optional[str] = None

# Схемы для каталогов
class CatalogHeader(BaseModel):
    name: str
    type: str

class CatalogItem(BaseModel):
    item_id: Optional[int] = None
    values: Optional[List[str]] = None
    headers: Optional[List[str]] = None
    rows: Optional[List[List[str]]] = None

class CatalogResponse(BaseModel):
    catalog_id: int
    items: Optional[List[CatalogItem]] = None
    catalog_headers: Optional[List[CatalogHeader]] = None
    source_type: Optional[str] = None

class CatalogSummary(BaseModel):
    id: int
    name: str
    items_count: int
    headers_count: int
    source_type: str
    headers: List[CatalogHeader]

class CatalogsListResponse(BaseModel):
    catalogs: List[CatalogSummary]
    total_count: int

# Схемы для формы задачи
class TaskFormField(BaseModel):
    id: int
    name: str
    type: str
    required: Optional[bool] = False
    catalog_id: Optional[int] = None
    catalog_items: Optional[List[CatalogItem]] = None

class TaskForm(BaseModel):
    form_id: int
    form_name: str
    fields: List[TaskFormField]

class TaskFormResponse(BaseModel):
    form: TaskForm
    catalogs: List[CatalogSummary]

class TaskCreateRequest(BaseModel):
    form_id: int
    field_values: Dict[str, Any]
    subject: Optional[str] = None
    text: Optional[str] = None
