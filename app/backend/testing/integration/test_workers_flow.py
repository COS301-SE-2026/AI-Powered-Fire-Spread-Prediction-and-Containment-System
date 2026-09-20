import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from db import get_db
from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.models.users import User
from app.backend.src.models.workers import WorkerNode
from app.backend.src.routes.workers import