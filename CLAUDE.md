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

## Project Details
Architecture, stack, workflow patterns, and test/verification rules are stored in **basic-memory** under the `parish-database` project. Query basic-memory for these details when needed.
