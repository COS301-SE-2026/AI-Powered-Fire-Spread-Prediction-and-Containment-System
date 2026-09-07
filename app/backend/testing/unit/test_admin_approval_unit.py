import os
import uuid
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.backend.db import Base, get_db
from app.backend.src.dependencies.auth import get_current_admin_user
from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole
from app.backend.src.models.role_request import RoleRequest
from app.backend.src.models.users import User
from app.backend.src.routes.role_requests import router
from app.backend.src.services.admin import role_request as role_request_service

