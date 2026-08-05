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

# Set the avatar URL for the notification
avatar_url = "https://copyparty.lazyc97.top/vikunja_reminder/icon.png"
target_url = urlsplit(APPRISE_TARGET_URL)
target_query = dict(parse_qsl(target_url.query))
target_query["avatar_url"] = avatar_url
APPRISE_TARGET_URL = urlunsplit(target_url._replace(query=urlencode(target_query)))


notifier = Apprise()
notifier.add(APPRISE_TARGET_URL)

app = FastAPI()


class TaskData(BaseModel):
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
    if notifier.notify(body=message, title=title) == True:
        return {"status": "ok"}

    return Response(status_code=500, content="Failed to send notification")


def main():
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
