import asyncio
import os
from logging.config import fileConfig
from typing import cast

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from dreamteams_exporter.adapters.db.config import EXPORTER_SCHEMA, DbConfig
from dreamteams_exporter.adapters.db.models.base import mapper_registry

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = mapper_registry.metadata

EXPORTER_CONFIG_PATH_ENV = "EXPORTER_CONFIG_PATH"


def get_url() -> str:
    """Resolve the SQLAlchemy URL, preferring a test-injected value over the TOML config file."""
    injected = config.attributes.get("db_url")
    if injected is not None:
        return cast("str", injected.render_as_string(hide_password=False))

    config_path = os.environ.get(EXPORTER_CONFIG_PATH_ENV)
    if config_path is None:
        msg = f"'{EXPORTER_CONFIG_PATH_ENV}' must point at the exporter TOML config to run migrations"
        raise RuntimeError(msg)

    db_config = DbConfig.from_toml(config_path)
    return db_config.connection_url.render_as_string(hide_password=False)


def _include_object(object_: object, name: str | None, type_: str, *_: object) -> bool:
    """Restrict autogenerate to objects inside the exporter schema."""
    if type_ == "table":
        schema = getattr(object_, "schema", None)
        return schema == EXPORTER_SCHEMA
    if type_ == "schema":
        return name == EXPORTER_SCHEMA
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emits SQL without touching a DB)."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=EXPORTER_SCHEMA,
        include_schemas=True,
        include_object=_include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Bind alembic to an open DB connection and run the configured migration step."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=EXPORTER_SCHEMA,
        include_schemas=True,
        include_object=_include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Build an async engine, attach it to the alembic context, and run migrations."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()  # type: ignore[index]

    connectable = async_engine_from_config(
        configuration,  # type: ignore[arg-type]
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for the standard online migration flow."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
