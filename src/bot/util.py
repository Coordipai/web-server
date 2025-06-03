import asyncio

import httpx
from apscheduler.schedulers.background import BackgroundScheduler

from src.config.config import COORDIPAI_BOT_URL
from src.config.database import get_db
from src.project.repository import find_all_active_projects
from src.response.error_definitions import DailyIssueReportError
from src.user.repository import find_user_by_user_id

scheduler = BackgroundScheduler()


async def send_daily_request():
    async with httpx.AsyncClient() as client:
        try:
            db = next(get_db())
            try:
                active_projects = find_all_active_projects(db)

                project_info = []
                for project in active_projects:
                    owner = find_user_by_user_id(db, project.owner)
                    if owner and owner.discord_id:
                        project_info.append(
                            {
                                "discord_channel_id": project.discord_channel_id,
                                "discord_id": owner.discord_id,
                            }
                        )

                response = await client.post(
                    COORDIPAI_BOT_URL,
                    json=project_info,
                )

                print(
                    f"Request sent for {len(active_projects)} active projects. Status code: {response.status_code}"
                )
                if response.status_code != 200:
                    raise DailyIssueReportError(response.status_code)
            finally:
                db.close()

        except Exception as e:
            print(f"Request failed: {e}")


def scheduled_job():
    asyncio.create_task(send_daily_request())


def start_scheduler():
    scheduler.add_job(scheduled_job, "cron", hour=9, minute=0)
    scheduler.start()


def shutdown_scheduler():
    scheduler.shutdown()
