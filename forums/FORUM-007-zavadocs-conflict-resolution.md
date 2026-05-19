# Community Forum: ZavaDocs Conflict Resolution Frustrations

**Article Number**: FORUM-007  
**Category**: Document Management & Sync  
**Product**: ZavaDocs

---

## Thread: ZavaDocs lost my offline edits — no conflict copy created. Happened to 15 people.

**Posted by:** @AngelaM_BrightPath | February 7, 2026

Our team was editing training documents on a cross-country flight. When we landed and reconnected to Wi-Fi, all our offline edits just... vanished. No conflict copies, no error messages. 15 people lost work. We're on ZavaDocs Desktop Client v4.1.3 on Windows 11. This is unacceptable. Is there any way to recover our work?

---

### Reply 1

**Posted by:** @DocSync_Expert_Tom | February 7, 2026

I've seen this before — v4.1.3 has a bug where offline edits are silently discarded if the offline period exceeds 4 hours. The sync token expires and the client just... gives up instead of creating a conflict copy.

**v4.2.0 fixes this** — the sync token lifetime was extended to 7 days and the client now creates conflict copies instead of discarding edits when the token expires.

**For data recovery:** Your edits might still be in the local cache. Check:
```
%APPDATA%\ZavaDocs\sync\deltas\
```
If you find `.delta` files with timestamps matching your flight, ZavaDocs support can help extract them.

---

### Reply 2

**Posted by:** @AngelaM_BrightPath | February 8, 2026

@DocSync_Expert_Tom I checked the deltas folder — found delta files for 8 of the 15 users! The other 7 had already been cleared by auto-cleanup (it runs when the client starts with a fresh sync). ZavaCloud support (CASE-007) helped us extract and reapply the deltas for the 8 users. Still lost work for 7 people though.

Updating to v4.2.0 now. This should have been a mandatory update.

---

### Reply 3

**Posted by:** @RemoteWorker_Josh | February 9, 2026

This happened to us too, though only for 2 people. Our workaround until we updated: **Use the web browser for collaborative editing, not the desktop client.** The browser version saves to the server in real-time — no offline sync issues.

Of course, that only works when you have internet, which doesn't help on a plane. But for most remote work situations, the browser is more reliable.

---

### Reply 4

**Posted by:** @ZavaDocs_PowerUser | February 10, 2026

Pro tip: Even in v4.2.0, check the sync status icon in the system tray before you go offline. Green checkmark = all synced. Orange spinner = still syncing. If you close the laptop while it's still syncing, your baseline might be stale and you'll get more conflict copies than necessary.

Also, increase your offline cache size (Settings > Sync > Cache Size) — I set mine to 20 GB so all my frequently used docs are cached and available offline.

---

### Reply 5

**Posted by:** @IT_Manager_Karen | February 12, 2026

For any IT admins reading this — add ZavaDocs Desktop Client to your mandatory update policy. v4.2.0 is a critical update. We pushed it via endpoint management and haven't had a sync complaint since.

KB-007 has the full guide on offline sync behavior, conflict resolution, and desktop client configuration. Highly recommend reading it.

---

### Reply 6

**Posted by:** @AngelaM_BrightPath | February 14, 2026

Update: We've been on v4.2.0 for a week now and had zero sync issues. Tested with a deliberate 6-hour offline period and edits synced perfectly when I reconnected. Conflict copies were created as expected when two people edited the same doc offline. Much better experience.
