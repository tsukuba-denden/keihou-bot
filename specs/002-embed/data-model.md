# Phase 1 Design: Data Model

**Date**: 2025-09-13
**Spec Reference**: `specs/002-embed/spec.md`

This document outlines the primary data entity for the feature, based on the existing `Alert` model in the codebase.

## Entity: Alert

The `Alert` entity represents a normalized weather or disaster alert from the JMA (Japan Meteorological Agency). This model is already implemented in `src/models.py`.

### Attributes

| Attribute    | Type                | Description                                                 |
|--------------|---------------------|-------------------------------------------------------------|
| `id`         | `str`               | A stable, unique identifier for the alert.                  |
| `title`      | `str`               | The short, primary title of the alert.                      |
| `area`       | `str`               | The general area the alert applies to.                      |
| `ward`       | `Optional[str]`     | The specific Tokyo ward, if applicable.                     |
| `category`   | `str`               | The type of alert (e.g., "Weather Warning").              |
| `severity`   | `str`               | The severity level (e.g., "Advisory", "Warning").         |
| `issued_at`  | `datetime`          | The timestamp when the alert was issued (in UTC).           |
| `expires_at` | `Optional[datetime]`| An optional timestamp for when the alert expires (in UTC).    |
| `link`       | `Optional[str]`     | A URL to the source of the alert information.               |
| `raw`        | `Optional[Any]`     | The raw, unprocessed data from the source (for debugging).  |

### Validation Rules
- The `id` must be unique to prevent duplicate notifications. This is handled by the `JsonStorage` class, which tracks sent alert IDs.
- All string fields are expected to be non-empty.

### State Transitions
- The `Alert` object is immutable (`frozen=True`) after creation. Its state does not change.
