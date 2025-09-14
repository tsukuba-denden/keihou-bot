# Implementation Plan: 解除通知の実装

**Branch**: `003-` | **Date**: 2025-09-14 | **Spec**: [specs/003-/spec.md](specs/003-/spec.md)
**Input**: Feature specification from `D:\GitHub_tsukuba-denden\keihou-bot\specs\003-\spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
When a weather warning is cancelled, the user is notified of the cancellation. This will be achieved by extending the application to detect cancellation messages from the JMA feed and send a notification to the user via Discord.

## Technical Context
**Language/Version**: Python >=3.10
**Primary Dependencies**: requests, discord.py, lxml, APScheduler, python-dotenv
**Storage**: JSON files in the `data` directory.
**Testing**: pytest, pytest-asyncio
**Target Platform**: CLI application, can be run in a Docker container.
**Project Type**: Single project.
**Performance Goals**: Fetches data every 5 minutes.
**Constraints**: Depends on JMA feed URL and Discord webhook URL.
**Scale/Scope**: Single JMA feed, single Discord channel.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (src, tests)
- Using framework directly? Yes
- Single data model? Yes
- Avoiding patterns? Yes

**Architecture**:
- EVERY feature as library? Yes
- Libraries listed: `jma_client`, `jma_parser`, `filter`, `discord_client`, `storage`
- CLI per library: No, the project is a single application.
- Library docs: Not planned for this feature.

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes
- Git commits show tests before implementation? Yes
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes
- Integration tests for: new libraries, contract changes, shared schemas? Yes
- FORBIDDEN: Implementation before test, skipping RED phase. Yes

**Observability**:
- Structured logging included? Yes
- Frontend logs → backend? N/A
- Error context sufficient? Yes

**Versioning**:
- Version number assigned? 0.1.0
- BUILD increments on every change? No
- Breaking changes handled? N/A

## Project Structure

### Documentation (this feature)
```
specs/003-/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   └── discord_cancellation_embed.md
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── __init__.py
├── discord_client.py
├── filter.py
├── jma_client.py
├── jma_parser.py
├── main.py
├── models.py
└── storage.py

tests/
├── integration/
│   └── test_main.py
└── unit/
    ├── test_discord_client.py
    ├── test_filter.py
    ├── test_jma_parser.py
    ├── test_models.py
    └── test_storage.py
```

**Structure Decision**: Option 1: Single project

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - The main unknown was how to handle user preferences for cancellation notifications.
2. **Generate and dispatch research agents**:
   - Research was conducted to determine the best approach for handling user preferences.
3. **Consolidate findings** in `research.md` using format:
   - The decision was made to tie the cancellation notification to the main warning subscription for the initial implementation.

**Output**: `research.md` with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - The `Cancellation Notification` entity was defined.
2. **Generate API contracts** from functional requirements:
   - A contract for the Discord embed message was created in `contracts/discord_cancellation_embed.md`.
3. **Generate contract tests** from contracts:
   - This will be done in the implementation phase.
4. **Extract test scenarios** from user stories:
   - A quickstart guide was created in `quickstart.md` to define the testing process.
5. **Update agent file incrementally** (O(1) operation):
   - Not applicable for this workflow.

**Output**: `data-model.md`, `contracts/discord_cancellation_embed.md`, `quickstart.md`

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 10-15 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
|           |            |                                     |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
