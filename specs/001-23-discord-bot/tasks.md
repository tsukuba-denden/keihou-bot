# Tasks: JMA Alert Bot for Tokyo's 23 Wards

**Input**: Design documents from `/specs/001-23-discord-bot/`
**Prerequisites**: plan.md, spec.md

## Phase 3.1: Setup
- [ ] T001 [P] Create project structure: `src/`, `tests/`, `data/` directories.
- [ ] T002 [P] Initialize Python project with `uv` and add dependencies: `requests`, `discord.py`, `lxml`, `APScheduler`.
- [ ] T003 [P] Configure linting with `pylint` and formatting with `black`.

## Phase 3.2: Core Implementation
- [ ] T004 Create data model for `Alert` in `src/models.py`.
- [ ] T005 Implement data storage for sent alerts in `src/storage.py` (using JSON or SQLite).
- [ ] T006 Implement JMA XML parsing logic in `src/jma_parser.py`.
- [ ] T007 Implement filtering logic for Tokyo's 23 wards in `src/filter.py`.
- [ ] T008 Implement Discord notification service in `src/discord_client.py`.

## Phase 3.3: Integration
- [ ] T009 Integrate JMA data fetching with `requests` in `src/jma_client.py`.
- [ ] T010 Integrate all modules in `src/main.py` to create the main application loop.
- [ ] T011 Use `APScheduler` to schedule the JMA data fetching task in `src/main.py`.

## Phase 3.4: Testing
- [ ] T012 [P] Unit test for `Alert` data model in `tests/unit/test_models.py`.
- [ ] T013 [P] Unit test for data storage in `tests/unit/test_storage.py`.
- [ ] T014 [P] Unit test for JMA XML parsing in `tests/unit/test_jma_parser.py`.
- [ ] T015 [P] Unit test for filtering logic in `tests/unit/test_filter.py`.
- [ ] T016 [P] Unit test for Discord notification service in `tests/unit/test_discord_client.py`.
- [ ] T017 Integration test for the main application loop in `tests/integration/test_main.py`.

## Phase 3.5: Polish
- [ ] T018 [P] Add logging to all modules.
- [ ] T019 [P] Add error handling for network issues and parsing errors.
- [ ] T020 [P] Create a `README.md` with setup and usage instructions.
- [ ] T021 [P] Dockerize the application by creating a `Dockerfile`.

## Dependencies
- T001, T002, T003 can be done in parallel.
- T004 is a prerequisite for T005, T006, T007, T008.
- Core Implementation (T004-T008) should be done before Integration (T009-T011).
- Testing (T012-T017) can be done in parallel with implementation.
- Polish (T018-T021) should be done last.

## Parallel Example
```
# Launch T001-T003 together:
Task: "Create project structure: src/, tests/, data/ directories."
Task: "Initialize Python project with `uv` and add dependencies: `requests`, `discord.py`, `lxml`, `APScheduler`."
Task: "Configure linting with pylint and formatting with black."
```
