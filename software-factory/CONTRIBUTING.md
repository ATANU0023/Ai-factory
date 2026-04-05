# Contributing to AI Software Factory

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🎯 Ways to Contribute

- **Report bugs** - Create an issue with detailed reproduction steps
- **Suggest features** - Open a discussion or feature request issue
- **Improve documentation** - Fix typos, add examples, clarify explanations
- **Write code** - Fix bugs, implement features, improve performance
- **Share examples** - Show how you're using the project

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/ai-software-factory.git
cd ai-software-factory
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-cov black isort mypy
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

## 📝 Code Style

### Python Standards

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints for all functions
- Write docstrings for all public methods
- Maximum line length: 100 characters

### Formatting

We use Black for code formatting:

```bash
# Format code
black .

# Check formatting
black --check .
```

### Type Checking

```bash
# Run mypy
mypy .
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

Example:

```python
def test_architect_generates_plan():
    """Test that architect agent generates valid development plan."""
    # Arrange
    architect = ArchitectAgent(model_router=mock_router)
    
    # Act
    result = architect.execute({"user_input": "Create a todo app"})
    
    # Assert
    assert result["architect_plan"] is not None
    assert "files" in result["architect_plan"]
```

## 📋 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Commit messages are clear

### 2. Commit Messages

Use conventional commits format:

```
feat: add undo/redo functionality
fix: resolve cache corruption issue
docs: update README with examples
test: add integration tests for auditor
refactor: simplify workflow graph logic
```

### 3. Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
```

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Enter input '....'
3. See error

**Expected behavior**
What should happen

**Screenshots/Logs**
If applicable, add logs or screenshots

**Environment:**
- OS: Windows/Linux/MacOS
- Python version: 3.13
- Package versions: (from requirements.txt)

**Additional context**
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature related to a problem?**
Description of the problem

**Describe the solution**
What you want to happen

**Describe alternatives**
Other solutions you've considered

**Additional context**
Mockups, examples, or references
```

## 📚 Documentation Guidelines

### README Updates

- Keep examples up-to-date
- Test all code snippets
- Use clear, concise language
- Include screenshots/GIFs for UI changes

### Code Comments

- Explain WHY, not WHAT
- Document edge cases
- Reference issues/PRs when relevant
- Keep comments current with code

## 🎨 Design Principles

1. **User-first** - Prioritize user experience
2. **Safety** - Never lose user data
3. **Transparency** - Show what's happening
4. **Flexibility** - Work in diverse environments
5. **Performance** - Fast and efficient

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Give constructive feedback
- Celebrate contributions

## ❓ Questions?

- Open a [GitHub Discussion](https://github.com/YOUR_USERNAME/ai-software-factory/discussions)
- Email: your-email@example.com

---

Thank you for contributing! 🎉
