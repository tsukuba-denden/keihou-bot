# Discord Embed Contract for Cancellation Notification

This contract defines the structure of the Discord embed message for a cancellation notification.

## Embed Structure

```json
{
  "title": "【解除】気象警報・注意報",
  "description": "以下の地域の警報・注意報は解除されました。",
  "color": 3447003,
  "fields": [
    {
      "name": "地域",
      "value": "[Region Name]"
    },
    {
      "name": "解除された警報・注意報",
      "value": "[Warning Type]"
    }
  ],
  "footer": {
    "text": "気象庁 | JMA"
  }
}
```

## Field Descriptions

*   **title**: The title of the embed.
*   **description**: A brief description of the cancellation.
*   **color**: The color of the embed. Green for cancellation.
*   **fields**: A list of fields to display.
    *   **name**: The name of the field.
    *   **value**: The value of the field.
*   **footer**: The footer of the embed.
