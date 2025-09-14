# Implementation Plan: Display Alerts in Embeds

**Branch**: `002-embed` | **Date**: 2025-09-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-embed/spec.md`

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

## Summary
The primary requirement is to change the bot's notifications from plain text to Discord embeds for better readability. The technical approach involves modifying the `DiscordNotifier` class to construct and send a `discord.Embed` object instead of a plain string. Long alert messages will be truncated to keep the embeds concise, as detailed in `research.md`.

## Technical Context
**Language/Version**: Python 3.10+
**Primary Dependencies**: discord.py>=2.4.0
**Storage**: Filesystem (via `src/storage.py`)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux Server (generic)
**Project Type**: Single Project
**Performance Goals**: N/A
**Constraints**: N/A
**Scale/Scope**: N/A

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**: PASS
- Projects: 1 (src)
- Using framework directly? Yes (`discord.py`)
- Single data model? Yes (`Alert`)
- Avoiding patterns? Yes

**Architecture**: PASS
- EVERY feature as library? N/A (simple project)
- Libraries listed: N/A
- CLI per library: N/A
- Library docs: N/A

**Testing (NON-NEGOTIABLE)**: PASS
- The project has an existing test suite in `/tests` which will be extended.
- New tests will be added for the embed creation logic.

**Observability**: PASS
- Structured logging is already in use.

**Versioning**: PASS
- Project version is defined in `pyproject.toml`.

## Project Structure

### Documentation (this feature)
```
specs/002-embed/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/
│   └── discord_embed.md # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── discord_client.py  # To be modified
├── models.py
└── ...

tests/
└── unit/
    └── test_discord_client.py # To be modified/created
```

**Structure Decision**: Option 1: Single project

## Phase 0: Outline & Research
Completed. The primary unknown regarding handling long text was resolved.

**Output**: `research.md`

## Phase 1: Design & Contracts
Completed. The data model, embed contract, and validation steps have been documented.

**Output**: `data-model.md`, `contracts/discord_embed.md`, `quickstart.md`

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base.
- Create a unit test in `tests/unit/test_discord_client.py` to verify the embed creation logic. This test will fail initially (RED).
- Modify `src/discord_client.py` to create and send `discord.Embed` objects instead of plain text, making the test pass (GREEN).
- Refactor the code if necessary (REFACTOR).
- Manually validate the change using the steps in `quickstart.md`.

**Ordering Strategy**:
1.  Write failing unit test.
2.  Implement feature to make test pass.
3.  Manual validation.

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
None.

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented: None

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
