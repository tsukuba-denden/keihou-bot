# Tasks: 解除通知の実装

**Input**: Design documents from `/specs/003-/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root

## Phase 3.1: Setup
- [ ] T001 No setup tasks required.

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T002 [P] Create unit tests in `tests/unit/test_jma_parser_cancellation.py` for parsing JMA XML cancellation messages.
- [ ] T003 [P] Create integration tests in `tests/integration/test_cancellation.py` for the end-to-end cancellation notification flow.

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T004 Modify `src/models.py` to include a status field in the `JmaAlert` model to track if a warning is active or cancelled.
- [ ] T005 Modify `src/jma_parser.py` to correctly parse cancellation messages from the JMA feed and update the alert status.
- [ ] T006 Modify `src/storage.py` to handle the updated `JmaAlert` model, including updating the status of an existing alert.
- [ ] T007 Modify `src/discord_client.py` to create and send a cancellation notification embed based on the contract.
- [ ] T008 Modify `src/main.py` to identify cancelled alerts, update their status in storage, and trigger the cancellation notification.

## Phase 3.4: Integration
- [ ] T009 No integration tasks required.

## Phase 3.5: Polish
- [ ] T010 [P] Update `README.md` and any other relevant documentation to reflect the new cancellation notification feature.

## Dependencies
- Tests (T002-T003) before implementation (T004-T008)
- T004 blocks T005, T006, T008
- T005 blocks T008
- T006 blocks T008
- T007 blocks T008
- Implementation before polish (T010)

## Parallel Example
```
# Launch T002-T003 together:
Task: "Create unit tests in tests/unit/test_jma_parser_cancellation.py for parsing JMA XML cancellation messages."
Task: "Create integration tests in tests/integration/test_cancellation.py for the end-to-end cancellation notification flow."
```
