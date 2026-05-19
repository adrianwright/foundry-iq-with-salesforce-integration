# ZavaAdmin Tenant and User Provisioning

**Article Number:** KB-004  
**Product:** ZavaAdmin / ZavaID  
**Category:** Tenant Management & User Lifecycle  
**Last Updated:** February 2026

## Overview

ZavaAdmin is the centralized administration console for the ZavaCloud platform. This article covers tenant setup, user provisioning (manual and automated via SCIM), group synchronization from HR systems, and dashboard configuration for monitoring user activity.

## User Provisioning Methods

### Manual Provisioning
Suitable for small teams (< 50 users):

1. Navigate to ZavaAdmin > Users > Add User
2. Enter email address, first name, last name, and department
3. Assign product licenses (ZavaHub, ZavaDocs, ZavaBoard, ZavaConnect, ZavaVault)
4. Assign role: User, Power User, or Admin
5. Click Create — the user receives a welcome email with setup instructions

### CSV Bulk Import
Suitable for initial onboarding (50-5,000 users):

1. Navigate to ZavaAdmin > Users > Bulk Import
2. Download the CSV template
3. Fill in columns: `email`, `firstName`, `lastName`, `department`, `role`, `licenses` (comma-separated)
4. Upload the CSV and review the preview
5. Click Import — users are created in batches of 100

### SCIM Provisioning (Recommended)
Automated user lifecycle management synced from your identity provider:

1. In ZavaAdmin, navigate to Settings > Identity > SCIM Provisioning
2. Click **Enable SCIM** to generate a SCIM endpoint URL and Bearer token
3. In your IdP (Azure AD, Okta, etc.), configure a SCIM 2.0 provisioning connector:
   - **Tenant URL**: `https://scim.ZavaCloud.io/v2/{tenant-id}`
   - **Secret Token**: (generated in step 2)
4. Map attributes: `userName` → email, `displayName`, `department`, `groups`
5. Set provisioning scope (all users or specific groups)
6. Enable provisioning and run an initial sync

### SCIM Sync Schedule
| Event | Trigger | Latency |
|-------|---------|---------|
| New user in IdP | Automatic | 5-40 minutes (IdP-dependent) |
| User attribute change | Automatic | 5-40 minutes |
| User deactivation | Automatic | 5-40 minutes |
| Full sync | Manual or scheduled | Depends on user count |

## Group Synchronization

ZavaCloud supports syncing groups from your IdP or HR system for role-based access:

1. **IdP Groups** — Synced automatically via SCIM. IdP group membership maps to ZavaCloud teams and product access.
2. **HR System Groups** — Use the ZavaAPI to sync department/cost-center groups from Workday, BambooHR, or SAP SuccessFactors (see KB-011 for API details).

### Group-to-License Mapping
Configure automatic license assignment based on group membership:

| Group | Auto-Assigned Licenses |
|-------|----------------------|
| Engineering | ZavaHub, ZavaDocs, ZavaBoard, ZavaVault |
| Sales | ZavaHub, ZavaDocs, ZavaConnect |
| Executive | All products |
| Contractors | ZavaHub, NimmbusDocs |

Configure at: ZavaAdmin > Settings > Licensing > Group Mapping

## Common Provisioning Issues

### Ghost/Phantom User Accounts
**Symptoms:** Users appear in ZavaAdmin that don't exist in the IdP, or deactivated users reappear.

**Common Causes:**
- SCIM deprovisioning action set to "Disable" instead of "Delete"
- Multiple SCIM connectors creating duplicate users
- IdP soft-delete vs hard-delete mismatch

**Resolution:**
1. Check ZavaAdmin > Users > filter by "Source: SCIM" to see all SCIM-provisioned users
2. In the IdP, verify the SCIM provisioning logs for errors
3. Set deprovisioning action to "Soft delete" in ZavaAdmin (preserves data for 30 days, then auto-purges)
4. If duplicates exist, merge accounts: ZavaAdmin > Users > select duplicates > Merge

### Dashboard Widgets Not Loading
**Symptoms:** ZavaAdmin analytics dashboard shows blank widgets or "Data unavailable" errors.

**Common Causes:**
- Browser ad-blocker blocking analytics endpoints
- Insufficient admin permissions (requires "Analytics Viewer" role or higher)
- Data pipeline delay (fresh tenants may take 24 hours for initial data)

**Resolution:**
1. Disable ad-blockers for `*.ZavaCloud.io`
2. Verify role: ZavaAdmin > Users > (your user) > Roles — must include "Analytics Viewer"
3. For new tenants, wait 24 hours for the analytics pipeline to populate
4. Clear browser cache and try an incognito window

## User Lifecycle Management

### Recommended Workflow
1. **Onboarding**: SCIM auto-creates user → welcome email → MFA setup (see KB-008)
2. **Role changes**: Update group membership in IdP → SCIM syncs to ZavaCloud → licenses adjust automatically
3. **Offboarding**: Disable user in IdP → SCIM deactivates in ZavaCloud → 30-day data retention → auto-purge
4. **Rehire**: Re-enable in IdP → SCIM reactivates if within 30 days, otherwise creates new account

## Best Practices

1. **Use SCIM provisioning** for organizations with 50+ users — eliminates manual account management
2. **Map IdP groups to licenses** to ensure automatic, policy-driven license assignment
3. **Set deprovisioning to soft-delete** to avoid accidental data loss
4. **Audit provisioning logs monthly** in ZavaAdmin > Settings > Identity > SCIM Logs
5. **Test SCIM sync with a pilot group** before enabling for the full organization

## Related Articles
- KB-003: SSO and SAML Configuration Guide
- KB-014: Username and UPN Change Procedure
- KB-011: ZavaAPI Rate Limits and Integration Best Practices
