# 🤖 AI Software Factory - Claude Code Alternative

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-purple.svg)](https://openrouter.ai/)

**A Claude Code-like AI assistant that can read, modify, and generate code in any project.** Built with hierarchical multi-agent architecture (Architect → Developer → Auditor) for production-quality software development.

---

## ✨ Features

### 🎯 Claude Code-like Interface
- **Work in ANY directory** - Navigate to any project and start coding
- **Full filesystem access** - Read, edit, and modify files anywhere
- **Directory navigation** - `/cd`, `/pwd` commands like a shell
- **Undo/Redo system** - Unlimited undo/redo for all changes
- **Automatic backups** - Every edit is backed up automatically

### 🧠 Intelligent Assistance
- **Smart intent detection** - Automatically distinguishes casual chat from project requests
- **Dual mode operation** - Switch between chat mode and build mode with `/mode`
- **Clarifying questions** - Understands your requirements before building (toggle with `/questions`)
- **Multi-agent workflow** - Architect plans, Developer codes, Auditor tests
- **Context-aware** - Analyzes existing codebase structure and style
- **Clean terminal output** - Human-readable format, no verbose JSON logs

### 🛡️ Safety First
- **Diff previews** - Review all changes before applying
- **Confirmation prompts** - Explicit approval for file modifications
- **Backup system** - Timestamped backups in `.ai-factory-backups/`
- **Graceful degradation** - Works without Docker, pytest, or other tools

### 💰 Completely Free
- Uses **OpenRouter** API (free tier available)
- No subscription fees
- No usage limits (depends on your OpenRouter quota)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13 or higher
- OpenRouter API key (free at [openrouter.ai](https://openrouter.ai/))

### Installation

```bash
# Clone the repository
git clone https://github.com/ATANU0023/Ai-factory.git
cd software-factory

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### Usage

#### Option 1: Work on Existing Project (Recommended)

```bash
# Navigate to your project
cd C:\Users\YourName\Projects\my-web-app

# Launch AI Factory
python path/to/software-factory/ai-factory.py

💬 You: /pwd
📂 Current directory: C:\Users\YourName\Projects\my-web-app

💬 You: /list
📁 Files (23):
  📄 app/main.py
  📄 app/routes.py
  ...

💬 You: Add error handling to all API endpoints

🤖 Analyzing code...
🤖 Generating modifications...
✅ Modified 3 files
```

#### Option 2: Create New Project

```bash
python ai-factory.py

💬 You: Create a Flask REST API with user authentication

🤔 Let me ask a few questions...
1. What database should I use? (SQLite/PostgreSQL/MySQL)
   💬 Your answer: SQLite

2. Include JWT authentication?
   💬 Your answer: Yes

✅ Building project...
✅ SUCCESS: Generated 12 files
```

---

## 📋 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show help message | `/help` |
| `/pwd` | Show current directory | `/pwd` |
| `/cd <path>` | Change directory | `/cd C:\Projects\app` |
| `/list` | List files | `/list` |
| `/read <file>` | View file content | `/read app.py` |
| `/edit <file>` | Edit a file | `/edit config.py` |
| `/undo` | Undo last change | `/undo` |
| `/redo` | Redo undone change | `/redo` |
| `/backups` | List backup files | `/backups` |
| `/questions` | Toggle clarifying Q&A | `/questions` |
| `/mode <type>` | Switch mode: chat or build | `/mode chat` |
| `/status` | Show current settings | `/status` |
| `/ask <prompt>` | Generate without questions | `/ask Hello world` |
| `quit/exit` | Exit program | `quit` |

### 💬 Smart Input Modes

The system intelligently detects whether you're having a conversation or requesting a project:

**Casual Conversation** (automatically detected):
```
💬 You: how are u
🤖 I'm here to help build software! What would you like to create?

💬 You: what is today's date?
🤖 Today is Monday, April 06, 2026

💬 You: what can you do?
🤖 I can generate code, modify projects, add features, fix bugs...
```

**Project Requests** (automatically detected):
```
💬 You: create a todo app
🚀 Building your project...
```

### 🔄 Mode Switching

Control how the system interprets your input:

```bash
# Chat Mode - All input treated as questions
💬 You: /mode chat
✅ Switched to CHAT mode
💬 Chat mode: All inputs treated as questions (use /ask for projects)

💬 You: tell me about Python
🤖 [Conversational response]

💬 You: /ask create a calculator
🚀 Building your project...

# Build Mode - All input treated as project requests (default)
💬 You: /mode build
✅ Switched to BUILD mode

💬 You: create a weather app
🚀 Building your project...
```

### 📊 Status Display

Check your current configuration anytime:
```
💬 You: /status

📊 Current Settings:
   Mode: BUILD
   Clarifying Questions: ON
   Working Directory: C:\Projects\my-app

💡 Use '/mode chat' for conversational mode
💡 Use '/mode build' for project building (default)
```

---

## 🏗️ Architecture

### Multi-Agent System

```
User Request
    ↓
┌─────────────┐
│  Architect   │ ← Creates detailed development plan
└──────┬──────┘
       ↓
┌─────────────┐
│  Developer   │ ← Generates code based on plan
└──────┬──────┘
       ↓
┌─────────────┐
│   Auditor    │ ← Tests and validates code
└──────┬──────┘
       ↓
   Success/Fix
```

### Technology Stack

- **LangGraph** - Agent orchestration and workflow management
- **ChromaDB** - Vector database for semantic memory and caching
- **OpenRouter** - Unified LLM API (supports DeepSeek, GPT-4, Claude, etc.)
- **Pydantic Settings** - Configuration management
- **Docker (Optional)** - Sandboxed code execution

---

## 📖 Examples

### Example 1: Modify Existing Web App

```bash
cd my-flask-project
python ai-factory.py

💬 You: Add rate limiting to all API endpoints

🤖 Reading app/routes.py...
🤖 Analyzing structure...
🤖 Generating modifications...

📋 Preview changes:
--- a/app/routes.py
+++ b/app/routes.py
@@ -5,6 +5,7 @@
 from flask import Flask
+from flask_limiter import Limiter

 @app.route('/api/users')
+@limiter.limit("100/hour")
 def get_users():
     ...

✅ Apply changes? (yes/no): yes
✅ Modified 1 file
💾 Backup created
```

### Example 2: Add New Feature

```bash
💬 You: Add user authentication with JWT

🤖 Analyzing project structure...
🤖 Checking dependencies...
🤖 Generating authentication system...

✅ Created 3 new files:
  • app/auth.py
  • app/models/user.py
  • app/routes/auth_routes.py

✅ Modified 2 files:
  • app/routes.py
  • requirements.txt
```

### Example 3: Fix Bugs

```bash
💬 You: Fix the null pointer error in user profile page

🤖 Reading app/routes.py...
🤖 Identifying issue...
🤖 Generating fix...

📋 Fix: Add null check before accessing user.avatar_url
--- a/app/routes.py
+++ b/app/routes.py
@@ -45,7 +45,7 @@
 def profile(user_id):
     user = User.query.get(user_id)
-    avatar = user.avatar_url
+    avatar = user.avatar_url if user else "/static/default.png"
     return render_template('profile.html', avatar=avatar)

✅ Apply fix? (yes/no): yes
✅ Bug fixed!
```

### Example 4: Casual Conversation

```bash
# The system automatically detects casual conversation
💬 You: how are u

🤖 I'm here to help build software! Please describe what you'd like to create.

💬 You: what can you do?

🤖 I can generate code, modify projects, add features, fix bugs, write tests, and more!
   Try asking me to build something like "Create a todo app" or "Build a REST API".

# Or switch to chat mode for extended conversations
💬 You: /mode chat
✅ Switched to CHAT mode

💬 You: explain async/await in Python
🤖 [Detailed explanation of async/await...]

💬 You: /mode build
✅ Switched to BUILD mode
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```env
# Required
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Optional - Model Configuration
# All models can be customized via environment variables
PLANNING_MODEL_NAME=deepseek/deepseek-chat
PLANNING_MODEL_MAX_TOKENS=8192
PLANNING_MODEL_TEMPERATURE=0.3

CODE_GENERATION_MODEL_NAME=deepseek/deepseek-chat
CODE_GENERATION_MODEL_MAX_TOKENS=8192
CODE_GENERATION_MODEL_TEMPERATURE=0.2

CONVERSATIONAL_MODEL_NAME=deepseek/deepseek-chat
CONVERSATIONAL_MODEL_MAX_TOKENS=500
CONVERSATIONAL_MODEL_TEMPERATURE=0.7

LOG_ANALYSIS_MODEL_NAME=meta-llama/llama-3.1-8b-instruct
LOG_ANALYSIS_MODEL_MAX_TOKENS=2048
LOG_ANALYSIS_MODEL_TEMPERATURE=0.1

SUMMARIZATION_MODEL_NAME=openai/gpt-4o-mini
SUMMARIZATION_MODEL_MAX_TOKENS=2048
SUMMARIZATION_MODEL_TEMPERATURE=0.3

# Other Settings
LOG_LEVEL=INFO
ENABLE_SEMANTIC_CACHE=true
MAX_RETRIES=3
```

Get your API key at [openrouter.ai/keys](https://openrouter.ai/keys)

### Model Selection

Models are configured in `config/settings.py` and can be overridden via environment variables:

```python
# Default configuration in settings.py
planning_model = ModelConfig(
    model_name="deepseek/deepseek-chat",
    max_tokens=8192,
    temperature=0.3,
)

# Override in .env file
PLANNING_MODEL_NAME=anthropic/claude-3.5-sonnet
PLANNING_MODEL_TEMPERATURE=0.5
```

See [openrouter.ai/models](https://openrouter.ai/models) for available models.

### Available Models

- **Planning Model**: Used for architecture design and project planning
- **Code Generation Model**: Used for writing code
- **Conversational Model**: Used for Q&A and casual chat
- **Log Analysis Model**: Used for analyzing execution logs
- **Summarization Model**: Used for creating summaries

---

## 🔒 Safety Features

### 1. Automatic Backups
Every file modification creates a timestamped backup:
```
.ai-factory-backups/
  ├── app_routes.py.1712345678.bak
  ├── config_py.1712345679.bak
  └── ...
```

### 2. Undo/Redo
```bash
💬 You: /edit main.py
[Make changes]

💬 You: /undo
✅ Undid changes to main.py

💬 You: /redo
✅ Redid changes to main.py
```

### 3. Diff Preview
All edits show unified diff before applying - review exact changes before confirming.

### 4. Confirmation Prompts
File overwrites require explicit "yes" confirmation. Cancel anytime.

### 5. Clean Terminal Output
The interactive interface uses human-readable logging:
- Only shows warnings and errors (no verbose JSON logs)
- Clean, minimal output for better user experience
- Detailed JSON logs still available for debugging (non-interactive mode)

---

## 🆚 Comparison with Other Tools

| Feature | AI Factory | Claude Code | Cursor | GitHub Copilot |
|---------|-----------|-------------|--------|----------------|
| Cost | **FREE** | $20/mo | $20/mo | $10/mo |
| Multi-agent workflow | ✅ | ❌ | ❌ | ❌ |
| Smart intent detection | ✅ | ❌ | ❌ | ❌ |
| Chat/Build modes | ✅ | ❌ | ❌ | ❌ |
| Clarifying questions | ✅ | ❌ | ❌ | ❌ |
| Auto backups | ✅ | ❌ | ❌ | ❌ |
| Undo/Redo | ✅ | ✅ | ✅ | ❌ |
| Clean terminal output | ✅ | ✅ | ✅ | N/A |
| Open source | ✅ | ❌ | ❌ | ❌ |
| Self-hosted | ✅ | ❌ | ❌ | ❌ |

---

## 🛠️ Development

### Project Structure

```
software-factory/
├── agents/              # Multi-agent system
│   ├── architect_agent.py
│   ├── developer_agent.py
│   ├── auditor_agent.py
│   └── supervisor_agent.py
├── orchestrator/        # Workflow orchestration
│   └── workflow_graph.py
├── memory/             # Vector storage & caching
│   ├── vector_store.py
│   └── semantic_cache.py
├── router/             # LLM routing & fallback
│   └── model_router.py
├── sandbox/            # Code execution (optional Docker)
│   └── docker_executor.py
├── tools/              # Utility tools
│   └── file_manager.py
├── observability/      # Logging & metrics
│   └── logger.py
├── config/             # Configuration
│   └── settings.py
├── ai-factory.py       # Main CLI interface
├── main.py             # Core factory logic
└── requirements.txt    # Dependencies
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Inspired by:
- [Claude Code](https://claude.ai/code) by Anthropic
- [Cursor](https://cursor.sh) IDE
- [GitHub Copilot Workspace](https://github.com/features/copilot)

Built with:
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Agent orchestration
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenRouter](https://openrouter.ai/) - LLM API gateway

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/ATANU0023/Ai-factory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ATANU0023/ai-factory/discussions)
- **Email**: atanupramanik506@gmail.com
---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ star on GitHub!

---

**Made with ❤️ by ATANU PRAMANIK**
