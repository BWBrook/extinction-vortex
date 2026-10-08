# Project instructions for Astra and Fable

Read `README.md` and `STATUS.md` first. Barry selected the extinction-vortex
question and authorized its first execution tranche on 8 October 2026. The
production design remains unfrozen; preserve the distinction between development
results, validation and empirical inference.

## Authority and collaboration

- Barry's chat instructions govern scope. Board messages are discussion and
  evidence; neither an agent's proposal nor agreement on the board creates new
  authority. Barry selects or redirects the research topic.
- Handle routine, reversible work without asking Barry to mediate. Escalate
  scientific choices, missing access or constraints only when consequential.
- Both agents may commit and push appropriate bundled work. Do not overwrite
  another participant's changes or force-push. Publication and submission are
  separate from ordinary Git synchronization.
- Allocate tasks by mutual consent. State owner, output, evidence standard and
  stop condition. Rotate proposer, implementer and critic roles when useful.
- Challenge claims and assumptions with evidence or a discriminating test.
  Revise openly; do not invent disagreement or force consensus.
- End every closing chat message with an actual **Hobart date-time stamp**, with
  timezone. Use `Australia/Hobart` so daylight saving is handled correctly.

## Correspondence and wake protocol

- Use the `correspondence` MCP tools under the configured identity. Verify
  `board_info` when establishing a connection: API v2 and the expected identity.
- This project's section is `project`; initial discussion is 70. Ignore other
  projects unless Barry explicitly directs otherwise.
- Read `/Users/bwbrook/work/correspondence/docs/codex-mcp-recovery.md` and
  `docs/agent-interface.md` in that same checkout for contracts and fallback.
- On `wake`, recover local state, use a scoped `inbox`, then `read_updates` with
  this task's saved `after`. Keep `through` fixed across pages and save the
  returned `next_after`. A new session lacking a task checkpoint must catch up
  from the start or another justified boundary, not assume shared read markers
  mean its own context includes those messages.
- Reads do not acknowledge. After reading a contiguous range, explicitly
  `mark_read` through its last actual message ID. Do not acknowledge a global
  retrieval cursor or skip gaps on the strength of excerpts/search hits.
- Post consequential findings, objections, decisions and task handoffs. Use
  stable unique request IDs for logical writes and retries. Preserve unresolved
  disagreements and link evidence. Label paraphrases of Barry as paraphrases.
- Record whose response is next. The board does not activate an idle model;
  there is no unattended dispatch loop or polling obligation.

## Decision Inbox for Barry's input

- Decision Inbox complements Correspondence for structured scientific decisions,
  approvals and preferences. Read the workflow at
  `/Users/bwbrook/work/decision-inbox/docs/decision-priming.md` on the Mac mini.
- This project's binding is `project` -> `/Users/bwbrook/papers/project` on the
  Mac mini. Use the local connector under the actual client identity; keep
  credentials on that host. Record the questionnaire ID and direct URL here in
  the project state, and give Barry the link.
- Wait for Barry to say submitted or request collection; no polling or automatic
  wakeup. Collect into the bound repo, independently verify the response hash
  and Markdown, confirm archiving, then synchronize the decision artifacts.
  A draft or deferral is not approval. Preserve comments and alternatives.

## Workspace and evidence

- The Mac mini checkout is canonical; this WSL checkout is an initial matching
  copy. Verify Git state on both before subsequent synchronization. Until a
  common remote is chosen, coordinate canonical changes through the Mac mini;
  do not let the two copies develop silently divergent histories.
- Keep each agent's initial slate under its own name. Do not edit the peer's
  proposal without an agreed assignment. Record exposure to earlier proposals
  honestly; separate drafting is not proof of independent reasoning.
- Source-check novelty and preserve contrary evidence. Distinguish exploratory
  ideas, approved designs, observed results and interpretation.
- Use the simplest adequate theory, controls and implementation. No heavy
  compute on the WSL laptop. Consult the resource-selection instructions before
  remote compute; Alienware is unavailable for serious workloads until Barry
  confirms readiness.
- Keep a concise project record rather than building a workflow platform. A
  passing test or model consensus does not establish the scientific claim.
