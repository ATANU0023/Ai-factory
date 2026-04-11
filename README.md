# 🤖 AI Software Factory

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Local AI](https://img.shields.io/badge/Local%20AI-Zero--Setup-green.svg)](#-zero-key-local-mode)

**A Claude Code-like AI assistant that can read, modify, and generate code in any project.** Built with a hierarchical multi-agent architecture (Architect → Developer → Auditor) for production-grade software development. 

Now featuring **Zero-Key Local Mode**—run powerful coding AI 100% privately on your CPU.

---

## ✨ Features

### 🟢 Zero-Key Local Mode (NEW)
- **High-Performance CPU Inference**: Run `Qwen2.5-Coder` directly on your machine.
- **100% Private & Offline**: Your code never leaves your computer.
- **Zero Cost**: No API keys, no subscriptions, no paywalls.
- **Optimized for v1.0.10**: Multi-threaded engine for 2-3x faster response times.

### 🎯 Claude Code-like Interface
- **Work in ANY directory**: Navigate to any project and start coding.
- **Full filesystem access**: Read, edit, and modify files anywhere.
- **Directory navigation**: `/cd`, `/pwd`, and `/list` commands built-in.
- **Undo/Redo system**: Unlimited safe-guards for your code.
- **Automatic backups**: Every edit is backed up to `.ai-factory-backups/`.

### 🧠 Intelligent Assistance
- **Smart intent detection**: Automatically distinguishes casual chat from project requests.
- **Clarifying questions**: Understands your requirements before writing a single line of code.
- **Multi-agent workflow**: Architect plans, Developer codes, Auditor reviews.
- **Dynamic Skills Injection**: Instantly teach agents new rules by adding `.md` files to the `skills/` directory.

---

## ⚡ Quick Start (Global Install)

The fastest and most seamless way to install the AI Software Factory on Windows is our one-line installer:

```powershell
# Open Windows PowerShell and paste this:
irm https://raw.githubusercontent.com/ATANU0023/Ai-factory/main/install.ps1 | iex
```

### Manual Installation (Any OS)
```bash
# 1. Install the base package
pipx install ai-software-factory

# 2. Enable Local AI support (Optional, for Zero-Key use)
pip install "ai-software-factory[local]"

# 3. Launch
ai-factory
```

---

## 📋 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/auth` | Switch between Local vs Cloud mode | `/auth` |
| `/pwd` | Show current directory | `/pwd` |
| `/cd <path>` | Change directory | `/cd ./src/app` |
| `/list` | List files in current project | `/list` |
| `/read <file>` | View file content with line numbers | `/read app.py` |
| `/edit <file>` | Open the interactive file editor | `/edit config.py` |
| `/undo` | Revert the last code change | `/undo` |
| `/mode <type>` | Switch between 'chat' and 'build' | `/mode chat` |
| `quit/exit` | Exit the factory | `exit` |

---

## 🏗️ Architecture

AI Factory uses **LangGraph** to orchestrate a specialized team of agents:

1.  **Architect**: Analyzes requirements and drafts a comprehensive file-by-file plan.
2.  **Developer**: Executes the plan, writing precise, production-grade code.
3.  **Auditor**: Reviews the changes, runs checks, and ensures everything matches the plan.

---

## 🛡️ Safety & Privacy
- **Previews**: Unified diff preview before any changes are written.
- **Backups**: Every edit creates a timestamped backup automatically.
- **Sandbox (Optional)**: Support for Docker execution for untrusted code.

---

## 📝 License
MIT License - See [LICENSE](LICENSE) file for details.

**Made with ❤️ by ATANU PRAMANIK**
