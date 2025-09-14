# Phase 1 Design: Quickstart & Validation

**Date**: 2025-09-13
**Spec Reference**: `specs/002-embed/spec.md`

This document provides instructions on how to perform a quick, manual validation of the "Display Alerts in Embeds" feature.

## Validation Goal
To confirm that when the bot processes a sample weather alert, it successfully sends a well-formatted embed message to a specified Discord channel.

## Prerequisites

1.  **Python Environment**: A Python 3.10+ environment with all project dependencies installed.
    ```sh
    # If you use uv
    uv sync --all-extras --group dev
    ```

2.  **Discord Webhook URL**: You must have a valid Discord Webhook URL for the channel where you want to receive the test alert.

## Validation Steps

### 1. Configure Environment

Create a `.env` file in the root of the project directory and add your Discord Webhook URL to it:

```env
# .env
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your/webhook_url_here"
```

### 2. Run the Test Pipeline

Execute the main script from the root of the repository with arguments that force it to run once, use a local sample file, and bypass the duplicate-check mechanism.

```sh
python src/main.py --once --simulate samples/tokyo-warning-sample.xml --force-send
```

### 3. Verify the Output

- **Check your Discord channel**: A new message from the bot should appear almost instantly.
- **Confirm it is an embed**: The message should be a rich embed, not plain text.
- **Check the content**: 
    - The embed's title should match the title from the sample alert (`大雨注意報`).
    - The color should be appropriate for the alert's severity (e.g., orange for a "Warning").
    - The body of the embed should contain the area and description from the sample alert.
    - The timestamp should be present in the footer.

## Expected Outcome

If the steps are followed correctly, you will see a Discord embed in your channel that looks similar to this (content may vary based on the sample file):

**Title**: 大雨注意報
**Color**: Orange
**Body**: Contains details for "千代田区", category, etc.
**Footer**: Shows the alert's issue time.

This successful validation confirms that the core requirement of the feature—sending alerts as embeds—is working correctly.
