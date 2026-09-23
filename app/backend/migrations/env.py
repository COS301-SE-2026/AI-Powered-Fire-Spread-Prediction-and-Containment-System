import os
from logging.config import fileConfig

from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import create_engine

from app.backend.db import Base

from app.backend.src.models.containment_lines import ContainmentLines
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.models.role_request import RoleRequest
from app.backend.src.models.users import User
from app.backend.src.models.notification import Notification

config = context.config
target_metadata = Base.metadata

def include_object(obj, name, type_, reflected, compare_to):
    # never attempt to drop a table that exists in the db but not in the current models
    if type_ == "table" and reflected and compare_to is None:
        return False
    return alembic_helpers.include_object(obj, name, type_, reflected, compare_to)

def run(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        process_revision_directives=alembic_helpers.writer,
        render_item=alembic_helpers.render_item,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

shared = config.attributes.get("connection")
if shared is not None:
    # call from app on startup and then reuse the connection and lock
    run(shared)
else:
    # call from the cli
    if config.config_file_name:
        fileConfig(config.config_file_name)
    with create_engine(os.environ["DATABASE_URL"]).connect() as conn:
        run(conn)