# Context, compaction and save/reload

## Output limits are not compaction

A server may require the input tokens plus reserved output tokens to fit its
context window. Reducing the output allowance can create temporary room, but
history will continue growing. An allowance that is too small can cut off a
response or tool arguments.

Use the model server's actual context limit and tokenizer. Do not assume the
client's default model profile describes a replacement local model accurately.

## Automatic compaction

Compaction summarizes older context while retaining recent work. Whether it
works depends on the client, backend, token counting and model behavior.
Configuration switches alone do not prove successful continuation.

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

## Test continuity

Record an unusual identifier, a constraint and an unresolved failure. Cross a
real compaction boundary or start a fresh chat with the checkpoint, then verify
all three survive. Repeat under your actual tool workload before relying on it
for unattended long-running work.
