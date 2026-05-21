---
name: debug-claude-hooks
description: Systematically debug Claude Code hook registration and execution failures. Use this skill whenever hooks don't fire, don't register, or behave unexpectedly — including quoting issues, silent failures, and experimental hook types.
when_to_use: |
  Trigger when Claude Code hooks are not registering, not firing, or producing
  unexpected results. Also trigger when creating new hooks and wanting to avoid
  common pitfalls.
  Example user phrases:
  - "my hook isn't running"
  - "hooks.json doesn't seem to work"
  - "PostToolUse hook not firing"
  - "agent hook silently fails"
paths: ["**/*"]
allowed-tools: Read Bash Edit Write Grep Glob
version: "1.0.0"
---

# Debug Claude Code Hooks

Structured workflow for diagnosing Claude Code hook registration and execution
failures. Hook problems are notoriously silent — no error messages, no logs —
so this skill provides a systematic approach: verify docs first, isolate with
diagnostics, check quoting, test one hook at a time, and flag known
experimental limitations.

## When to use

- Hooks in `hooks.json` (project or plugin) don't seem to register or fire
- A hook fires but behaves differently than expected
- You're setting up hooks for the first time and want to avoid common mistakes
- A specific hook type (e.g., `Agent`) silently does nothing

**Anti-patterns** (this skill is the wrong tool when):
- You're asking *how to write* a hook from scratch (use `claude-code-reference` skill to fetch official docs)
- The hook script itself has a logic bug unrelated to registration (standard debugging suffices)

## Steps

1. **Fetch official documentation before assuming anything.** Use the
   `claude-code-reference` skill or fetch directly from
   `https://code.claude.com/docs/en/hooks.md` and
   `https://code.claude.com/docs/en/hooks-guide.md`. Hook types, configuration
   format, and supported features change across Claude Code versions. Do not
   rely solely on training data — verify the current schema and supported hook
   types against live docs.

2. **Create a minimal diagnostic script.** Write a tiny shell script that
   records whether the hook runner reaches it, what environment variables are
   set, and what stdin contains. This isolates whether the problem is
   registration (hook never called) vs. execution (hook called but fails).

   Example diagnostic script:
   ```bash
   #!/usr/bin/env bash
   DIAG_LOG="/tmp/hook-diag-$(date +%s).log"
   echo "=== Hook fired at $(date) ===" >> "$DIAG_LOG"
   echo "HOOK_TYPE=$1" >> "$DIAG_LOG"
   env | grep -i claude >> "$DIAG_LOG" 2>&1 || true
   cat >> "$DIAG_LOG"  # capture stdin payload
   ```
   Wire this script into the hook entry in `hooks.json` to confirm the hook
   runner reaches your script at all.

3. **Verify command path quoting in hooks.json.** The most common registration
   failure is incorrect quoting of the `CLAUDE_PLUGIN_ROOT` or
   `CLAUDE_PROJECT_ROOT` variable in the `command` field. Prefer unquoted
   variable references:

   **Bad** (escaped quotes break the command path):
   ```json
   "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/hook.sh"
   ```

   **Good** (no extra quoting):
   ```json
   "command": "${CLAUDE_PLUGIN_ROOT}/scripts/hook.sh"
   ```

   The hook runner expands variables itself — wrapping them in escaped quotes
   produces a literal `"` character in the path, causing a silent failure.

4. **Test each hook type individually.** Do not register multiple hooks at once
   and hope they all work. Add one hook entry, verify it fires with the
   diagnostic script, then add the next. This isolates which specific hook type
   or configuration is failing. Test order: `PostToolUse` (easiest to trigger),
   then `PreToolUse`, then `Stop`, then `Agent`.

5. **Flag experimental and silently-failing features.** As of 2026-05, the
   `Agent` hook type (`type: "agent"`) is officially documented as supported but
   may silently fail when defined in a *plugin* `hooks.json` (it works in
   project-level `.claude/settings.json`). Document such limitations clearly so
   you don't waste time re-diagnosing a known gap. If a hook type is marked
   "experimental" in the official docs, assume it may have reduced
   functionality in plugin contexts.

6. **Validate hooks.json syntax.** A malformed JSON file causes all hooks to
   silently not load. Run `cat hooks.json | python3 -m json.tool` or equivalent
   to confirm valid JSON. Check for trailing commas, unescaped characters, and
   correct nesting under the `hooks` key.

## Example

**Scenario**: A developer adds a `PostToolUse` hook in their plugin's
`hooks.json` to run a security scan after every tool call, but the hook never
fires.

**Walkthrough**:
1. Fetch `hooks.md` from official docs — confirm `PostToolUse` is a valid
   hook type and the configuration schema matches.
2. Create `diag-hook.sh` that logs timestamp and environment to `/tmp/hook-diag.log`,
   wire it into the `command` field temporarily.
3. Run a tool call (e.g., Read a file) and check `/tmp/hook-diag.log`. Nothing
   appears — the hook runner never called the script, so the problem is
   registration, not the script itself.
4. Inspect `hooks.json` — find `"command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/diag-hook.sh"`.
   The escaped quotes around the variable are producing a bad path. Change to
   `"command": "${CLAUDE_PLUGIN_ROOT}/scripts/diag-hook.sh"`.
5. Run another tool call — the diagnostic log appears. Replace the diagnostic
   script with the real security scan script. Verified working.

**Outcome**: Hook fires reliably after every tool call; root cause was
escaped-quote variable expansion in the command path.

## Common pitfalls

- **Escaped quotes around variables**: The `command` field in `hooks.json` is
  not a shell string — it is parsed by the hook runner directly. Adding
  `\"...\"` around `${CLAUDE_PLUGIN_ROOT}` creates a literal quote in the path
  and the file is not found. Use bare variable references.

- **Silent failures with no feedback**: Hook registration problems produce no
  error messages or warnings. The hook simply doesn't run. Always use a
  diagnostic script first to confirm the hook runner reaches your code.

- **Agent hooks in plugin contexts**: `type: "agent"` hooks may silently fail
  when defined in a plugin's `hooks.json`, even though they work in project
  settings. If you need agent hooks, define them in `.claude/settings.json`
  instead of a plugin `hooks.json`.

- **Malformed JSON**: A trailing comma or missing bracket in `hooks.json`
  causes the entire file to be ignored silently. Validate JSON syntax before
  debugging anything else.

- **Script not executable**: The hook script must have execute permission
  (`chmod +x`). Missing `+x` causes silent failure on most platforms.
