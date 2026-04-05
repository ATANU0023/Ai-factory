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
- **Smart intent detection** - Only asks questions when needed
- **Clarifying questions** - Understands your requirements before building
- **Multi-agent workflow** - Architect plans, Developer codes, Auditor tests
- **Context-aware** - Analyzes existing codebase structure and style

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
git clone https://github.com/YOUR_USERNAME/ai-software-factory.git
cd ai-software-factory

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
python path/to/ai-software-factory/ai-factory.py

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
| `/ask <prompt>` | Generate without questions | `/ask Hello world` |
| `quit/exit` | Exit program | `quit` |

**Or just describe what you want:**
```
💬 You: Add logging to all functions
💬 You: Create unit tests for the API
💬 You: Refactor database queries
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

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```env
# Required
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Optional
LOG_LEVEL=INFO
ENABLE_SEMANTIC_CACHE=true
MAX_RETRIES=3
```

Get your API key at [openrouter.ai/keys](https://openrouter.ai/keys)

### Model Selection

Edit `config/settings.py` to change the LLM model:

```python
code_generation_model = ModelConfig(
    model_name="deepseek/deepseek-chat",  # or "anthropic/claude-3.5-sonnet", etc.
    max_tokens=8192,
    temperature=0.2,
)
```

See [openrouter.ai/models](https://openrouter.ai/models) for available models.

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

---

## 🆚 Comparison with Other Tools

| Feature | AI Factory | Claude Code | Cursor | GitHub Copilot |
|---------|-----------|-------------|--------|----------------|
| Cost | **FREE** | $20/mo | $20/mo | $10/mo |
| Multi-agent workflow | ✅ | ❌ | ❌ | ❌ |
| Clarifying questions | ✅ | ❌ | ❌ | ❌ |
| Auto backups | ✅ | ❌ | ❌ | ❌ |
| Undo/Redo | ✅ | ✅ | ✅ | ❌ |
| Open source | ✅ | ❌ | ❌ | ❌ |
| Self-hosted | ✅ | ❌ | ❌ | ❌ |

---

## 🛠️ Development

### Project Structure

```
ai-software-factory/
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

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/ai-software-factory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/ai-software-factory/discussions)
- **Email**: your-atanupramanik506@gmail.com
---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ star on GitHub!

---

**Made with ❤️ by ATANU PRAMANIK**
