from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from db import get_db
from dependencies.auth import decode_token, get_current_user
from models.notification import Notification
from model.users import User
from schemas.no