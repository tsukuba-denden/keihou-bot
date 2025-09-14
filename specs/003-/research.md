# Research for Cancellation Notification Feature

## Technical Stack

*   **Language/Version**: Python >=3.10
*   **Primary Dependencies**: requests, discord.py, lxml, APScheduler, python-dotenv
*   **Storage**: JSON files in the `data` directory.
*   **Testing**: pytest, pytest-asyncio
*   **Target Platform**: CLI application, can be run in a Docker container.
*   **Project Type**: Single project.
*   **Performance Goals**: Fetches data every 5 minutes.
*   **Constraints**: Depends on JMA feed URL and Discord webhook URL.
*   **Scale/Scope**: Single JMA feed, single Discord channel.

## Open Questions

### User Opt-out for Cancellation Notifications

*   **Question**: Should there be a way for users to opt-out of cancellation notifications specifically, or is it tied to the main warning notification subscription?
*   **Assumption**: For the initial implementation, the cancellation notification will be tied to the main warning notification subscription. Users who subscribe to a warning will automatically receive the cancellation notification.
*   **Rationale**: This simplifies the initial implementation. A separate opt-out can be added as a future enhancement if requested.
*   **Decision**: Proceed with the assumption. This will be documented in the `data-model.md`.
