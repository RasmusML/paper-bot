# <img src="imgs/icon.jpg" alt="drawing" width="40" align="center"/> paper-bot

A [client] bot to retrieve scientific papers from [database].

**Clients**: slack, discord.

**Databases**: Semantic Scholar (ACM, arXiv, bioRxiv, medRxiv, PubMed, ...).

## Commands

Retrieve papers published after `<since>` and satisfying `<query>`. `<query>` uses the Semantic Scholar search-format. [Example](queries/amp.txt).

```
/paperfind <query> <since> [--no_extra] [--no_query] [--split] [--template]
```

Retrieve papers "similar" to paper with `<title>`.

```
/paperlike <title> [--no_extra] [--split]
```

Retrieve papers citing paper with `<title>`.

```
/papercite <title> [--no_extra] [--split]
```

**Note**: On discord, prefix a command with `!` instead of `/`, e.g., `!paperfind [...]`.

### Optional flags

- `--no_extra`: Don't include `｜📅 publication date｜📚 reference count｜💬 citation count｜` in the bot response.
- `--no_query`: Don't include the original query in the bot response.
- `--split`: Bot sends a seperate message for each paper retrieved.
- `--template`: Use the query in `queries/<query>.txt` as the search query.

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
