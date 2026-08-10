# Vikunja Reminder

A web server to receive webhook from Vikunja for reminder fired event and send notifications through Apprise.

## How to run

Create `.env` file:
```
APPRISE_TARGET_URL="your Apprise target URL"  # Apprise target URL
PORT="8080"                              # Server port; defaults to 8000
```

See the [Apprise URL documentation](https://github.com/caronc/apprise) for supported notification services.

Run the server:
```
uv run main.py
```

There you can create webhook on Vikunja to send `task.reminder.fired` events to your server.

Note: In case you're sending to a server in internal network, you must set [allownonroutableips](https://vikunja.io/docs/config-options/#1-webhooks-allownonroutableips) of your Vikunja instance to `true`.
