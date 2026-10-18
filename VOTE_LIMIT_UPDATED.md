# ✅ Vote Claiming System Updated - 3 Votes Per Cycle

## What Changed

Changed the vote claiming system from **time-based cooldown** (1 vote per hour) to **cycle-based limit** (3 votes per vote party).

## Why This Is Better

### Before (Time-Based Cooldown):
- ❌ Users could farm votes by clicking every hour
- ❌ No connection to actual voting (3 sites)
- ❌ Encouraged spam clicking
- ❌ Unfair - some users could claim more votes

### Now (Cycle-Based Limit):
- ✅ **3 votes per cycle** = matches the 3 vote sites
- ✅ No time-based farming possible
- ✅ Fair - everyone gets exactly 3 claims per cycle
- ✅ Encourages voting on all 3 sites
- ✅ Resets automatically when vote party completes

## How It Works Now

### User Experience:

1. **First Vote:**
   ```
   ✅ @Username voted!
   *They now have **1/3** votes this cycle*
   💡 *2 votes remaining*
   ```

2. **Second Vote:**
   ```
   ✅ @Username voted!
   *They now have **2/3** votes this cycle*
   💡 *1 vote remaining*
   ```

3. **Third Vote:**
   ```
   ✅ @Username voted!
   *They now have **3/3** votes this cycle*
   ```

4. **Fourth Vote Attempt:**
   ```
   ⚠️ You've already claimed all **3** votes for this cycle!
   *Wait for the next vote party to claim more.*
   ```

### Embed Display:

The tracker embed now shows:
```
🗳️ **Claimed this cycle:** 15 votes (3 per player)
*Last voter: Username*
```

## Technical Changes

### Files Updated:

1. **`views.py`**
   - Removed time-based cooldown check
   - Added cycle limit check (3 votes max)
   - Updated confirmation messages to show X/3 format
   - Shows remaining claims after each vote

2. **`embed_builder.py`**
   - Updated embed to show "(3 per player)" note
   - Uses `MAX_VOTES_PER_CYCLE` constant

3. **`config.py`**
   - Added `MAX_VOTES_PER_CYCLE = 3` constant
   - Deprecated `VOTE_CLAIM_COOLDOWN` (no longer used)

4. **`i18n.py`**
   - Updated English and Spanish messages
   - Changed cooldown message to cycle limit message
   - Updated vote claimed messages to show X/3 format

### Data Flow:

1. User clicks "I Voted!" button
2. Bot checks if `votes_this_cycle >= 3`
3. If yes → show "already claimed all 3" message
4. If no → claim vote, increment counter
5. Show confirmation with X/3 format
6. Update embed with total claimed votes
7. When vote party completes → `reset_cycle()` resets all counters to 0

## Configuration

You can easily change the limit by editing `config.py`:

```python
MAX_VOTES_PER_CYCLE = 3  # Change this number
```

For example:
- `MAX_VOTES_PER_CYCLE = 5` → 5 votes per cycle
- `MAX_VOTES_PER_CYCLE = 1` → 1 vote per cycle

## Benefits

### For Users:
- ✅ Clear limit (3 votes per cycle)
- ✅ No confusion about cooldowns
- ✅ Encourages voting on all 3 sites
- ✅ Fair system - everyone gets same amount

### For Server:
- ✅ Prevents vote farming
- ✅ More authentic voting behavior
- ✅ Easier to understand
- ✅ Matches actual vote site count

### For Admins:
- ✅ Easy to configure (one constant)
- ✅ Automatic reset on cycle completion
- ✅ No time-based logic to maintain
- ✅ Clear tracking in leaderboards

## Testing

1. Push changes to GitHub
2. Restart bot on Wispbyte
3. Click "I Voted!" 3 times
4. Verify:
   - Each click shows X/3 format
   - Shows remaining claims
   - 4th click shows limit message
5. Wait for vote party to complete
6. Verify counters reset to 0
7. Click again → should work (new cycle)

## Migration

No migration needed! The existing `votes_this_cycle` field in `player_data.json` works perfectly with the new system. The only difference is:
- Old: Limited by time (1 hour cooldown)
- New: Limited by count (3 votes max)

When the vote party completes, `reset_cycle()` already resets `votes_this_cycle` to 0, so it works seamlessly.

## Summary

The vote claiming system is now **cycle-based** instead of **time-based**, preventing farming and encouraging authentic voting behavior. Each player can claim exactly 3 votes per vote party cycle, matching the 3 vote sites.

---

**No more farming! Fair voting for everyone!** 🎉
