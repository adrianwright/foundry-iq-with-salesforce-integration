# Support Case: Bulk Workspace Clone Failures in NimbusBoard

**Case Number**: CASE-009  
**Status**: Resolved  
**Priority**: Medium  
**Product**: NimbusBoard  
**Category**: Data Migration & Templates  
**Origin**: Web  
**Contact**: Karen Johansson, PMO Lead, Crestview Technologies  
**Account**: Crestview Technologies  
**Created**: February 12, 2026  
**Last Updated**: February 18, 2026

---

## Subject
Bulk workspace clone job failing — 73 of 200 workspaces not cloned for Q2 planning

## Description
Karen Johansson reported that a bulk workspace clone operation for quarterly planning failed partially. 127 of 200 workspaces were cloned successfully, but 73 failed with various errors. Crestview Technologies clones all project workspaces at the start of each quarter as a template for the new quarter's planning. The Q2 deadline is approaching and the cloning needs to be completed.

## Investigation Notes

**2026-02-12 — Initial Triage (Support Engineer: Maya Singh)**
- Reviewed bulk clone job log: NimbusAdmin > NimbusBoard > Bulk Operations > Job #BK-2026-0212
- Failure breakdown:
  - 41 workspaces: "Clone timeout — workspace exceeds 10,000 cards" (above single-clone limit)
  - 22 workspaces: "Integration clone failed — external webhook references invalid" (Slack webhook URLs)
  - 10 workspaces: "Attachment size limit exceeded — total attachments > 5 GB"

**2026-02-13 — Remediation Steps**
- **41 oversized workspaces**: Advised Karen to archive cards older than 6 months before re-cloning. Provided bulk archive script via NimbusAPI: `POST /api/v2/workspaces/{id}/cards/archive` with filter `created_before=2025-08-01`
- **22 integration failures**: Cloned these workspaces without integrations (uncheck "Automations and rules" in clone options), then manually re-added Slack webhook integrations with new Q2 channel URLs
- **10 attachment limit**: Cloned without attachments, then migrated files to new workspace's NimbusVault folder separately

**2026-02-15 — Re-clone Executed**
- Karen's team archived 340,000+ old cards across the 41 oversized workspaces
- Re-ran bulk clone for all 73 failed workspaces — 71 succeeded
- 2 remaining failures: workspaces had corrupted automation rules. Deleted the corrupted rules and cloned manually

**2026-02-18 — Resolution Confirmed**
- All 200 workspaces successfully cloned for Q2
- Karen's team implemented a quarterly pre-clone checklist: archive old cards, verify webhook URLs, check attachment sizes
- Suggested feature request: NimbusBoard should auto-skip oversized workspaces and report them separately instead of failing the entire batch

## Resolution
73 clone failures resolved by archiving old cards (reducing below 10,000 limit), cloning without integrations then re-adding, and cloning without oversized attachments. 2 workspaces with corrupted automations fixed by deleting and re-creating rules. KB-009 documents bulk cloning best practices.

## Related Articles
- KB-009: Tenant Data Migration and Workspace Cloning
- KB-011: NimbusAPI Rate Limits and Integration Best Practices
- FORUM-009: Bulk Workspace Cloning Tips and Gotchas
