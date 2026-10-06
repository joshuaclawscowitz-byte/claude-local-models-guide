# Context, compaction and save/reload

## Output limits are not compaction

A server may require the input tokens plus reserved output tokens to fit its
context window. Reducing the output allowance can create temporary room, but
history will continue growing. An allowance that is too small can cut off a
response or tool arguments.

Use the model server's actual context limit and tokenizer. Do not assume the
client's default model profile describes a replacement local model accurately.

## Work out the budget

For a backend that reserves the full requested output allowance, plan for:

```text
input + reserved output + safety margin <= configured context window
```

Input includes more than the visible chat: system instructions, tool schemas,
retrieved files, tool results and retained history may all count. The safety
margin is operational headroom, not extra model capacity.

For an illustrative 65,536-token window, a 4,096-token output allowance and a
2,048-token margin leave 59,392 tokens for input. These are example numbers, not
recommended settings for every model. Confirm how the runtime accounts for
reasoning and output tokens as well.

Reducing output can permit a request that previously did not fit. The tradeoff
is less space for that response, including structured tool arguments. It does
not delete older messages, increase the model's actual window or guarantee
better reasoning. More output capacity also cannot repair a broken tool schema.

## Automatic compaction

Compaction summarizes older context while retaining recent work. Whether it
works depends on the client, backend, token counting and model behavior.
Configuration switches alone do not prove successful continuation.

There are three separate mechanisms that are often confused:

| Mechanism | What changes | What to verify |
| --- | --- | --- |
| Native client compaction | The client replaces older history with a condensed representation | It triggers early enough for this backend and subsequent tool calls work |
| Gateway compaction | An extra service rewrites the request history | Summaries preserve constraints and complete tool pairs; failures remain visible |
| Manual save/reload | A new chat reads a durable checkpoint | It recovers current state without assuming old claims are still true |

The Python launcher implements none of these. A valid endpoint connection does
not configure a compaction threshold. Token-count estimates and actual server
limits can disagree; a summarization request also needs enough room to run.
Do not wait until every request is rejected before designing continuity.

For a custom summarizing gateway, preserve complete tool-call/result pairs,
retain the user's instructions and unresolved failures, check the resulting
size, and surface failed summaries. Summaries can lose details even when they
fit the token limit. Preserve the original transcript separately.

## Explicit checkpoints

For work that spans many chats, keep a short project checkpoint with:

- Current goal and constraints.
- Decisions already made.
- Files changed and checks actually run.
- Failed calls, uncertain outcomes and open questions.
- The next concrete action.

Save it before ending a session. In a fresh chat, load it along with the current
project instructions and verify the referenced files still exist. Keep revisions
so a bad or stale update does not destroy the last useful checkpoint. Never put
credentials in it.

A persistent project identity can survive many chats through these files.
That is different from retaining an unlimited conversation in the model's
context. Explicit checkpoints and native compaction complement one another.

## A practical long-running workflow

Keep one stable project location and checkpoint, while allowing conversations
to be replaced. Before a restart, save the current goal, permissions, completed
work, evidence and next action. After reload, inspect the current files and
repository status before editing them. A checkpoint saying “tests passed” should
identify what was tested and when; it is not proof that later changes pass.

For short-lived workers, give each a bounded task and require a final output
plus evidence. Bring the useful result into the project's checkpoint. For a
long-standing conversation, use the same durable state so a context failure
does not make that one chat the only place the project exists.

A pane title, agent nickname or model alias can help the user navigate, but
none of them stores project memory. Concurrent agents also need a clear owner
for shared edits; starting a fresh chat does not prevent conflicting file writes.

## Test continuity

Record an unusual identifier, a constraint and an unresolved failure. Cross a
real compaction boundary or start a fresh chat with the checkpoint, then verify
all three survive. Repeat under your actual tool workload before relying on it
for unattended long-running work.
