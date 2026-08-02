# Vikunja Discord Reminder

A web server to receive webhook from Vikunja for reminder fired event and send message on Discord.

## How to run

Create `.env` file with variables:
```
DISCORD_WEBHOOK_URL="webhook you create on discord"
MENTION_USER_IDS="list of user ID you wanna get mentioned, separated by comma"
```

Run the server:
```
uv run main.py
```

There you can create webhook on Vikunja to send `task.reminder.fired` events to your server.

Note: In case you're sending to a server in internal network, you must set [allownonroutableips](https://vikunja.io/docs/config-options/#1-webhooks-allownonroutableips) of your Vikunja instance to `true`.
