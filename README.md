# Cabal 🕴️

Your AI team, running on Slack. Open-source and forkable.

---

## 💡 What it is

Cabal is a Python framework for running a small team of AI agents as Slack bots. Each agent has a role (coach, CTO, PM, sales, architect), its own memory, and its own voice. They live in your Slack workspace, respond to messages in their areas, and collaborate on a single project scope.

Agents are defined declaratively as markdown files. Routines (daily standups, sprint rituals) are declarative too. No dashboards, no SaaS — just a repo you fork and run.

## 🎯 Who it's for

People juggling more than one track — a full-time role and a side venture, multiple clients, or a founding team of one — who want a structured team dynamic around their work without hiring one.

## 🚧 Status

**v0.0.x — pre-alpha.** Not yet usable as a CLI tool. Current focus is the memory module and core infrastructure.

See [CHANGELOG.md](CHANGELOG.md) for progress.

## 🛠️ Stack

- Python 3.11, `uv` for packaging
- `slack-bolt` (Socket Mode) for Slack
- SQLModel + SQLite for persistence
- OpenRouter via the `openai` SDK — model-agnostic
- Linear + Google Calendar integrations

## 📄 License

AGPL-3.0 — see [LICENSE](LICENSE)
