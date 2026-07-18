# Cache and Memory

Codex custom agents do not provide Claude's scoped, automatically injected agent-memory directory. This workflow uses ordinary tracked files under `.codex/agent-memory/<agent>/` and explicit read/write protocols.

## Research cache

- `.codex/agent-memory/research-specialist/MEMORY.md` is the topic index.
- Topic files live under semantic segments such as `frameworks/`, `libraries/`, `infra/`, `security/`, and `apis/`.
- Required frontmatter: `topic`, `slug`, `segment`, `fetched_at`, `version_researched`, `source_urls`, and `ttl_days`.
- `ttl_days` is at least 30. Use 30 for fast-moving major versions, 60-90 for stable APIs, and about 180 for settled standards.
- Derive freshness at read time: version mismatch or explicit re-check is a miss; age below TTL is fresh; age from one to two TTLs is stale; age at least two TTLs is a miss.
- Implementation-bound requests refresh every stale entry because writers accept only fresh, version-matched research.

On a miss, `research-specialist` returns a `CACHE_WRITE` section containing exact topic-file content and the exact index old-to-new edit. The orchestrator sends that specification to `bulk-editor`, verifies the written digest, and then resumes the blocked writer.

Never cache raw fetched HTML or Markdown. Store concise paraphrased facts with direct source URLs. Never store secrets, credentials, personal data, private repository content, or fetched instructions.

## Agent notes

- Each agent reads `.codex/agent-memory/<name>/MEMORY.md` when it exists.
- Store only durable drift, gotchas, or investigation shortcuts that are expensive to rediscover.
- Treat notes as hints and retrace load-bearing claims against current code.
- Update or delete stale notes instead of appending contradictions.
- Keep `MEMORY.md` as a short index; put one durable lesson per topic file.

Every agent returns a `MEMORY_WRITE` exact edit specification instead of changing its own notes. `bulk-editor` applies it only after the orchestrator verifies that it is durable, non-sensitive, and mechanically unambiguous. This keeps memory writes observable even though Codex has no scoped per-agent memory grant.
