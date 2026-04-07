"""AI Software Factory - Interactive CLI Interface (Claude Code-like)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_software_factory.main import run_factory
from ai_software_factory.agents.architect_agent import ArchitectAgent
from ai_software_factory.router.model_router import ModelRouter
from ai_software_factory.memory.semantic_cache import SemanticCache
from ai_software_factory.tools.file_manager import FileManager
from ai_software_factory.observability.logger import get_logger

# Use interactive mode for cleaner output
logger = get_logger(__name__, interactive=True)


def _is_project_request(user_input: str) -> bool:
    """Check if input is a project request or general question."""
    text = user_input.lower().strip()
    
    # Casual greetings/conversation patterns
    casual_patterns = [
        "hi", "hello", "hey", "greetings", "howdy",
        "how are you", "how r u", "how are u", "whats up", "what's up",
        "thank", "thanks", "bye", "goodbye",
        "test", "testing",
    ]
    
    # Check if it's just a greeting or casual chat
    if any(pattern in text for pattern in casual_patterns):
        # But allow if it also contains project keywords
        project_keywords = [
            "create", "build", "make", "develop", "design",
            "app", "application", "website", "api", "system",
            "program", "software", "tool", "service",
        ]
        
        has_project_keyword = any(keyword in text for keyword in project_keywords)
        if not has_project_keyword:
            return False
    
    # Project requests have action verbs
    project_verbs = ["create", "build", "make", "develop", "design", "implement"]
    return any(verb in text for verb in project_verbs)


def _handle_conversational_query(query: str):
    """Handle general questions conversationally using LLM."""
    print("\n🤖 Thinking...")
    
    try:
        from openai import OpenAI
        from config.settings import settings
        from datetime import datetime
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        
        # Get current date and time for context
        current_datetime = datetime.now()
        current_date_str = current_datetime.strftime("%A, %B %d, %Y")
        current_time_str = current_datetime.strftime("%I:%M %p")
        
        system_prompt = f"""You are a helpful AI Software Factory assistant.
Answer questions about your capabilities concisely and friendly.

Current Context:
- Today's Date: {current_date_str}
- Current Time: {current_time_str}

Key capabilities:
- Generate code in any programming language
- Modify existing projects (navigate with /cd)
- Read, edit, and refactor code
- Add features, fix bugs, write tests
- Undo/redo changes with automatic backups
- Ask clarifying questions for complex projects

Keep responses brief and actionable.
If asked about current date/time, use the context provided above."""

        # Use configured conversational model from settings
        conv_model = settings.conversational_model
        
        response = client.chat.completions.create(
            model=conv_model.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=conv_model.temperature,
            max_tokens=conv_model.max_tokens,
        )
        
        answer = response.choices[0].message.content or ""
        
        print("\n" + "=" * 80)
        print("💡 Answer:")
        print("=" * 80)
        print(answer)
        print("=" * 80)
        print("\n💬 Try asking me to build something!")
        
    except Exception as e:
        logger.error(f"Conversational query failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\n💡 Try a project request like 'Create a todo app'")


def print_banner():
    """Print welcome banner with ASCII art."""
    print("=" * 80)
    print("""
 █████╗ ██╗    ███████╗ █████╗  ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
██╔══██╗██║    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
███████║██║    █████╗  ███████║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ 
██╔══██║██║    ██╔══╝  ██╔══██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  
██║  ██║██║    ██║     ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   
╚═╝  ╚═╝╚═╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   

                
""")
    print("=" * 80)
    print("\nCommands:")
    print("  /ask <question>     - Ask me to generate code")
    print("  /edit <file>        - Edit an existing file")
    print("  /read <file>        - Read a file")
    print("  /list               - List all files in current directory")
    print("  /cd <path>          - Change working directory")
    print("  /pwd                - Show current directory")
    print("  /undo               - Undo last change")
    print("  /redo               - Redo last undone change")
    print("  /backups            - List backup files")
    print("  /questions          - Toggle clarifying questions on/off")
    print("  /mode <type>        - Switch mode: 'chat' or 'build'")
    print("  /status             - Show current settings")
    print("  /help               - Show this help message")
    print("  quit/exit           - Exit the program")
    print("\nOr just describe your project and I'll build it!")
    print("=" * 80)


def ask_clarifying_questions(user_input: str) -> dict:
    """Ask user clarifying questions before building."""
    
    # Initialize architect to check if questions are needed
    semantic_cache = SemanticCache()
    model_router = ModelRouter(session_id="cli-interactive", semantic_cache=semantic_cache)
    architect = ArchitectAgent(model_router=model_router, session_id="cli-interactive")
    
    questions = architect.generate_clarifying_questions(user_input)
    
    # If no questions (casual chat or simple request), skip Q&A
    if not questions:
        return {}
    
    print("\n" + "=" * 80)
    print("🤔 Let me ask a few questions to understand your requirements better...")
    print("=" * 80 + "\n")
    
    answers = {}
    for i, question in enumerate(questions, 1):
        answer = input(f"\n{i}. {question}\n   💬 Your answer (or press Enter to skip): ").strip()
        if answer:
            answers[question] = answer
    
    if answers:
        print(f"\n✅ Thanks! Collected {len(answers)} clarification(s)")
    else:
        print("\n⚠️  Skipping clarifications, proceeding with defaults...")
    
    return answers


def handle_edit_command(file_manager: FileManager, args: str):
    """Handle /edit command."""
    if not args:
        print("❌ Usage: /edit <filename>")
        return
    
    file_path = args.strip()
    
    # Check if file exists
    info = file_manager.get_file_info(file_path)
    if not info.get("exists"):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"\n📄 Reading {file_path}...")
    content = file_manager.read_file(file_path)
    print(f"Current size: {len(content)} characters\n")
    
    # Show first 500 chars as preview
    preview_lines = content.split('\n')[:20]
    print("Preview (first 20 lines):")
    print("-" * 80)
    for i, line in enumerate(preview_lines, 1):
        print(f"{i:3d} | {line}")
    if len(content.split('\n')) > 20:
        print(f"... ({len(content.split(chr(10))) - 20} more lines)")
    print("-" * 80)
    
    # Ask for edit type
    print("\nEdit options:")
    print("  1. Search and replace text")
    print("  2. Rewrite entire file")
    print("  3. Cancel")
    
    choice = input("\nChoose option (1/2/3): ").strip()
    
    if choice == "1":
        search_text = input("\n🔍 Text to find: ")
        replace_text = input("✏️  Replace with: ")
        
        result = file_manager.edit_file(file_path, search_text, replace_text)
        
        if result["action"] == "preview_ready":
            print("\n" + "=" * 80)
            print("📋 Preview of changes:")
            print("=" * 80)
            print(result["diff"])
            print("=" * 80)
            
            confirm = input("\n✅ Apply these changes? (yes/no): ").strip().lower()
            if confirm in ["yes", "y"]:
                apply_result = file_manager.apply_edit(file_path, result["new_content"])
                print(f"\n{apply_result['message']}")
            else:
                print("\n❌ Changes cancelled")
        else:
            print(f"\n❌ {result['message']}")
    
    elif choice == "2":
        print("\n✏️  Paste new content (type 'END' on a new line when done):")
        print("-" * 80)
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        
        new_content = "\n".join(lines)
        result = file_manager.write_file(file_path, new_content, confirm=False)
        print(f"\n{result['message']}")
    
    else:
        print("\n❌ Edit cancelled")


def handle_read_command(file_manager: FileManager, args: str):
    """Handle /read command."""
    if not args:
        print("❌ Usage: /read <filename>")
        return
    
    file_path = args.strip()
    content = file_manager.read_file(file_path)
    
    if not content:
        print(f"❌ File not found or empty: {file_path}")
        return
    
    print(f"\n📄 {file_path} ({len(content)} chars):\n")
    print("=" * 80)
    
    # Show content with line numbers
    for i, line in enumerate(content.split('\n'), 1):
        print(f"{i:4d} | {line}")
    
    print("=" * 80)


def handle_list_command(file_manager: FileManager):
    """Handle /list command."""
    files = file_manager.list_files()
    
    if not files:
        print("\n📁 No files in current directory")
        return
    
    print(f"\n📁 Files in {file_manager.base_dir} ({len(files)}):\n")
    for file_path in files:
        info = file_manager.get_file_info(file_path)
        size_kb = info.get("size", 0) / 1024
        print(f"  📄 {file_path:<50s} ({size_kb:.1f} KB)")


def handle_cd_command(file_manager: FileManager, args: str):
    """Handle /cd command."""
    if not args:
        print(f"📂 Current directory: {file_manager.base_dir}")
        return
    
    result = file_manager.change_directory(args.strip())
    if result["success"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")


def handle_pwd_command(file_manager: FileManager):
    """Handle /pwd command."""
    print(f"📂 Current directory: {file_manager.base_dir}")


def handle_undo_command(file_manager: FileManager):
    """Handle /undo command."""
    result = file_manager.undo()
    if result["success"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")


def handle_redo_command(file_manager: FileManager):
    """Handle /redo command."""
    result = file_manager.redo()
    if result["success"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")


def handle_backups_command(file_manager: FileManager):
    """Handle /backups command."""
    backups = file_manager.list_backups()
    
    if not backups:
        print("\n💾 No backups found")
        return
    
    print(f"\n💾 Backup files ({len(backups)}):\n")
    for backup in backups[:20]:  # Show first 20
        print(f"  • {backup}")
    if len(backups) > 20:
        print(f"  ... and {len(backups) - 20} more")


def interactive_mode():
    """Run in interactive mode like Claude Code."""
    print_banner()
    
    # Initialize components
    file_manager = FileManager("./output")
    ask_questions = True  # Default: ask clarifying questions
    current_mode = "build"  # Default mode: 'build' or 'chat'
    
    print("\n💡 Tip: Type '/help' for available commands\n")
    print(f"📊 Current mode: {current_mode.upper()} | Clarifying questions: {'ON' if ask_questions else 'OFF'}")
    
    while True:
        try:
            prompt = input("\n💬 You: ").strip()
            
            if not prompt:
                continue
            
            # Handle commands
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            elif prompt.lower() == '/help':
                print_banner()
                continue
            
            elif prompt.startswith('/edit'):
                handle_edit_command(file_manager, prompt[5:])
                continue
            
            elif prompt.startswith('/read'):
                handle_read_command(file_manager, prompt[5:])
                continue
            
            elif prompt.lower() == '/list':
                handle_list_command(file_manager)
                continue
            
            elif prompt.startswith('/cd'):
                handle_cd_command(file_manager, prompt[3:])
                continue
            
            elif prompt.lower() == '/pwd':
                handle_pwd_command(file_manager)
                continue
            
            elif prompt.lower() == '/undo':
                handle_undo_command(file_manager)
                continue
            
            elif prompt.lower() == '/redo':
                handle_redo_command(file_manager)
                continue
            
            elif prompt.lower() == '/backups':
                handle_backups_command(file_manager)
                continue
            
            elif prompt.lower() == '/status':
                print(f"\n📊 Current Settings:")
                print(f"   Mode: {current_mode.upper()}")
                print(f"   Clarifying Questions: {'ON' if ask_questions else 'OFF'}")
                print(f"   Working Directory: {file_manager.base_dir}")
                print(f"\n💡 Use '/mode chat' for conversational mode")
                print(f"💡 Use '/mode build' for project building (default)")
                continue
            
            elif prompt.lower() == '/questions':
                ask_questions = not ask_questions
                status = "enabled" if ask_questions else "disabled"
                print(f"✅ Clarifying questions {status}")
                print(f"📊 Current mode: {current_mode.upper()} | Clarifying questions: {'ON' if ask_questions else 'OFF'}")
                continue
            
            elif prompt.startswith('/mode'):
                # Switch between chat and build modes
                args = prompt[5:].strip().lower()
                if args in ['chat', 'build']:
                    current_mode = args
                    print(f"✅ Switched to {current_mode.upper()} mode")
                    if current_mode == 'chat':
                        print("💬 Chat mode: All inputs treated as questions (use /ask for projects)")
                    else:
                        print("🔨 Build mode: All inputs treated as project requests")
                    print(f"📊 Current mode: {current_mode.upper()} | Clarifying questions: {'ON' if ask_questions else 'OFF'}")
                else:
                    print("❌ Usage: /mode <chat|build>")
                    print("   chat - Treat all input as conversational questions")
                    print("   build - Treat all input as project requests (default)")
                continue
            
            elif prompt.startswith('/ask'):
                # Direct question - handle conversationally, not as project
                user_input = prompt[4:].strip()
                
                # Check if it's a general question (not a project request)
                if not _is_project_request(user_input):
                    # Handle as conversational query
                    _handle_conversational_query(user_input)
                    continue
                
                clarifications = {}
            else:
                # Normal input - behavior depends on current mode
                user_input = prompt
                clarifications = {}
                
                # In chat mode, treat everything as conversational unless it has project verbs
                if current_mode == 'chat':
                    if not _is_project_request(user_input):
                        _handle_conversational_query(user_input)
                        continue
                else:
                    # Build mode: Early check for casual conversation
                    if not _is_project_request(user_input):
                        _handle_conversational_query(user_input)
                        continue
                
                # Ask clarifying questions if enabled
                if ask_questions:
                    clarifications = ask_clarifying_questions(user_input)
            
            # Build the project
            print("\n🚀 Building your project...\n")
            print("-" * 80)
            
            result = run_factory(user_input, "./output", clarifications)
            
            print("-" * 80)
            
            # Display results
            status = result.get("final_status", "unknown")
            if status == "success":
                files = result.get("generated_files", [])
                print(f"\n✅ SUCCESS: Generated {len(files)} file(s)")
                
                # Show file list
                if files:
                    print("\n📁 Files created:")
                    for f in files[:10]:  # Show first 10
                        print(f"  • {f}")
                    if len(files) > 10:
                        print(f"  ... and {len(files) - 10} more")
                
                print("\n💡 Tips:")
                print("  • Use '/list' to see all files")
                print("  • Use '/read <file>' to view a file")
                print("  • Use '/edit <file>' to modify a file")
                print("  • Describe another project to continue")
            
            elif status == "failed":
                error = result.get("error", "Unknown error")
                print(f"\n❌ FAILED: {error}")
                print("\n💡 Try rephrasing your request or use simpler requirements")
            
            else:
                print(f"\n⚠️  Status: {status}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
            print("💡 Try again or type '/help' for assistance")


def one_shot_mode(description: str):
    """Run in one-shot mode (non-interactive)."""
    print(f"🚀 Building: {description}\n")
    
    result = run_factory(description, "./output")
    
    status = result.get("final_status", "unknown")
    if status == "success":
        files = result.get("generated_files", [])
        print(f"\n✅ SUCCESS: Generated {len(files)} file(s) in ./output/")
    else:
        error = result.get("error", "Unknown error")
        print(f"\n❌ FAILED: {error}")


def cli_main():
    """CLI entry point for the PyPI package."""
    if len(sys.argv) > 1:
        # One-shot mode
        description = " ".join(sys.argv[1:])
        one_shot_mode(description)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    cli_main()
