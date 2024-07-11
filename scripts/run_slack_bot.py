"""Script to run a Slack bot that fetches scientific papers.

References
----------
- https://slack.dev/bolt-python/concepts

"""

import datetime
import logging
import os

import paperbot as pb
import paperbot.formatter.rich_text as rt
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logger = logging.getLogger(__name__)

HELP_INFO = """
*PaperBot Usage*
- Use `/paperbot <query>,<date_since>` to fetch papers.
- Example: `/paperbot ("machine learning" | "ML") + "AMP",2022-01-01`
"""

TEMPLATE_QUERIES_DIR = "queries/"


load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


def parse_arguments(text: str) -> list[str]:
    return text.strip().split(",")


@app.command("/paperbot")
def paperbot(ack, body):
    ack()

    channel_id = body["channel_id"]
    args = parse_arguments(body["text"])

    if len(args) != 2:
        app.client.chat_postMessage(channel=channel_id, text=HELP_INFO)
        return

    query_or_name, date_since = args

    template_queries = pb.read_queries_from_dir(TEMPLATE_QUERIES_DIR)
    query = template_queries.get(query_or_name, query_or_name)

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        app.client.chat_postMessage(channel=channel_id, text="Invalid date format. Please use YYYY-MM-DD.")
        return

    try:
        papers = pb.fetch_papers(query, since=since)
    except ValueError:
        app.client.chat_postMessage(channel=channel_id, text="Invalid query. Please check the syntax.")
        return

    papers = pb.prepare_papers(papers)

    blocks = pb.format_paper_overview(papers, since, format_type="slack-fancy")
    text = pb.format_paper_overview(papers, since, format_type="slack")

    app.client.chat_postMessage(channel=channel_id, text=text, blocks=blocks)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
