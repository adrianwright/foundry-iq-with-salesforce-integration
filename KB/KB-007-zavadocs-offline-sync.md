# ZavaDocs Offline Sync and Conflict Resolution

**Article Number:** KB-007  
**Product:** ZavaDocs  
**Category:** Document Management & Sync  
**Last Updated:** February 2026

## Overview

ZavaDocs allows users to create, edit, and collaborate on documents in real time. The desktop client supports offline editing with automatic synchronization when connectivity is restored. This article covers the offline sync architecture, conflict resolution process, and troubleshooting common sync failures.

## Offline Sync Architecture

### How Offline Mode Works
1. **ZavaDocs Desktop Client** caches a local copy of recently accessed documents
2. When the user goes offline (VPN drop, network loss, airplane mode), editing continues on the local copy
3. **Change tracking** records every edit as an operational transform (OT) delta
4. When connectivity returns, the desktop client pushes local deltas to the ZavaDocs server
5. The server merges deltas from all offline editors using a **last-writer-wins with conflict detection** strategy
6. If conflicts are detected, a **conflict copy** is created for manual resolution

### Sync Priority
| Item | Sync Priority | Max Offline Cache |
|------|--------------|-------------------|
| Documents actively being edited | Highest | Unlimited |
| Documents opened in last 7 days | High | 5 GB |
| Starred/favorited documents | Medium | 2 GB |
| Shared folder contents | Low | 1 GB |

## Common Sync Issues

### Offline Edits Lost After Reconnection
**Symptoms:** User edited documents offline, but changes disappeared when connectivity was restored.

**Common Causes:**
- Desktop client sync was paused manually (tray icon shows paused state)
- Local cache was cleared before sync completed (e.g., uninstall/reinstall of desktop client)
- File was deleted on the server by another user while the offline user was editing
- Desktop client version is outdated (offline sync requires v4.2+)

**Resolution Steps:**
1. Check sync status: Desktop client tray icon > View Sync Status — look for "Pending" or "Conflict" items
2. If sync is paused, click Resume and wait for the queue to process
3. Check the **Conflict Copies** folder in ZavaVault (ZavaVault > [user] > Conflict Copies)
4. If files were deleted server-side, check ZavaVault Trash (retained for 90 days)
5. Update desktop client to v4.2 or later: Help > Check for Updates

### Conflict Copies Created
**Symptoms:** Multiple versions of the same document appear with "(Conflict Copy — [username] — [date])" suffix.

**Common Causes:**
- Two or more users edited the same document while offline
- Offline edits occurred in the same paragraph/section, preventing auto-merge
- Network instability caused the desktop client to go offline briefly and create divergent edits

**Resolution Steps:**
1. Open both the original and conflict copy side-by-side
2. Use ZavaDocs' **Compare Documents** feature: File > Compare > select the conflict copy
3. Manually merge desired changes from the conflict copy into the original
4. Delete the conflict copy after reconciliation
5. To prevent future conflicts, prefer **real-time co-editing** (web browser) for documents with multiple active editors

### Sync Stuck at "Processing" 
**Symptoms:** Desktop client shows sync in progress indefinitely, never completing.

**Common Causes:**
- Large file (> 100 MB) timing out during upload
- Network proxy blocking WebSocket connections required for sync
- Local file locked by another application (e.g., antivirus scanning)

**Resolution Steps:**
1. Check which file is stuck: Desktop client > View Sync Status > expand "In Progress" items
2. For large files, pause sync, split the document, and resume
3. Verify WebSocket connections are allowed through your proxy/firewall (port 443, `wss://sync.ZavaCloud.io`)
4. Close any application that might be locking the file (antivirus, backup agents)
5. As a last resort, reset sync: Desktop client > Settings > Advanced > Reset Sync State (re-downloads all cached files)

## Desktop Client Configuration

### Recommended Settings
| Setting | Recommended Value | Location |
|---------|------------------|----------|
| Offline cache size | 10 GB | Settings > Sync > Cache Size |
| Sync on metered connection | Off | Settings > Sync > Metered Connections |
| Conflict notification | Enabled | Settings > Notifications > Sync Conflicts |
| Auto-update | Enabled | Settings > General > Auto-Update |

### Minimum Requirements
- **Windows:** 10 (21H2+) or 11, 4 GB RAM, 2 GB free disk for cache
- **macOS:** 12 (Monterey) or later, 4 GB RAM, 2 GB free disk for cache
- **Linux:** Ubuntu 22.04+, Fedora 38+, 4 GB RAM (beta support)

## Best Practices

1. **Use real-time co-editing** (web browser) instead of offline editing when possible — eliminates conflicts entirely
2. **Keep the desktop client updated** to the latest version for best sync reliability
3. **Set offline cache size appropriately** — larger cache means more documents available offline but uses more disk space
4. **Resolve conflict copies promptly** — they accumulate and cause confusion if ignored
5. **Check sync status before closing the desktop client** — ensure all changes have been uploaded

## Related Articles
- KB-013: ZavaVault File Permissions After Workspace Migration
- KB-009: Tenant Data Migration and Workspace Cloning
- KB-001: VPN Connectivity Troubleshooting
