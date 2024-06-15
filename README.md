# paper-bot

A [client] bot to retrieve scientific papers from [database].

**Clients**: slack, discord.

**Databases**: ACM, arXiv, bioRxiv, medRxiv, PubMed.

## Installation

You need to have Python 3.10 or newer installed on your system.

Install the latest development version:

```
git clone https://github.com/RasmusML/paper-bot.git
cd paper-bot
pip install -e .
```

## Setup
Add client tokens to `.env` in project root and run the desired clients bot script located in `scripts/`.