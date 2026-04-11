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

## ✨ Features

### 🟢 Zero-Key Local Mode
Run high-quality coding AI directly on your CPU. Completely free, private, and works 100% offline. Ideal for low-end systems or secure environments. **Optimized in v1.0.11** for multi-threaded performance.

### 🎯 Claude Code-like Interface
- **Work in ANY directory**: Navigate to any project and start coding.
- **Unlimited Undo**: Messed up? Just type `/undo`. Every change is automatically backed up.
- **Preview Diffs**: Review every line of code before it's written to your disk.
- **Interactive Shell**: Navigate and code with `/cd`, `/read`, `/edit`, and `/list`.

### 🧠 Dynamic Skills Injection
Instantly teach the agent new rules by adding `.md` files to the `skills/` folder. Want it to always use TailwindCSS or follow Clean Architecture? Just drop a file in.

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
| `/auth` | Configure Local vs Cloud mode | `/auth` |
| `/pwd` | Show current directory | `/pwd` |
| `/cd <path>` | Change the factory's working directory | `/cd ./src/app` |
| `/list` | List files in the current focus folder | `/list` |
| `/read <file>` | View a file with line numbers | `/read main.py` |
| `/edit <file>` | Open the interactive file editor | `/edit config.py` |
| `/undo` | Revert the last code change | `/undo` |
| `/redo` | Redo a previously undone change | `/redo` |
| `/status` | Show current mode and settings | `/status` |
| `/questions`| Toggle clarifying questions (ON/OFF) | `/questions` |
| `quit/exit` | Exit the factory | `exit` |

---

## 📖 Examples

### 1. Adding a Feature to an Existing Project
```bash
cd my-react-app
ai-factory

💬 You: Add a dark mode toggle to the Navbar component
🤖 Reading src/components/Navbar.tsx...
🤖 Modifying files...

📋 Preview changes:
+ import { Moon, Sun } from 'lucide-react';
+ const [theme, setTheme] = useState('light');
...
✅ Apply changes? (yes/no): yes
✅ Modified 2 files | 💾 Backup created
```

### 2. Fixing a Bug
```bash
💬 You: Fix the null pointer error in the user profile page
🤖 Locating issue...
🤖 Found: user.avatar_url accessed without null check in src/Profile.js
🤖 Applying fix...
```

---

## 🏗️ Architecture

AI Factory uses **LangGraph** to orchestrate a specialized team of agents:

1.  **Architect**: Analyzes requirements and drafts a comprehensive file-by-file plan.
2.  **Developer**: Executes the plan, writing precise, production-grade code.
3.  **Auditor**: Reviews the changes, runs checks (linting/tests), and ensures quality.

---

## 🆚 Comparison

| Feature | AI Factory | Claude Code | Cursor |
|---------|------------|-------------|--------|
| **Cost** | **FREE** | Paid Tier | Paid Tier |
| **Offline** | ✅ | ❌ | ❌ |
| **Local AI** | ✅ | ❌ | ❌ |
| **Auto-Backups**| ✅ | ✅ | ❌ |
| **Multi-Agent** | ✅ | ❌ | ❌ |

---

## 📝 License
MIT License - See [LICENSE](LICENSE) file for details.

**Made with ❤️ by ATANU PRAMANIK**
