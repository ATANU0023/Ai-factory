# 🤖 AI Software Factory (Core)

**The core engine behind the AI Software Factory.** This package handles agent orchestration, local LLM inference, and filesystem management.

---

## 🛠️ Technical Overview

### Directory Structure
- **`agents/`**: Core multi-agent logic (Architect, Developer, Auditor).
- **`router/`**: Model routing system with fallback and Local LLM (Llama-cpp) support.
- **`memory/`**: Semantic cache (ChromaDB) and Skill Manager.
- **`tools/`**: Filesystem tools, diff generators, and backup managers.
- **`observability/`**: Human-readable logging and performance metrics.
- **`config/`**: Pydantic-based settings for Local vs Cloud operation.

---

## 🚀 Version 1.0.11
- **💨 Optimized Local Mode**: Multi-threaded core allocation for CPU.
- **✨ Clean Console**: Silenced JSON technical logs for CLI interactions.
- **📍 Direct Filesystem Focus**: Edits files in-place within your active directory.

---

## 📦 Developer Setup (Local)
To modify the core engine:
```bash
git clone https://github.com/ATANU0023/Ai-factory
cd software-factory
pip install -e .[local,dev]
```

---

## 🛡️ Best Practices
1. **Always Review Diffs**: The UI provides a full diff before writing—check it!
2. **Use Skills**: Place `.md` files in the `skills/` folder to guide the AI's behavior.
3. **Check Backups**: Revert any mistakes using `/undo` or by checking `.ai-factory-backups/`.

**Developed by ATANU PRAMANIK**
