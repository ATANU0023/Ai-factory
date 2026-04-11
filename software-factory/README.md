# 🤖 AI Software Factory

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Local AI](https://img.shields.io/badge/Local%20AI-Zero--Setup-green.svg)](#-zero-key-local-mode)

**A high-performance, frictionless AI Coding Assistant.** Built to run anywhere—from high-end cloud GPUs to low-end laptops—with completely free, private, and offline-capable architecture.

---

## 🚀 Why AI Factory?

Most AI coding tools require expensive subscriptions or proprietary API keys. **AI Factory is different.** It is designed to "just work" for everyone, immediately.

- **Zero-Key Setup**: Use our built-in local model (`Qwen2.5-Coder`). No credit card, no API key, and no GPU required.
- **Hierarchical Multi-Agent**: Not just a chatbot. It uses a professional **Architect → Developer → Auditor** workflow to ensure production-quality code.
- **Filesystem Power**: It can read, edit, refactor, and create files across your entire project with a simple command.
- **Smart Context**: Automatically analyzes your project structure to understand your coding style and dependencies.

---

## ✨ Key Features

### 🟢 Zero-Key Local Mode
Run high-quality coding AI directly on your CPU. Completely free, private, and works 100% offline. Ideal for low-end systems or secure environments.

### 🔵 Fast Cloud Mode
Upgrade to Cloud Mode in seconds using a free OpenRouter key. Access the world's most powerful models like Claude 3.5 Sonnet, GPT-4o, and DeepSeek-V3.

### 🛠️ Production-Ready CLI
- **Interactive Shell**: Navigate and code with `/cd`, `/read`, `/edit`, and `/list`.
- **Unlimited Undo**: Messed up? Just type `/undo`. Every change is automatically backed up.
- **Clarifying Q&A**: The agent asks questions before starting complex tasks to ensure it gets the requirements right.
- **Skill Injection**: Instantly teach the agent new rules by adding `.md` files to the `skills/` folder.

---

## ⚡ Quick Start (Global Install)

The fastest way to install AI Factory locally on Windows is our one-line installer:

```powershell
# Run in PowerShell (Sets up Python, pipx, and paths automatically)
irm https://raw.githubusercontent.com/ATANU0023/Ai-factory/main/install.ps1 | iex
```

### Manual Installation (Any OS)
```bash
# 1. Install the base package
pipx install ai-software-factory

# 2. Add Local AI support (Optional, for offline/zero-key use)
pip install "ai-software-factory[local]"

# 3. Launch the factory
ai-factory
```

---

## 📋 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/auth` | Configure Local vs Cloud mode | `/auth` |
| `/cd <path>`| Change working directory | `/cd ./src/app` |
| `/read <file>`| View file content with line numbers | `/read main.py` |
| `/edit <file>`| Open the interactive file editor | `/edit config.py` |
| `/undo` | Revert the last change | `/undo` |
| `/questions`| Toggle clarifying questions (ON/OFF)| `/questions` |
| `/mode` | Switch between 'chat' and 'build' | `/mode chat` |
| `quit` | Exit the factory | `exit` |

---

## 🏗️ Architecture

AI Factory uses **LangGraph** to orchestrate a specialized team of agents:

1.  **Architect**: Analyzes requirements and drafts a comprehensive file-by-file plan.
2.  **Developer**: Executes the plan, writing precise, production-grade code.
3.  **Auditor**: Reviews the changes, runs checks, and ensures everything matches the plan.

---

## 🛡️ Safety & Privacy

- **Local First**: Files are never sent to the cloud when using Local Mode.
- **Backups**: Every edit creates a timestamped backup in `.ai-factory-backups/`.
- **Previews**: You always see a `diff` preview before any changes are written to disk.

---

## 🧠 Customizing Your Factory

You can define custom coding standards or project rules by adding Markdown files to the `skills/` directory.

**Example `skills/my_rules.md`**:
```markdown
# My Project Rules
- Always use TypeScript for new files.
- Use functional components instead of class components.
- Wrap all API calls in a try/catch block.
```

---

## 📝 License
MIT License - See [LICENSE](LICENSE) file for details.

**Made with ❤️ by ATANU PRAMANIK**
