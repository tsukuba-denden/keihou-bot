# Tasks: Display Alerts in Embeds

**Input**: Design documents from `/specs/002-embed/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- Paths shown below assume a single project structure, which matches this repository.

## Phase 3.1: Setup
*No setup tasks are required as the project structure and dependencies are already in place.*

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: This test MUST be written and MUST FAIL before ANY implementation**
- [ ] **T001** Create a failing unit test in `tests/unit/test_discord_client.py` for the new embed creation logic. The test should:
    1.  Instantiate a sample `Alert` object.
    2.  Call a new (not-yet-created) helper method, e.g., `_create_embed_from_alert(alert)`.
    3.  Assert that the returned object is an instance of `discord.Embed`.
    4.  Assert that the embed's `title`, `description`, `color`, and `timestamp` correctly correspond to the sample `Alert` data and the rules in `specs/002-embed/contracts/discord_embed.md`.

## Phase 3.3: Core Implementation (ONLY after T001 is failing)
- [ ] **T002** In `src/discord_client.py`, create a new private helper method `_create_embed_from_alert(self, alert: Alert) -> discord.Embed`. This method will contain the logic to transform an `Alert` object into a `discord.Embed` object, including the severity-to-color mapping defined in the contract.

- [ ] **T003** In `src/discord_client.py`, refactor the `send_alerts` and `_send_via_webhook` methods. They should now iterate through alerts, call `_create_embed_from_alert()` for each, and pass the resulting `discord.Embed` object to the `webhook.send(embed=...)` parameter instead of sending a formatted string.

## Phase 3.4: Polish & Refinement
- [ ] **T004** Implement the description truncation logic within `_create_embed_from_alert` in `src/discord_client.py`, as specified in `research.md`. Add a new test case to `tests/unit/test_discord_client.py` that specifically verifies a long description is truncated correctly and ends with `...`.

## Phase 3.5: Manual Validation
- [ ] **T005** Manually execute the validation steps documented in `specs/002-embed/quickstart.md`. This involves setting up a `.env` file with a real `DISCORD_WEBHOOK_URL` and running the `main.py` script to post a sample alert to a Discord channel, confirming it appears correctly as an embed.

## Dependencies
- **T001** must be completed before **T002**.
- **T002** and **T003** must be completed before **T004**.
- **T004** must be completed before **T005**.

All tasks are sequential as they modify the same two core files (`src/discord_client.py` and `tests/unit/test_discord_client.py`).
