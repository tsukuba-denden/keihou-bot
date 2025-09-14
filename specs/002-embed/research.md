# Phase 0 Research: Handling Long Alert Text

**Date**: 2025-09-13
**Spec Reference**: `specs/002-embed/spec.md`

## 1. Unknowns from Feature Spec

The primary unknown identified in the specification was:
- **FR-005**: How should the system handle alert text that exceeds Discord's embed character limits?

## 2. Research & Analysis

### Discord Embed Limits
A review of the official Discord API documentation confirms the following key limits for embeds:
- **Description**: 4096 characters
- **Field Value**: 1024 characters
- **Total Characters (all fields)**: 6000 characters

### Options Considered
1.  **Truncate and Add Ellipsis (...)**: Shorten the description text to fit within the limit and append "..." to indicate that the content has been cut short.
2.  **Split into Multiple Fields**: Divide the long text across several embed fields.
3.  **Send Multiple Embeds**: Split the content into multiple separate embed messages.
4.  **Use a File Attachment**: Post the full text as a `.txt` file attachment alongside the embed.

### Evaluation
- The JMA alerts for this bot are typically concise. The `description` field is the most likely to exceed limits, but it's not a frequent occurrence.
- The current plain-text implementation already provides a direct link to the JMA source, which contains the full, unabridged alert.
- **Splitting (Options 2 & 3)** would create unnecessary visual noise and complexity for what should be a quick, scannable notification.
- **File Attachment (Option 4)** is overkill and requires more user interaction to see the full message.

## 3. Decision & Rationale

**Decision**: The system will **truncate** the embed description if it exceeds Discord's character limit.

**Rationale**:
- **Simplicity**: This is the simplest and cleanest solution.
- **User Experience**: It keeps the alert notification compact and easy to read. The primary goal is to notify, not to be an exhaustive source of record within Discord itself.
- **Leverages Existing Link**: Since a source link is already part of the alert data, users have a clear and immediate path to the full content if they need it. This avoids cluttering the channel.
- **Low Risk**: Given the nature of the alerts, critical information is unlikely to be lost in truncation, as the most important details (title, area, severity) are in separate, shorter fields.

This decision resolves the ambiguity in **FR-005**.
