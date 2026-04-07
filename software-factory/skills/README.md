# Skills Directory

This directory contains Markdown (`.md`) files that define specific skills, rules, and guidelines for the autonomous agents in the AI factory. 

Every time the agents process a request, they will read all `.md` files in this directory (except this `README.md`) and inject their contents into the system prompt. This allows you to dynamically extend the capabilities and enforce coding standards for the agents without modifying their core code.

## How to add a new skill

1. Create a new `.md` file in this directory (e.g., `modern_ui_design.md`).
2. Write clear instructions, guidelines, and rules in the file.
3. Your agents will automatically pick up and apply the skill in their next operation!
