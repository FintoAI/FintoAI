# FintoAI

> A local-first AI agent for reasoning about your personal finances.
> Read-only. Deterministic. Your data never leaves your machine.

## Why

Personal finance tools tell you what you spent. They don't help you reason about it.
Mint and Monzo show pretty charts but can't answer "did I spend more on takeaways the months I worked late? or did I spend more on Amazon during some period of the month?" ChatGPT can reason, but you have to dump CSVs into a stranger's cloud and trust it not to hallucinate the numbers. Spreadsheets work but die the moment your question gets interesting.
FintoAI is the missing piece: a real agent that reasons about your transactions, runs entirely on your machine, and never makes up a number it can't point at.

## What makes it different

- **Local-first.** Runs on your machine. Bank data is stored in a local SQLite database. Nothing is sent to any cloud service except the LLM call itself — and even that you control.
- **Deterministic safety.** The agent never invents numbers. Every figure in every answer is traced back to a specific transaction in your database, and citations are shown.
- **Read-only by design.** FintoAI cannot move money. The bank integration layer has no write methods — the abstraction makes it physically impossible.
- **Open source.** AGPL-3.0. Fork it, audit it, run it.

## Status

Pre-alpha. Building in public. Currently: [one sentence on where you actually are — "scaffolding the provider interface" is fine].

Follow progress: [Substack link once you have it] · [GitHub issues]

## Architecture

FintoAI is four layers, deliberately boring:

Providers (src/fintoai/providers/) — read-only adapters for bank data sources. The BankProvider abstract base class has no write methods, so no implementation can move money even by accident. GoCardless first (UK banks, free tier); Plaid, TrueLayer, and a CSV importer later.
Storage (src/fintoai/storage/) — a local SQLite database with SQLAlchemy models for accounts and transactions. Lives in a single file on your machine. Easy to back up, easy to delete, easy to inspect with any SQLite browser.
Agent (src/fintoai/agent/) — a LangGraph loop that turns a natural-language question into SQL against your local database. Every answer carries citations: the specific transaction IDs the numbers came from. If the agent can't ground a claim in real rows, it doesn't make the claim.
API (src/fintoai/api/) — a FastAPI server exposing the agent over HTTP, plus (later) an MCP interface so other AI clients can query your finances directly.

## Getting started

> Not yet runnable end-to-end. These instructions will work once the first provider lands.

```bash
git clone git@github.com:FintoAI/FintoAI.git
cd FintoAI
uv sync
cp .env.example .env  # then fill in credentials
uv run uvicorn fintoai.api.main:app --reload
```

## Roadmap

- [x] Repo scaffolding, BankProvider interface
- [ ] GoCardless provider (UK bank connections)
- [ ] SQLite storage layer + transaction sync
- [ ] First agent loop: "how much did I spend on X last month" with citations
- [ ] Eval harness (20 known-answer tests)
- [ ] Recurring transaction detection
- [ ] Budget reasoning
- [ ] MCP server interface
- [ ] Public launch

## Design principles

1. The agent never invents a number.
2. Every answer cites the transactions it's based on.
3. Bank integrations are read-only at the type level.
4. Local-first. Cloud is opt-in, never default.
5. Boring tech: Python, SQLite, FastAPI. Nothing exotic.

## Licence

AGPL-3.0. See [LICENSE](./LICENSE).