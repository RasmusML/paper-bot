# <img src="imgs/icon.jpg" alt="drawing" width="40" align="center"/> paper-bot

A [client] bot to retrieve scientific papers from [database].

**Clients**: slack, discord.

**Databases**: Semantic Scholar (ACM, arXiv, bioRxiv, medRxiv, PubMed, ...).

## Commands
Retrieve papers published after `<since>` and satisfying `<query>`. `<query>` uses the Semantic Scholar search-format. If `<query>` matches a template in `queries/`, the template is used instead, e.g., `amp` uses [queries/amp.txt](queries/amp.txt).
```
/paperfind <query> <since> [--split] [--no_extra] [--no_query]
```

Retrieve papers "similar" to paper with `<title>`.
```
/paperlike <title> [--split] [--no_extra]
```

Retrieve papers citing paper with `<title>`.
```
/papercite <title> [--split] [--no_extra]
```

**Note**: On discord, prefix a command with `!` instead of `/`, e.g., `!paperfind [...]`.

### Optional flags
- `--split`: Bot sends a seperate message for each paper retrieved.
- `--no_extra`: Don't include `｜📅 publication date｜📚 reference count｜💬 citation count｜` in the bot response.
- `--no_query`: Don't include the original query in the bot response.

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
