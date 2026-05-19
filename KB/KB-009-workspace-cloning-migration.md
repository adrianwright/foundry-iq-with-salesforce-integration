# Tenant Data Migration and Workspace Cloning

**Article Number:** KB-009  
**Product:** ZavaBoard / ZavaAdmin  
**Category:** Data Migration & Templates  
**Last Updated:** February 2026

## Overview

This article covers workspace migration, bulk cloning, and project templates in ZavaBoard and across the ZavaCloud platform. These operations are commonly performed during organizational restructuring, team onboarding, and quarterly planning cycles.

## Workspace Cloning in ZavaBoard

### Single Workspace Clone
1. Open the source workspace in ZavaBoard
2. Click the workspace menu (⋯) > **Clone Workspace**
3. Choose what to include:
   - ✅ Board structure (columns, swimlanes)
   - ✅ Card templates (without actual cards)
   - ☐ Active cards (optional — includes all current cards)
   - ☐ Archived cards (optional)
   - ☐ Automations and rules
   - ☐ Member assignments
4. Enter a name for the cloned workspace
5. Click **Clone** — processing time depends on workspace size

### Bulk Workspace Cloning
For cloning multiple workspaces (e.g., quarterly planning reset):

1. Navigate to ZavaAdmin > ZavaBoard > Bulk Operations
2. Click **Bulk Clone**
3. Select source workspaces (up to 200 at a time)
4. Configure clone options (same as single clone)
5. Set naming pattern: `{original_name} — Q2 2026` or custom prefix/suffix
6. Click **Start Bulk Clone** — runs as a background job

### Bulk Clone Performance

| Workspace Count | Avg. Cards per Workspace | Estimated Time |
|----------------|-------------------------|----------------|
| 1-10 | < 100 | < 1 minute |
| 10-50 | < 100 | 2-5 minutes |
| 50-200 | < 100 | 5-15 minutes |
| 50-200 | > 500 | 15-45 minutes |
| 200+ | Any | Use off-peak hours |

## Common Cloning Issues

### Bulk Clone Failures (Partial Completion)
**Symptoms:** Bulk clone job reports partial failure — some workspaces cloned, others show "Error."

**Common Causes:**
- Source workspace has custom integrations (Slack notifications, Jira sync) that can't be auto-cloned
- Workspace exceeds 10,000 cards — above the single-clone limit
- API rate limits hit during bulk operation (see KB-011)
- Workspace contains file attachments exceeding 5 GB total

**Resolution Steps:**
1. Check the bulk job log: ZavaAdmin > ZavaBoard > Bulk Operations > Job History > [job] > View Log
2. For workspaces with custom integrations: clone without integrations, then manually re-add
3. For oversized workspaces: archive old cards before cloning to reduce below the 10,000 limit
4. For attachment limits: clone without attachments, then migrate files separately via ZavaVault
5. Retry failed workspaces individually

### Automations Not Working After Clone
**Symptoms:** Cloned workspace has automations listed but they don't trigger.

**Common Causes:**
- Automations reference specific users or channels that don't exist in the new workspace context
- Webhook URLs from the source workspace are still pointed at the original workspace
- Automation credentials (for external integrations) weren't carried over

**Resolution Steps:**
1. Open each automation in the cloned workspace: Workspace Settings > Automations
2. Update user/channel references to the new workspace members
3. Regenerate webhook URLs for the cloned workspace
4. Re-authenticate any external integration connections

## Project Template Library

### Creating Templates
1. Open an existing workspace or create a new one with the desired structure
2. Click workspace menu (⋯) > **Save as Template**
3. Choose what to include in the template (same options as cloning)
4. Add a description and tags for discoverability
5. Choose visibility: **Personal**, **Team**, or **Organization**
6. Click **Save Template**

### Using Templates
1. Click **New Workspace** > **From Template**
2. Browse or search the template library
3. Select a template and click **Use Template**
4. Customize the workspace name and settings
5. Click **Create**

### Organization Template Library
Admins can manage organization-wide templates:
- ZavaAdmin > ZavaBoard > Templates
- Pin recommended templates for new teams
- Retire outdated templates (archive, don't delete — existing workspaces aren't affected)

## Cross-Product Data Migration

### Migrating Between ZavaCloud Tenants
For organizational restructuring (mergers, divestitures):

1. **Export from source tenant**: ZavaAdmin > Data Management > Export
   - Select products: ZavaBoard workspaces, ZavaDocs documents, ZavaVault files
   - Export generates a `.zavaexport` archive
2. **Import to destination tenant**: ZavaAdmin > Data Management > Import
   - Upload the `.zavaexport` archive
   - Map users from source to destination tenant
   - Review and confirm the import plan
3. Post-migration:
   - Verify all content migrated successfully
   - Re-configure SSO and SCIM for the destination tenant (see KB-003, KB-004)
   - Update any external integrations pointing to the old tenant

## Best Practices

1. **Clone during off-peak hours** (evenings, weekends) for bulk operations of 50+ workspaces
2. **Archive old cards before cloning** to keep workspace size manageable
3. **Use templates** for repeating project structures instead of cloning ad-hoc
4. **Test bulk clone with 2-3 workspaces first** before running the full batch
5. **Document custom integrations** in each workspace so they can be manually re-added after cloning

## Related Articles
- KB-007: ZavaDocs Offline Sync and Conflict Resolution
- KB-013: ZavaVault File Permissions After Workspace Migration
- KB-011: ZavaAPI Rate Limits and Integration Best Practices
