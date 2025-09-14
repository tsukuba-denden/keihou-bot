# Phase 1 Design: Discord Embed Contract

**Date**: 2025-09-13
**Spec Reference**: `specs/002-embed/spec.md`

This document defines the contract for the Discord embed message that will be sent for each JMA alert. This serves as the primary interface for the user-facing notification.

## Embed Structure

The bot will send a single `discord.Embed` object with the following structure, mapping fields from the `Alert` data model.

| Embed Property | Value Source (`Alert` model) | Notes                                                                                             |
|----------------|------------------------------|---------------------------------------------------------------------------------------------------|
| `title`        | `alert.category`             | Use the alert category as the embed title for concise, scannable context.                         |
| `description`  | `(Formatted String)`         | A formatted string containing key information (Area only; Category omitted as it's the title).    |
| `color`        | `alert.severity`             | The embed color will change based on the severity level to provide a quick visual indicator.      |
| `timestamp`    | `alert.issued_at`            | The issue time of the alert, displayed in the embed's footer.                                     |
| `url`          | `alert.link`                 | If a source link is available, it will be attached to the embed's title.                          |

### Description Formatting

The main `description` of the embed will be a multi-line string constructed as follows:

```
**Area**: {alert.ward or alert.area}

{A formatted and potentially truncated version of the main alert body/details.}
```

### Color Mapping
The `color` of the embed will be determined by the `severity` string:
- **Emergency**: `discord.Color.dark_red()`
- **Warning**: `discord.Color.orange()`
- **Advisory**: `discord.Color.gold()`
- **Default**: `discord.Color.light_grey()`

### Handling Long Text
As decided in `research.md`, if the formatted description text exceeds Discord's character limits, it will be truncated and an ellipsis (`...`) will be appended. The user can click the title link to view the full alert on the JMA website.
