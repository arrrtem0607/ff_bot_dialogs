from sqlalchemy import select, update, inspect
from sqlalchemy.orm import joinedload
import logging
from functools import wraps

from database.entities.core import Database, Base
from database.entities.models import Worker
from configurations import get_config

logger = logging.getLogger(__name__)
config = get_config()


def session_manager(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self.db.async_session_factory() as session:
            try:
                logger.debug(f"Starting session for {func.__name__}")
                result = await func(self, session, *args, **kwargs)
                await session.commit()
                logger.debug(f"Session for {func.__name__} committed successfully")
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Error in {func.__name__}: {e}")
                raise e
            finally:
                await session.close()
                logger.debug(f"Session for {func.__name__} closed")
    return wrapper


class ORMController:
    def __init__(self, db: Database = Database()):
        self.db = db
        logger.info("ORMController initialized")

    async def create_tables(self):
        async with self.db.async_engine.begin() as conn:
            def sync_inspect(connection):
                inspector = inspect(connection)
                return inspector.get_table_names()

            existing_tables = await conn.run_sync(sync_inspect)

            if 'workers' not in existing_tables:
                logger.info("Creating 'workers' table")
                await conn.run_sync(Base.metadata.create_all, tables=[Worker.__table__])

            if 'packing_info' not in existing_tables:
                logger.info("Creating 'packing_info' table")
                # Предположим, что у вас есть модель PackingInfo
                # await conn.run_sync(Base.metadata.create_all, tables=[PackingInfo.__table__])
                # Если модели PackingInfo нет, закомментируйте или удалите эту строку

            logger.info("Tables checked and created if not exist")

    @session_manager
    async def create_worker(self, session, worker_data):
        logger.info(f"Creating worker with data: {worker_data}")
        worker = Worker(**worker_data)
        session.add(worker)
        await session.flush()
        logger.info(f"Worker created with ID: {worker.id}")
        return worker

    @session_manager
    async def get_worker_by_tg_id(self, session, tg_id: int):
        logger.info(f"Fetching worker by Telegram ID: {tg_id}")
        result = await session.execute(
            select(Worker).where(Worker.tg_id == tg_id)
        )
        worker = result.scalar_one_or_none()
        logger.info(f"Worker fetched: {worker}")
        return worker

    @session_manager
    async def update_worker_role(self, session, worker_id: int, role: str):
        logger.info(f"Updating worker ID {worker_id} to role {role}")
        await session.execute(
            update(Worker).where(Worker.id == worker_id).values(role=role)
        )
        logger.info(f"Worker ID {worker_id} role updated to {role}")

    @session_manager
    async def get_all_workers(self, session):
        logger.info("Fetching all workers")
        result = await session.execute(
            select(Worker).options(joinedload(Worker.role))
        )
        workers = result.scalars().all()
        logger.info(f"Fetched workers: {workers}")
        return workers

    @session_manager
    async def get_user_role(self, session, tg_id):
        result = await session.execute(select(Worker.role).where(Worker.tg_id == tg_id))
        role_record = result.scalars().first()
        admins_id = config.bot_config.get_developers_id()
        if tg_id == admins_id:
            role_record = 'admin'
        return role_record or "guest"
