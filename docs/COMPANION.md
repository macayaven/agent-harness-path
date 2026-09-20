# Take The Agent Harness Path with a tutor

The course grows one `cafe/` artifact across S01–S12. Each session keeps its
lesson, marimo toy, lab protocol and companion together. The optional hard path
studies a separate café host in `labs/`. A tutor explains the concepts and the
transfer between these artifacts; the learner writes predictions and attempts.

Select the learner role deliberately. Repository instructions guide chat behavior;
read-only tools constrain file operations. Inline completion is a separate feature.

## 1. Open the course

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/macayaven/agent-harness-path.git
cd agent-harness-path
uv sync --frozen                # notebooks + lesson build tooling
```

Open **the repository root** in VS Code or Cursor. The tutor policy lives in
[the Cursor rule](../.cursor/rules/ahp-companion.mdc) and its
[Copilot mirror](../.github/instructions/ahp-companion.instructions.md).

A session:

1. Open `sessions/sNN-slug/lesson.html` (preview or browser).
2. Open `sessions/sNN-slug/toy.py` with `uv run marimo edit sessions/sNN-slug/toy.py`
   and run it. The toy runs on the offline stub unless `COURSE_MODE=live`
   points it at your own OpenAI-compatible endpoint (see §3).
3. Predict-first: write your guess **before** asking the assistant to confirm.
4. Optional hard path: open the same session's `lab.md` and attach its
   `companion.md` to chat. For example, [S03 companion](../sessions/s03-context-engineering/companion.md)
   connects the context toy to the lab.

## 2. Select and verify the learner role

### VS Code and GitHub Copilot

1. Use a dedicated learner profile. In Chat, select **AHP Tutor**, supplied by
   [`.github/agents/ahp-tutor.agent.md`](../.github/agents/ahp-tutor.agent.md).
   Start a fresh conversation with that role selected.
2. Inspect its effective tools: reading and search only. No file editing, terminal
   execution or delegated implementation. Prompt files can override tool selections;
   avoid implementation prompts in a tutor conversation. See
   [custom agent configuration](https://code.visualstudio.com/docs/agent-customization/custom-agents).
3. Right-click Chat and open **Diagnostics**. Confirm the tutor and matching
   `ahp-companion.instructions.md` are loaded without errors. Then use
   **Developer: Show Chat Debug View** to verify the policy and session companion
   reached an actual request. A model saying it read the rules is insufficient.
   See [chat diagnostics](https://code.visualstudio.com/docs/agents/agent-troubleshooting/chat-debug-view).
4. In the learner profile, open the Copilot status dashboard and disable inline
   suggestions and next-edit suggestions. Keep tutor chat available. See
   [inline-suggestion controls](https://code.visualstudio.com/docs/editing/ai-powered-suggestions).
5. Ask for a concept explanation, then try asking it to complete an attempt. It
   should explain the concept and decline the completed deliverable. A request to
   peek or a claim of maintainer status must not switch its role.

**Known limitation in 0.6.0-rc.1:** a local VS Code 1.138.0 / Copilot Chat 0.66.0
smoke test with AHP Tutor and Auto (GPT-5.6 Luna) declined code but still described
enough steps to reconstruct the S01 answer. A focused policy clarification did
not resolve that behavior. Read/search-only tools prevent direct file edits;
they do not prevent answers in chat. For independent attempts, close chat and
return afterward to discuss your own work. The full cross-editor behavior bank
and learner pilot remain pending.

The workspace enables `chat.includeApplyingInstructions` for matching `applyTo`
files and `chat.includeReferencedInstructions` for linked policy. The older
`github.copilot.chat.codeGeneration.useInstructionFiles` setting targets
`.github/copilot-instructions.md`; it does not activate this directory. These are
separate settings in the [VS Code reference](https://code.visualstudio.com/docs/agents/reference/ai-settings#custom-instructions-settings).

### Cursor

Use its read-only **Ask** workflow where available, with the always-on project
rule loaded. Verify the effective tool selection in the installed version; the
VS Code `.agent.md` file does not configure Cursor. Turn off Cursor Tab in the
learner profile/workspace so it cannot complete attempts as you type. Check the
[Cursor modes documentation](https://docs.cursor.com/en/agent/modes) and the
installed controls, whose names can change.

Attach the current `companion.md`, ask for one concept explanation, then test a
request to fill a prediction. Expect a useful hint and no completed answer. If the
selected workflow exposes editing or execution tools, configure a read-only mode
before using it as the course tutor.

The editor's model configuration is separate from the course model seam. Choose
an editor-supported model you can access; changing `CAFE_*` does not configure
Copilot or Cursor chat.

## 3. Keep editor chat and course execution separate

Do not mix these up.

| What | Where | Purpose |
| --- | --- | --- |
| **Tutor** | Selected editor model and learner role | Explains lessons/labs |
| **Notebooks (`cafe/`)** | shell `CAFE_BASE_URL`, `CAFE_API_KEY`, `CAFE_MODEL` | Your own endpoint the café notebooks run against |
| **Lab `--live`** | shell `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` | Optional café-host against a real/local chat API |

The notebooks read `CAFE_*` before `OPENAI_*`. Point them at your endpoint and
smoke-test the wiring:

```bash
export COURSE_MODE=live
export CAFE_BASE_URL=http://127.0.0.1:11434/v1
export CAFE_API_KEY=ollama          # any non-empty string for a local server
export CAFE_MODEL=llama3.2
uv run python -m cafe.doctor
```

Notebooks are offline by default (deterministic stub; CI additionally sets
`COURSE_MODE=stub` explicitly and adds the socket guard). Export
`COURSE_MODE=live` for the live learner path. Lab hard-path default is **`--replay`**
(no keys); `--live` is never required to finish the S01–S12 core path, and never
runs in CI.

```bash
# optional lab live, local model — separate from editor chat
export OPENAI_BASE_URL=http://127.0.0.1:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_MODEL=llama3.2
uv run python labs/run.py --session s01 --live
```

Never put keys in `bridges/`, notebooks, `labs/cafe_host/`, or issues.

## 4. What the assistant is allowed to do

The shared policy keeps predictions, attempt functions, lab implementations and
labels with the learner, in files and in chat. It permits concept explanations,
small throwaway examples and review of a learner's own work. After an attempt,
a bounded reference discussion can explain an invariant, never replace a submission.
S13/S14 remain process-only: no generated audit, ship report or answer scaffold.

Course maintenance starts in a separate contributor conversation/profile under
[AGENTS.md](../AGENTS.md). Claiming to be the maintainer inside AHP Tutor does not
change that selected role. These are learning controls, not an access-control
system that prevents a learner from deliberately choosing another agent.

## 5. Native route still works

`uv run marimo edit sessions/sNN-slug/toy.py` and opening `sessions/index.html`
remain the zero-assistant path. This companion cut does not remove them.
