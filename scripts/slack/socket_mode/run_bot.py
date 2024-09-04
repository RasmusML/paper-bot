import logging
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import paperbot.clients.slack as client

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.command("/paperfind")
def paperfind(ack, body):
    ack()
    client.paperfind(app, body)


@app.command("/paperlike")
def paperlike(ack, body):
    ack()
    client.paperlike(app, body)


@app.command("/papercite")
def papercite(ack, body):
    ack()
    client.papercite(app, body)


# silence the 'unhandled message' logging warnings
@app.event("message")
def handle_message_events(body):
    pass


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
