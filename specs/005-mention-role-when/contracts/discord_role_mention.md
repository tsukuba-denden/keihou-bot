# Contract: Discord Role Mention for Arrival Time Change

## Purpose
When school arrival time differs from the normal baseline, the notification MUST include a role mention to improve reach.

## Message Structure
- content: MUST start with a single role mention `<@&{ROLE_ID}>` only when a change is detected.
- embed: Follows existing style for school guidance/alerts. The embed is optional for this contract but recommended.

## Trigger Condition
- IF new_start_time != baseline_start_time for the target date → include role mention
- ELSE → no role mention

## Suppression
- Suppression key: `{date}:{type}:{channel_id}:{scope}`
- A role mention MAY be sent once per key per day (per_day_once policy)
- Updates to the same key SHALL be sent without role mention

## Error Handling
- If role_id is missing/invalid → send without mention and log WARN
- If baseline time is unknown → send without mention and log INFO

## Examples
- Changed start time (mention):
  - content: `<@&123456789012345678> 本日の登校開始は 10:00 です`
- Normal start time (no mention):
  - content: `本日の登校開始は通常どおり 08:30 です`
