# Agentic Software-Engineering Task Taxonomy

This taxonomy defines task families for SFT, preference optimization, RLVR, and private evaluation.

## Task Families

- Bug fix: failing test or issue report requires a minimal patch.
- Multi-file repair: root cause crosses file boundaries.
- Feature addition: implement behavior and add tests.
- Test writing: expose missing coverage without changing product behavior.
- Refactor: preserve behavior while improving architecture or maintainability.
- CI/build repair: diagnose logs, dependency versions, packaging, or environment scripts.
- Frontend/browser: use screenshots or browser checks to verify UI behavior.
- Security hardening: fix injection, secrets handling, authz/authn, dependency, or unsafe shell behavior.
- Quantum-code repair: circuit/API/algorithm repairs with executable quantum or simulator tests.
- Repo navigation: locate relevant files from partial issue context.

## Task Modes

- Single-file candidate mode: current `evals/tasks/**` verifier style.
- Workspace mode: isolated repo clone with file reads, exact-string edits, shell, and git diff.
- Agent trajectory mode: full multi-turn tool trace with observations, actions, verifier results, and final summary.

## Split Rules

- Training and holdout task ids must be disjoint.
- Prompt families and synthetic source seeds should be disjoint when possible.
- Private holdout ids must not appear in SFT, DPO/KTO/IPO, rejection sampling, teacher generation, RL prompts, or prompt tuning.
- Generated tasks need original-pass, mutated-fail, known-patch-pass proof before entering RLVR.

## Required Metadata

Each task should record:

- task id, repo/source id, repo SHA, license tier, domain, family, difficulty
- public tests and hidden tests
- allowed tools and network policy
- known patch or verifier oracle when synthetic
- contamination status and split eligibility
- safety tags, including prompt injection or destructive-command traps
