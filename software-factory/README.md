# 🤖 AI Software Factory (Sub-Project)

**The core engine behind the AI Software Factory.** This package handles agent orchestration, local LLM inference, and filesystem management.

---

## 🚀 Version 1.0.10 Highlights
- **💨 Optimized Local Mode**: 2-3x faster response times on CPU using physical-core threading.
- **✨ Clean Console**: Silenced JSON logs and technical warnings for a professional CLI look.
- **📍 Current Directory Focus**: No more `./output` folder—the AI builds and edits files directly where you are.

---

## 🛠️ Usage Guide

### 1. Launching
After installation via `pipx`, simply run:
```bash
ai-factory
```

### 2. Configuration (`/auth`)
The first time you run the tool, use `/auth` to choose your engine:
- **🟢 Local Mode**: Zero-Key, private, and free. Downloads a ~1GB model on first use.
- **🔵 Cloud Mode**: High-speed, uses OpenRouter. Requires an API Key.

### 3. Basic Workflow
AI Factory distinguishes between **Casual Chat** and **Build Requests** automatically.
- **Project Request**: "Add a login page to this react app" -> Triggers the Architect/Developer workflow.
- **Casual Question**: "What is Python?" -> Responds with a helpful answer.

---

## 📋 Commands

| Command | Action |
|---------|--------|
| `/cd <path>` | Change the factory's working directory. |
| `/list` | List all files in the current focus folder. |
| `/read <file>` | View a file with line numbers (helps with manual review). |
| `/edit <file>` | Open a specific file for AI modification. |
| `/undo` | Roll back the last code change made by the AI. |
| `/status` | Check if you are in Local or Cloud mode. |
| `/questions` | Toggle whether the AI asks clarifying questions. |

---

## 📦 Maintenance
To update to the latest version of the AI Software Factory:
```bash
pipx upgrade ai-software-factory
```

---

## 🛡️ Best Practices
- **Skills**: Add a `.md` file to the `skills/` folder to tech the AI your specific coding style.
- **Backups**: If something goes wrong, check the `.ai-factory-backups/` folder in your project root.
- **Diffs**: Always review the `diff` before typing `yes` to apply changes.

**Developed with ❤️ and optimized for the terminal.**
