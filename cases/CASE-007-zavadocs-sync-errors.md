# Support Case: ZavaDocs Sync Errors Losing Offline Edits

**Case Number**: CASE-007  
**Status**: Resolved  
**Priority**: High  
**Product**: ZavaDocs  
**Category**: Document Management & Sync  
**Origin**: Web  
**Contact**: Angela Martinez, Training Coordinator, BrightPath Education  
**Account**: BrightPath Education  
**Created**: February 7, 2026  
**Last Updated**: February 14, 2026

---

## Subject
ZavaDocs desktop client losing offline edits for 15+ users after reconnection — no conflict copies created

## Description
Angela Martinez reported that approximately 15 users at BrightPath Education lost offline edits after their laptops reconnected to the network. Users were editing training documents on a flight, and when they reconnected at the destination, their changes were gone. No conflict copies were created. The users are on ZavaDocs Desktop Client v4.1.3 on Windows 11.

## Investigation Notes

**2026-02-07 — Initial Triage (Support Engineer: Carlos Diaz)**
- Confirmed ZavaDocs Desktop Client version: v4.1.3 — this is one version behind the current v4.2.0
- v4.2.0 includes critical fixes for offline sync reliability, specifically for extended offline periods (> 4 hours)
- v4.1.3 has a known issue: if the offline period exceeds the sync token lifetime (4 hours), the desktop client fails to push offline deltas and silently discards them
- No conflict copies were created because the client treated the offline session as expired rather than conflicting

**2026-02-08 — Data Recovery Attempted**
- Checked ZavaDocs local cache on 3 affected laptops — offline edits are still present in the local OT delta log
- ZavaDocs Desktop Client stores deltas in `%APPDATA%\ZavaDocs\sync\deltas\`
- Manually extracted delta files and applied them to the server documents using the ZavaDocs recovery tool
- Successfully recovered edits for 3 users; remaining users' delta caches had been cleared by the auto-cleanup

**2026-02-10 — Client Update Deployed**
- BrightPath IT pushed ZavaDocs Desktop Client v4.2.0 to all users via endpoint management
- v4.2.0 extends the sync token lifetime to 7 days and creates conflict copies instead of discarding deltas
- Tested offline scenario: laptop disconnected for 6 hours, edits synced correctly after reconnection

**2026-02-14 — Resolution Confirmed**
- Angela confirmed no further sync issues after the client update
- Recovered offline edits for 8 of 15 affected users; remaining 7 had to recreate their changes
- BrightPath added ZavaDocs desktop client updates to their mandatory patch cycle

## Resolution
ZavaDocs Desktop Client v4.1.3 had a known issue discarding offline edits when the offline period exceeded 4 hours. Updated to v4.2.0 which extends sync token lifetime and creates conflict copies. Partial data recovery achieved for 8 of 15 users. KB-007 documents offline sync best practices.

## Related Articles
- KB-007: ZavaDocs Offline Sync and Conflict Resolution
- FORUM-007: ZavaDocs Conflict Resolution Frustrations
