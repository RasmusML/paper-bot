import logging
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

import paperbot.clients.slack as client

SUPPORT_SPLIT_FLAG = False

load_dotenv()

app = App(process_before_response=True, token=os.environ.get("SLACK_BOT_TOKEN"))


def respond_to_slack_within_3_seconds(ack):
    ack("processing...")


app.command("/paperfind")(
    ack=respond_to_slack_within_3_seconds,
    lazy=[
        lambda body: client.paperfind(
            app,
            body,
            support_split_flag=SUPPORT_SPLIT_FLAG,
        )
    ],
)
app.command("/paperlike")(
    ack=respond_to_slack_within_3_seconds,
    lazy=[
        lambda body: client.paperlike(
            app,
            body,
            support_split_flag=SUPPORT_SPLIT_FLAG,
        )
    ],
)
app.command("/papercite")(
    ack=respond_to_slack_within_3_seconds,
    lazy=[
        lambda body: client.papercite(
            app,
            body,
            support_split_flag=SUPPORT_SPLIT_FLAG,
        )
    ],
)

SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


def handler(event, context):
    request_handler = SlackRequestHandler(app=app)
    return request_handler.handle(event, context)
