# Support Case: File Permissions Broken After NimbusVault Migration

**Case Number**: CASE-013  
**Status**: Resolved  
**Priority**: High  
**Product**: NimbusVault  
**Category**: File Management & Permissions  
**Origin**: Web  
**Contact**: Michelle Tanaka, IT Operations Manager, Bridgewater Associates  
**Account**: Bridgewater Associates  
**Created**: February 17, 2026  
**Last Updated**: February 22, 2026

---

## Subject
350 users reporting "Access Denied" on files after workspace restructuring and NimbusVault folder migration

## Description
Michelle Tanaka reported that after restructuring their NimbusCloud workspace hierarchy (consolidating 12 department workspaces into 4 division-level workspaces), approximately 350 users cannot access files in the migrated NimbusVault folders. Files that were previously accessible now return "Access Denied." The migration was performed over the weekend by moving 8 top-level NimbusVault folders into new parent folders.

## Investigation Notes

**2026-02-17 — Initial Triage (Support Engineer: Chris Nakamura)**
- Confirmed "Access Denied" errors for files in 8 migrated folders
- Permission audit (NimbusAdmin > NimbusVault > Permission Audit) revealed:
  - Inherited permissions from old parent folders were dropped when folders were moved
  - New parent folders have a more restrictive permission set (division-level groups only, not department-level groups)
  - Direct permissions on individual files were preserved, but most users had access via inheritance
- Impact: ~4,200 files across 8 folders, affecting 350 users in 12 former department groups

**2026-02-18 — Remediation Plan**
- Option A: Re-inherit permissions from new parent folders and add department groups to division groups (recommended)
- Option B: Bulk-add all 12 department groups to all 8 migrated folders (quick fix but creates permission sprawl)
- Michelle chose Option A

**2026-02-19 — Permission Restructuring**
- Step 1: Added department groups as nested members of the appropriate division groups in NimbusAdmin
- Step 2: Applied "Re-inherit from parent" on all 8 migrated folders: Right-click > Sharing & Permissions > Advanced > Re-inherit from parent
- Step 3: Verified access for 10 sample users across different departments — all files accessible

**2026-02-22 — Resolution Confirmed**
- Michelle confirmed all 350 users have file access restored
- Permission audit re-run: no orphaned permissions, no overprivileged accounts
- Bridgewater team documented the folder migration procedure with a "re-inherit permissions" step for future restructuring
- Recommended running a permission audit before and after any folder migration (per KB-013)

## Resolution
Moving NimbusVault folders to new parent folders dropped inherited permissions. Fixed by nesting department groups into division groups and re-inheriting permissions from the new parent hierarchy. KB-013 documents file permission behavior during migrations.

## Related Articles
- KB-013: NimbusVault File Permissions After Workspace Migration
- KB-009: Tenant Data Migration and Workspace Cloning
- FORUM-013: File Access Denied After Workspace Migration
