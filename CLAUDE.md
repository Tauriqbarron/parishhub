# Parish Database - Claude Code Instructions

## Interaction Rules
- **NO CHAT:** Do not reply with conversational text. Output only tool uses or final confirmation.
- **NO SUMMARIES:** Do not summarize changes after editing.
- **COMPACT:** If listing files, list only relevant ones.
- **CONTEXT:** Do not read `node_modules`, `venv`, `package-lock.json`, `.svelte-kit`, or `__pycache__`.

## Background Task Behavior
- **Auto-Poll:** When running background tasks, poll for completion and report results immediately - do NOT wait for user to ask.
- **Task Tracking:** Store task IDs and check TaskOutput periodically until complete.
- **Immediate Reporting:** When a background task finishes, summarize results in the next response.

## Project Details & Basic Memory (AUTO-LOAD)

Architecture, stack, workflow patterns, deployment setup, and test/verification rules are stored in **basic-memory** under the `parish-database` project.

### Session Startup (MANDATORY)

At the **start of every session**, before doing any work:

1. Run `build_context` for the `parish-database` project to load all stored knowledge.
2. Run `search_notes` with broad queries (e.g., "architecture", "deployment", "stack", "conventions", "testing") to surface relevant context.

### Ongoing Usage

- **Before any task**, proactively search basic-memory for topics related to the request — do NOT wait for the user to ask.
- **Key topics to always check:** deployment, architecture, stack, database, CI/CD, testing, conventions, infrastructure.
- **After learning new project information**, save it to basic-memory so future sessions have it.
- The user should NEVER need to prompt you to check basic-memory — treat it as your persistent project knowledge base.
