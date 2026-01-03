---
description: Continue working on the next todo item from todo.json (project)
---

Read todo.json and find the next task where "done": false.

For that task, follow this step-by-step workflow:

## Step 1: Present the Task
- Show the **Milestone** name and **Task** name
- List the files that will be created/modified
- Explain what this task involves and why it matters

## Step 2: Discuss the Approach
- Explain how you plan to implement it
- Mention any design decisions or trade-offs
- Highlight any dependencies on other modules

## Step 3: Wait for Approval
Ask: "Does this approach sound good? Any questions before I proceed?"
**Do NOT write any code until the user confirms.**

## Step 4: Implement
After user approval:
- Create/modify the files listed in "files"
- Write tests alongside implementation
- Follow the patterns defined in CLAUDE.md

## Step 5: Show What Was Done
- Summarize the changes made
- Show key code snippets if helpful
- Mark the task as "done": true in todo.json
- **Stop and wait for user to run `/continue` again for the next task**

---

Important: Only process ONE task per `/continue` command. The user will run `/continue` again when ready for the next task.