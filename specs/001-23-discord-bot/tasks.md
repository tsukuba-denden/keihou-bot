# Tasks: JMA Alert Bot for Tokyo's 23 Wards

**Input**: Design documents from `/specs/001-23-discord-bot/`
**Prerequisites**: plan.md, spec.md

## Phase 3.1: Setup
- [ ] T001 [P] Create project structure: `src/`, `tests/`, `data/` directories.
- [x] T002 [P] Initialize Python project with `uv` and add dependencies: `requests`, `discord.py`, `lxml`, `APScheduler`.
- [x] T003 [P] Configure linting with `pylint` and formatting with `black`.

## Phase 3.2: Core Implementation
- [x] T004 Create data model for `Alert` in `src/models.py`.
- [x] T005 Implement data storage for sent alerts in `src/storage.py` (using JSON or SQLite).
- [x] T006 Implement JMA XML parsing logic in `src/jma_parser.py`.
- [x] T007 Implement filtering logic for Tokyo's 23 wards in `src/filter.py`.
- [x] T008 Implement Discord notification service in `src/discord_client.py`.

## Phase 3.3: Integration
- [x] T009 Integrate JMA data fetching with `requests` in `src/jma_client.py`.
- [x] T010 Integrate all modules in `src/main.py` to create the main application loop.
- [x] T011 Use `APScheduler` to schedule the JMA data fetching task in `src/main.py`.

## Phase 3.4: Testing
- [x] T012 [P] Unit test for `Alert` data model in `tests/unit/test_models.py`.
- [x] T013 [P] Unit test for data storage in `tests/unit/test_storage.py`.
- [x] T014 [P] Unit test for JMA XML parsing in `tests/unit/test_jma_parser.py`.
- [x] T015 [P] Unit test for filtering logic in `tests/unit/test_filter.py`.
<<<<<<< HEAD
- [ ] T016 [P] Unit test for Discord notification service in `tests/unit/test_discord_client.py`.
- [x] T017 Integration test for the main application loop in `tests/integration/test_main.py`.
=======
- [x] T016 [P] Unit test for Discord notification service in `tests/unit/test_discord_client.py`.
- [ ] T017 Integration test for the main application loop in `tests/integration/test_main.py`.
>>>>>>> 8c939417b452f96a99b3709e3e4fa2bb5094e7a7

## Phase 3.5: Polish
- [x] T018 [P] Add logging to all modules.
- [x] T019 [P] Add error handling for network issues and parsing errors.
- [x] T020 [P] Create a `README.md` with setup and usage instructions.
- [x] T021 [P] Dockerize the application by creating a `Dockerfile`.

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
