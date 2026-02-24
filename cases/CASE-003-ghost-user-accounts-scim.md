# Support Case: Ghost User Accounts After SCIM Sync

**Case Number**: CASE-003  
**Status**: Escalated  
**Priority**: High  
**Product**: NimbusID / NimbusAdmin  
**Category**: Identity & Provisioning  
**Origin**: Web  
**Contact**: David Chen, Directory Services Admin, Northgate Financial  
**Account**: Northgate Financial  
**Created**: January 28, 2026  
**Last Updated**: February 5, 2026

---

## Subject
SCIM provisioning creating duplicate/ghost user accounts — 47 phantom users found

## Description
David Chen reported discovering 47 user accounts in NimbusAdmin that do not correspond to any active users in their Azure AD (Entra ID) directory. These "ghost" accounts were created by SCIM provisioning and appear to be duplicates of existing users with slightly different email formats. Some ghost accounts have accessed NimbusHub and NimbusDocs, consuming licenses.

## Investigation Notes

**2026-01-28 — Initial Triage (Support Engineer: Rachel Torres)**
- Audited NimbusAdmin user list: 47 accounts sourced from SCIM with no matching Active Directory record
- Pattern identified: ghost accounts use `firstname.lastname@northgatefinancial.com` format while real accounts use `flastname@northgatefinancial.com`
- Root cause: Northgate Financial recently migrated from on-prem AD to Entra ID, changing UPN format
- SCIM connector is matching on `userName` (email) instead of `externalId`
- When UPN changed, SCIM treated the new format as new users instead of updating existing ones

**2026-01-30 — Remediation Plan**
- Step 1: Switch SCIM matching attribute from `userName` to `externalId` (Azure AD Object ID)
- Step 2: Merge duplicate accounts — map ghost account data to the real account
- Step 3: Delete the 47 ghost accounts after data merge
- Step 4: Re-run full SCIM sync to verify correct matching

**2026-02-03 — Remediation Executed**
- SCIM connector updated to match on `externalId`
- 38 of 47 ghost accounts had no meaningful data — deleted directly
- 9 ghost accounts had NimbusDocs files and NimbusBoard task assignments — data merged to real accounts before deletion
- Full SCIM sync ran successfully — all users matched correctly, no new duplicates

**2026-02-05 — Escalation to Engineering**
- Escalated as feature request: NimbusCloud should warn admins when SCIM creates users that closely match existing accounts (fuzzy duplicate detection)
- Engineering acknowledged — tracking as enhancement for Q3 2026

## Resolution
SCIM matching attribute changed from `userName` to `externalId` to prevent UPN format changes from creating duplicates. 47 ghost accounts cleaned up (9 with data merged, 38 deleted). Full guide in KB-004.

## Related Articles
- KB-004: NimbusAdmin Tenant and User Provisioning
- KB-014: Username and UPN Change Procedure
- FORUM-003: Phantom Accounts from SCIM Sync
