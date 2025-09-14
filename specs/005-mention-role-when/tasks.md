# Tasks: 登校時間変更時のロールメンション

**Input**: Design documents from `/specs/005-mention-role-when/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md (tech stack, structure)
2. Load data-model.md (entities), contracts/ (contracts), research.md (decisions), quickstart.md (scenarios)
3. Generate tasks by category (Setup → Tests → Models → Services → Integration → Polish)
4. Number tasks (T001...) and mark [P] where parallelizable across different files
5. Output tasks.md
```

## Phase 3.1: Setup
- [ ] T001 Ensure dependency installed: discord.py>=2.4.0 in `pyproject.toml` (verify only)
- [ ] T002 [P] Add env var note to README: `ROLE_ID` required (server-level)

## Phase 3.2: Tests First (TDD) ⚠ MUST COMPLETE BEFORE 3.3
- [ ] T003 Contract test for role mention content rule in `tests/contract/test_discord_role_mention.py`
  - Given baseline!=today → content begins with `<@&ROLE_ID>` exactly once
  - Given baseline==today → content has no role mention
  - Use DRY_RUN mode and a test double for webhook send
- [ ] T004 [P] Integration test: guidance with changed time in `tests/integration/test_school_guidance.py`
  - Ensure message includes role mention when time differs
- [ ] T005 [P] Integration test: guidance with normal time in `tests/integration/test_school_guidance.py`
  - Ensure message has no role mention when no difference
- [ ] T006 [P] Integration test: suppression (same-day duplicate) in `tests/integration/test_school_guidance.py`
  - First send mentions; second update within same day should not mention

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T007 Implement RoleMentionSetting model (in-memory or via `src/storage.py`) in `src/models.py`
  - Fields: role_id, enabled, suppress_policy, window_minutes
  - Load from env `ROLE_ID` if not stored; server-level scope only
- [ ] T008 Add suppression key helper in `src/storage.py`
  - Key: `{date}:{type}:{channel_id}:{scope}`; per-day-once policy
- [ ] T009 Update `DiscordNotifier._create_guidance_embed` and sending path to support content preface mention in `src/discord_client.py`
  - When baseline differs, prefix content with `<@&ROLE_ID> `; else no prefix
  - Respect DRY_RUN and webhook path
  - Do not mention on consecutive updates for same suppression key
- [ ] T010 Wire baseline comparison using `src/school_policy.py` in `src/main.py` or appropriate service
  - Provide a function to get normal start time and compare with today’s

## Phase 3.4: Integration
- [ ] T011 Logging: warning on invalid/missing role_id; info on suppression applied in `src/discord_client.py`
- [ ] T012 [P] Config docs: update `specs/005-mention-role-when/quickstart.md` with final env/settings

## Phase 3.5: Polish
- [ ] T013 [P] Unit tests for suppression helper in `tests/unit/test_suppression.py`
- [ ] T014 [P] Unit tests for RoleMentionSetting loading in `tests/unit/test_models.py`
- [ ] T015 Refactor to remove duplication and ensure code style passes

## Dependencies
- Tests (T003-T006) before implementation (T007-T010)
- T007 blocks T009; T008 blocks T009; T010 is independent but needed for end-to-end
- Implementation before integration/polish (T011-T015)

## Parallel Examples
```
# Run these in parallel [P] (different files):
Task: "Integration test changed time in tests/integration/test_school_guidance.py"
Task: "Integration test normal time in tests/integration/test_school_guidance.py"
Task: "Unit tests for suppression in tests/unit/test_suppression.py"
```

## Notes
- Keep mentions to at most one per suppression key per day
- If baseline unknown, send without mention and log INFO
- Respect Discord rate limits; avoid tight loops on retries
