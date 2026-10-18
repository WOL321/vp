# Auto-Delete Vote Confirmation Messages

## What Changed

The "✅ @user voted!" confirmation messages now automatically delete themselves after 30 seconds, similar to how the VP role ping messages disappear after 5 minutes.

## Why

These confirmation messages were cluttering the chat. While they provide useful immediate feedback, they don't need to stay in the chat permanently. The vote data is already tracked in the embed and leaderboard, so the confirmation messages are just temporary acknowledgments.

## How It Works

1. When a user clicks "I Voted!" and successfully claims a vote, the bot sends a confirmation message
2. The message is displayed for 30 seconds so the user and others can see it
3. After 30 seconds, the message automatically deletes itself
4. If the message is already deleted or the bot lacks permissions, it silently ignores the error

## Code Changes

### views.py

Added a helper method to the `VoteNotifyView` class:

```python
async def _delete_message_after(self, message, delay: int):
    """Delete a message after a specified delay."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except discord.HTTPException:
        pass  # Message already deleted or no permission
```

Modified the vote claim button to schedule auto-deletion:

```python
# Send message and schedule auto-delete after 30 seconds
confirm_message = await interaction.followup.send(confirm_msg)
asyncio.create_task(self._delete_message_after(confirm_message, 30))
```

## User Experience

### Before
```
[User clicks "I Voted!"]
✅ @User voted!
*They now have **1/3** votes this cycle*
💡 *2 votes remaining*

[Message stays in chat forever, cluttering the channel]
```

### After
```
[User clicks "I Voted!"]
✅ @User voted!
*They now have **1/3** votes this cycle*
💡 *2 votes remaining*

[30 seconds later...]
[Message disappears automatically]
```

## Benefits

1. **Cleaner Chat**: No accumulation of vote confirmation messages
2. **Immediate Feedback**: Users still see the confirmation for 30 seconds
3. **Consistent Behavior**: Matches the auto-delete behavior of VP ping messages
4. **No Data Loss**: Vote data is still tracked in the embed and leaderboard

## Configuration

If you want to change the delay, modify the delay parameter in `views.py`:

```python
asyncio.create_task(self._delete_message_after(confirm_message, 30))  # 30 seconds
```

Change `30` to any number of seconds you prefer.

## Testing

1. Click the "I Voted!" button
2. Verify the confirmation message appears
3. Wait 30 seconds
4. Verify the message automatically disappears

## Notes

- The bot needs "Manage Messages" permission to delete messages
- If the bot lacks permission, the message will stay but no error will be shown
- The auto-delete runs in the background and won't block other bot operations
