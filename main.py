import os
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import uvicorn
from apprise import Apprise
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from html_to_markdown import convert
from pydantic import BaseModel

load_dotenv()

APPRISE_TARGET_URL = os.environ.get("APPRISE_TARGET_URL") or ""
if APPRISE_TARGET_URL == "":
    raise ValueError("APPRISE_TARGET_URL environment variable is not set")
VIKUNJA_DOMAIN = os.environ.get("VIKUNJA_DOMAIN") or "https://vikunja.cloud"

# Set the avatar URL for the notification
avatar_url = "https://copyparty.lazyc97.top/vikunja_reminder/icon.png"


def get_apprise_url(task_id: str) -> str:
    target_url = urlsplit(APPRISE_TARGET_URL)
    query = dict(parse_qsl(target_url.query))
    query["avatar_url"] = avatar_url
    query["click"] = f"{VIKUNJA_DOMAIN}/tasks/{task_id}"
    return urlunsplit(target_url._replace(query=urlencode(query)))


def send_notification(task_id: int, title: str, body: str) -> bool:
    service = Apprise()
    if not service.add(get_apprise_url(str(task_id))):
        return False
    return service.notify(body=body, title=title) == True

app = FastAPI()


class TaskData(BaseModel):
    id: int
    title: str
    description: str
    due_date: str


class ProjectData(BaseModel):
    title: str


class ReminderData(BaseModel):
    reminder: str


class ReminderEventData(BaseModel):
    project: ProjectData
    task: TaskData
    reminder: ReminderData


class WebhookRequest(BaseModel):
    event_name: str
    data: dict


@app.post("/")
async def webhook(request: WebhookRequest):
    if request.event_name != "task.reminder.fired":
        return Response(status_code=400, content="Unsupported event type")

    data = ReminderEventData(**request.data)
    title = f"🔔 Reminder: {data.task.title}"
    description = convert(data.task.description).content
    due_date = datetime.fromisoformat(data.task.due_date)
    message = f"""
Project: {data.project.title}
{f"Due Date: {due_date}" if due_date.timestamp() > 0 else ""}
{f'''\nDescription:\n{description}''' if len(description or "") > 0 else ""}
""".strip()
    if send_notification(data.task.id, title=title, body=message):
        return {"status": "ok"}

    return Response(status_code=500, content="Failed to send notification")


def main():
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
