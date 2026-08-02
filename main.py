import os
from datetime import datetime

import uvicorn
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv
from fastapi import FastAPI
from html_to_markdown import convert
from pydantic import BaseModel

load_dotenv()

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL") or ""
MENTION_USER_IDS = (os.environ.get("MENTION_USER_IDS") or "").split(",")
if DISCORD_WEBHOOK_URL == "":
    raise ValueError("DISCORD_WEBHOOK_URL environment variable is not set")

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


@app.post("/webhook")
async def webhook(request: WebhookRequest):
    if request.event_name == "task.reminder.fired":
        data = ReminderEventData(**request.data)
        dc_webhook = DiscordWebhook(
            url=DISCORD_WEBHOOK_URL,
            avatar_url="https://cdn.discordapp.com/attachments/1418191631726678182/1533427003989037245/894bd400d7c5bde78a65ba02e326798ccfb82006.png",
            username="Vikunja Reminder Bot",
            allow_mentions=True,
            content=f"""
# Task: {data.task.title}
Mentions: {", ".join(f"<@{user_id}>" for user_id in MENTION_USER_IDS)}
Project: {data.project.title}
Due Date: <t:{int(datetime.fromisoformat(data.task.due_date).timestamp())}:F>
Description:
```markdown
{convert(data.task.description).content}
```
""",
            rate_limit_retry=True,
        )
        dc_webhook.execute()
    return {"status": "ok"}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
