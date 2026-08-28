# AI-Engine — Project Knowledge Graph

Living reference for this project: what each piece is, how it connects to the others,
and which decisions are locked vs. still open. Update this as components get built —
don't let it drift out of sync with the code.

## Core concept

An **orchestrator** routes incoming requests to **specialist agents**. Each agent owns
its own prompt, tools, and permissions. Application code — not the LLM — controls
execution, auth, and data access. The LLM decides *routing* and *what to say*; code
decides *what's allowed to happen*.

## Component map

```
request
  -> Orchestration Graph Engine (routes to an agent, ReAct loop, max-iteration guard)
       -> Agent Registry (looks up: system prompt + allowed tools + allowed data scope)
            -> Tool/MCP Layer (schema-validated tool calls; MCP servers as external tools)
                 -> RAG Module (retrieval + generation, source citation required)
                 -> Human-in-the-Loop Gate (high-risk actions pause for approval)
       -> Eval Harness (separate LLM call scores the run after the fact)
  -> Observability Layer (every step above logs latency, cost, and outcome)
```

| # | Component | Purpose | Key tech chosen |
|---|-----------|---------|------------------|
| 1 | Orchestration Graph Engine | Config-driven router; decides which agent handles a request; ReAct loop with a max-iteration guard | `langgraph` |
| 2 | Agent Registry | Each agent = system prompt + allowed tools + allowed data scope, defined declaratively | YAML config (agent name, prompt, tools, scope) — schema not yet designed |
| 3 | Tool/MCP Layer | Tools as schema-validated functions; MCP servers plug in as external tool providers; reject/retry bad LLM tool-call output | `pydantic` for schemas; MCP client TBD |
| 4 | RAG Module | Retrieval (vector DB) + generation, every answer carries a citation; low-confidence retrieval must say so or fall back to plain search | `chromadb` (local, no server needed) |
| 5 | Eval Harness | After each agent run, a separate LLM call scores accuracy / tool-use correctness / citation correctness; log every score | `sqlmodel` for score storage; scoring LLM TBD (likely same OpenRouter model) |
| 6 | Human-in-the-Loop Gate | High-risk actions (money movement, deletion, anything irreversible) write a pending-approval record instead of executing; human approves/rejects; full audit trail | `sqlmodel` for pending-approval + audit tables |
| 7 | Observability Layer | Every step (route decision, tool call, LLM call, eval score) logged with latency + token cost | `structlog` for structured logs |

## Decisions made so far

- **Language/stack:** Python, not Java. `uv` for project/dependency management.
- **LLM access:** OpenRouter (OpenAI-compatible API) via `langchain-openai`'s `ChatOpenAI`
  pointed at `base_url=https://openrouter.ai/api/v1`, key from `OPENROUTER_API_KEY`.
  This means model choice per agent/eval is just a string (e.g. `anthropic/claude-...`,
  `openai/gpt-...`) — not locked to one provider's SDK.
- **Persistence:** `sqlmodel` (SQLAlchemy + Pydantic) for eval scores and HITL
  approval/audit records. SQLite by default (`DATABASE_URL` in `.env`).
- **Vector DB:** `chromadb`, local/embedded — no separate server to run for RAG.
- **Config format:** Agents will be declared in a YAML file (name, prompt, allowed
  tools, allowed data scope) rather than in code — matches the "permission scoping
  happens in code/config, not in the prompt" principle. Exact schema not designed yet.
- **Entry point:** Not finalized — defaulting to a CLI script for fast iteration while
  building, with a FastAPI layer to follow once the core graph works. Flag if you'd
  rather start with the API.

## Open questions (to resolve before/while building each component)

- **Agent Registry / YAML schema:** exact fields per agent (name, prompt, tool
  allowlist, data-scope allowlist, model override?). Deferred — "I'll tell you when we
  get there."
- **MCP layer:** which MCP servers (if any) are targeted first, vs. plain Python tool
  functions wrapped with a schema.
- **Eval Harness:** which model scores runs, and the exact rubric (accuracy / tool
  correctness / citation correctness) — needs concrete criteria, not just categories.
- **HITL Gate:** what counts as "high-risk" for this project's actual use cases, and
  who "approves" (a person via CLI prompt? a small approval UI? a Slack message?).
- **Observability Layer:** structured logs only, or a dashboard on top? Cost tracking
  needs per-model pricing — OpenRouter returns usage in responses, need to map that to
  cost.
- **First agents to build:** deferred by you — generic toy agents vs. fintech-flavored
  examples vs. something else, TBD when we get there.

## Non-decisions (explicitly deferred, don't build yet)

- Cost-based model routing (switching models by task complexity) — deferred until
  there's real usage data to justify it.
- Live self-re-running agents based on eval scores — the eval harness logs scores for
  a human to review, it does not trigger automatic re-runs.
