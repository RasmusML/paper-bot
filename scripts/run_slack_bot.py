"""Script to run a Slack bot that fetches scientific papers.

References
----------
- https://slack.dev/bolt-python/concepts

"""

import datetime
import logging
import os

import paperbot as pb
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logger = logging.getLogger(__name__)

HELP_INFO = """
*PaperBot Usage*
- Use `/paperbot <query>,<date_since>` to fetch papers.
- Example: `/paperbot ([machine learning] OR [ML]) AND [AMP],2022-01-01
"""

TEMPLATE_QUERIES_DIR = "configs/queries"


load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.command("/paperbot")
def paperbot(ack, say, body):
    ack()

    text = body["text"]
    text = text.strip()

    args = text.split(",")

    if len(args) != 2:
        return say(HELP_INFO)

    query, date_since = args

    template_queries = pb.read_queries_from_dir(TEMPLATE_QUERIES_DIR)
    if query in template_queries:
        query = template_queries[query]

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        say("Invalid date format. Please use YYYY-MM-DD.")
        return

    output_path = "outputs/slack_bot_papers.json"

    try:
        pb.fetch_papers(output_path, query, since=since)
    except ValueError:
        say("Invalid query. Please check the syntax.")
        return

    papers = pb.load_papers(output_path)
    text = pb.format_paper_overview(papers, "slack")

    say(text)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
