# Data Model: 登校時間変更時のロールメンション

## Entities

### RoleMentionSetting
- scope: server (guild)
- role_id: string (Discord Role ID)
- enabled: boolean (default: true)
- allow_channel_override: boolean (default: false) [Future]
- suppress_policy: enum { per_day_once, time_window } (default: per_day_once)
- window_minutes: int (used when suppress_policy = time_window)

### ScheduleBaseline
- source: school_policy
- normal_start_time: string (e.g., "08:30") per weekday/exception
- exceptions: list of dates with override times

### ArrivalTimeChangeNotification
- date: YYYY-MM-DD
- new_start_time: HH:MM
- type: enum { delay, earlier, canceled }
- scope: enum { all, grade, class }
- scope_id: optional (grade/class id)
- notification_id: string (for dedup)

### SuppressKey (derived)
- date + type + channel_id + scope → unique key for mention suppression

## Validation Rules
- RoleMentionSetting.role_id must be a numeric string
- When suppress_policy = time_window, window_minutes >= 1
- ArrivalTimeChangeNotification.new_start_time must differ from baseline to trigger mention
