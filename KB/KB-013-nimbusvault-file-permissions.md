# NimbusVault File Permissions After Workspace Migration

**Article Number:** KB-013  
**Product:** NimbusVault  
**Category:** File Management & Permissions  
**Last Updated:** February 2026

## Overview

When workspaces are migrated, cloned, or restructured in NimbusCloud, file permissions in NimbusVault may not carry over as expected. This article covers how file permissions work in NimbusVault, common issues after migration, and resolution steps for broken access.

## NimbusVault Permission Model

### Permission Levels
| Level | Capabilities |
|-------|-------------|
| **Owner** | Full control — read, write, share, delete, manage permissions |
| **Editor** | Read and write — can edit files and upload to the folder |
| **Viewer** | Read only — can view and download files |
| **No access** | Cannot see the file or folder in NimbusVault |

### Permission Inheritance
- Files inherit permissions from their parent folder by default
- Explicit permissions on a file override inherited permissions
- Shared links create temporary access that doesn't modify the file's permission list

### Permission Sources
| Source | How It Works |
|--------|-------------|
| Direct assignment | Admin or owner grants access to a specific user |
| Group membership | Access granted via NimbusCloud group (synced from IdP or manually created) |
| Workspace membership | Members of a NimbusBoard workspace get access to the linked NimbusVault folder |
| Shared link | Time-limited access URL (no NimbusCloud account required for external sharing) |

## Post-Migration Permission Issues

### File Access Denied After Workspace Clone
**Symptoms:** Users in a cloned workspace cannot access files that were linked from the original workspace.

**Common Causes:**
- File links in cloned workspaces still point to the original workspace's NimbusVault folder
- New workspace members don't have permission on the original file location
- Files were not cloned — only references (links) were copied

**Resolution Steps:**
1. Check if files were cloned or linked: Open the file in NimbusVault > Properties > Location
2. If files are linked (not cloned), the new workspace members need permission on the original folder:
   - Option A: Grant the new workspace group access to the original folder
   - Option B: Copy files to the new workspace's NimbusVault folder (breaks the link to the original)
3. For bulk permission updates: NimbusAdmin > NimbusVault > Bulk Permissions > select folder > Add Group > [new workspace group]

### Inherited Permissions Lost After Folder Move
**Symptoms:** After moving a folder to a new location in NimbusVault, users lose access.

**Common Causes:**
- The folder was moved outside the parent hierarchy that granted inherited permissions
- The new parent folder has a more restrictive permission set
- Direct permissions on the moved folder were preserved, but inherited permissions from the old parent were dropped

**Resolution Steps:**
1. Check current permissions: Right-click folder > Sharing & Permissions
2. Compare with the expected permissions from the old location
3. Re-apply inherited permissions from the new parent: Sharing & Permissions > Advanced > "Re-inherit from parent"
4. Or explicitly grant access to the required groups/users

### Shared Links Broken After Migration
**Symptoms:** External shared links return "File not found" after a workspace migration.

**Common Causes:**
- File IDs changed during migration (if files were re-created instead of moved)
- Shared link settings were not migrated
- File was moved to a different NimbusVault location, changing the access path

**Resolution Steps:**
1. Locate the file in its new location using NimbusVault search
2. Generate a new shared link: Right-click > Share > Create Link
3. Distribute the new link to external recipients
4. For bulk link recovery: NimbusAdmin > NimbusVault > Shared Links > filter by "Broken" status

## Permission Audit

### Running a Permission Audit
1. Navigate to NimbusAdmin > NimbusVault > Permission Audit
2. Select the folder or workspace to audit
3. Click **Generate Report** — the report shows:
   - All users and groups with access
   - Permission source (direct, inherited, group, shared link)
   - Last access date per user
   - Overprivileged accounts (users with higher access than needed)
4. Export the report as CSV for compliance documentation

### Automated Permission Alerts
Configure alerts for permission changes:
- NimbusAdmin > Notifications > NimbusVault > Permission Changes
- Alert when: files shared externally, bulk permission changes, owner changes

## Best Practices

1. **Use group-based permissions** instead of individual user assignments — easier to manage during migrations
2. **Copy files instead of linking** when cloning workspaces, unless you need a single source of truth
3. **Run a permission audit** after any migration or restructuring
4. **Use the "Re-inherit from parent" option** after moving folders to simplify permission alignment
5. **Review and clean up shared links** quarterly — expired or unused links should be revoked

## Related Articles
- KB-009: Tenant Data Migration and Workspace Cloning
- KB-007: NimbusDocs Offline Sync and Conflict Resolution
- KB-004: NimbusAdmin Tenant and User Provisioning
