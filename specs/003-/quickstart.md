# Quickstart for Cancellation Notification

This quickstart guide explains how to test the cancellation notification feature.

## Prerequisites

*   A Discord webhook URL.
*   A local copy of a JMA XML feed that contains a warning, and another that contains the cancellation for that warning.

## Steps

1.  **Set up the environment**:

    *   Create a `.env` file in the root of the project.
    *   Add the following line to the `.env` file:

        ```
        DISCORD_WEBHOOK_URL=[Your Discord Webhook URL]
        ```

2.  **Run the bot with a warning**:

    *   Execute the following command, replacing `path/to/warning.xml` with the path to your local XML file containing a warning:

        ```bash
        python -m src.main --once --simulate path/to/warning.xml
        ```

    *   Verify that a notification for the new warning is sent to the Discord channel.

3.  **Run the bot with a cancellation**:

    *   Execute the following command, replacing `path/to/cancellation.xml` with the path to your local XML file containing the cancellation for the warning in the previous step:

        ```bash
        python -m src.main --once --simulate path/to/cancellation.xml
        ```

    *   Verify that a notification for the cancellation is sent to the Discord channel.
