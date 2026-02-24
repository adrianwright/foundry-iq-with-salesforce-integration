# Username and UPN Change Procedure

**Article Number:** KB-014  
**Product:** NimbusID / NimbusAdmin  
**Category:** Identity & User Management  
**Last Updated:** February 2026

## Overview

This article covers the procedure for changing a user's username (email/UPN) in NimbusCloud, including the impact on SSO, SCIM provisioning, API tokens, and cross-product references. Username changes are common during name changes, corporate rebranding, and domain migrations.

## How Usernames Work in NimbusCloud

### Identity Fields
| Field | Description | Mutable | Used For |
|-------|-------------|---------|----------|
| **User ID** | Internal UUID, system-generated | No — immutable | API references, audit logs, internal cross-references |
| **Username / UPN** | Email address (e.g., `jane@company.com`) | Yes | Login, display, email notifications |
| **External ID** | IdP-assigned identifier (e.g., SCIM `externalId`) | Yes (via SCIM only) | IdP-to-NimbusCloud user matching |
| **Display Name** | First + Last name | Yes | UI display, @mentions |

### Key Principle
**The User ID is immutable** — it never changes regardless of username updates. All internal references (file ownership, task assignments, audit logs) use User ID. This means username changes don't break internal data references.

## Username Change Methods

### Method 1: Admin Manual Change
1. Navigate to NimbusAdmin > Users > search for the user
2. Click the user profile > Edit
3. Update the **Email / UPN** field
4. Click Save — the change takes effect immediately
5. The user must log in with the new email address going forward
6. Old email address receives a notification about the change

### Method 2: SCIM-Driven Change
If SCIM provisioning is configured (see KB-004):
1. Update the user's email/UPN in your IdP (Azure AD, Okta, etc.)
2. SCIM sync propagates the change to NimbusCloud automatically (5-40 minute delay)
3. No action needed in NimbusAdmin — the sync handles the update
4. Verify in NimbusAdmin > Users > [user] > Provisioning Log

### Method 3: Bulk Username Change (Domain Migration)
For changing all users from `@oldomain.com` to `@newdomain.com`:
1. Navigate to NimbusAdmin > Settings > Identity > Domain Migration
2. Enter the old domain and new domain
3. Preview the affected users (review carefully before proceeding)
4. Click **Start Migration** — changes are applied in batches
5. Monitor progress in NimbusAdmin > Settings > Identity > Migration Status

## Impact of Username Change

### What Updates Automatically
| System | Behavior |
|--------|----------|
| Login | New email required immediately |
| NimbusHub | @mentions show new display name; old messages retain context |
| NimbusDocs | File ownership transfers seamlessly (via User ID) |
| NimbusBoard | Task assignments preserved (via User ID) |
| NimbusVault | File permissions preserved (via User ID) |
| Audit logs | Historical entries retain the original username for accuracy |
| SCIM | ExternalID updated if IdP propagates the change |

### What Requires Manual Action
| System | Action Needed |
|--------|--------------|
| SSO / SAML | If NameID uses email, update the IdP attribute mapping |
| OAuth tokens | Existing tokens remain valid until expiry; no action needed |
| Shared links | Links use file ID, not username — no impact |
| External integrations | API calls using the old email as a parameter (e.g., `?email=old@company.com`) must be updated |
| Calendar invitations | Pending NimbusConnect meeting invites sent to old email won't forward — resend if needed |

## Common Issues

### SSO Fails After Username Change
**Symptoms:** User can't log in via SSO after their email was changed in NimbusCloud but not in the IdP.

**Resolution:**
1. Ensure the IdP NameID matches the new NimbusCloud email
2. If using SCIM, wait for the sync cycle to update both systems
3. If NameID uses a persistent ID (not email), no change is needed in the IdP
4. Check NimbusAdmin > Users > [user] > SSO Status for errors

### SCIM Sync Creates Duplicate User
**Symptoms:** After changing a username in the IdP, SCIM creates a new user instead of updating the existing one.

**Common Causes:**
- The SCIM connector matches on `userName` (email) instead of `externalId`
- Changing the email looks like a new user to the SCIM connector

**Resolution:**
1. Configure the SCIM connector to match on `externalId` (immutable) instead of `userName`
2. Delete the duplicate user in NimbusAdmin
3. Verify the original user's `externalId` matches the IdP record
4. Re-run a SCIM sync to verify correct matching

## Best Practices

1. **Always change the username in the IdP first** if SCIM is configured — let the sync propagate the change
2. **Use `externalId` for SCIM matching** instead of email to prevent duplicates during username changes
3. **Communicate username changes to users in advance** — they need to know their new login email
4. **Update external integrations** that reference the old email address
5. **Test SSO login** with the new username immediately after the change

## Related Articles
- KB-003: SSO and SAML Configuration Guide
- KB-004: NimbusAdmin Tenant and User Provisioning
- KB-008: MFA Setup and Troubleshooting
