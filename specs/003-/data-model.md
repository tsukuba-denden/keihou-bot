# Data Model for Cancellation Notification

## Entities

### Cancellation Notification

Represents the message sent to the user when a warning is lifted. It should contain information about the original warning.

**Fields**:

*   `original_warning_id`: The ID of the warning that was cancelled.
*   `cancelled_at`: The timestamp when the cancellation was issued.
*   `region`: The region for which the warning was cancelled.
*   `warning_type`: The type of warning that was cancelled.

## State

The system needs to maintain the state of active warnings to be able to identify when a warning is cancelled. The current implementation uses a JSON file (`sent_ids.json`) to store the IDs of sent alerts. This will be extended to store the full alert information for active warnings.

## User Preferences

As per the research, there will be no separate opt-out for cancellation notifications in this iteration. The subscription is at the warning level.
