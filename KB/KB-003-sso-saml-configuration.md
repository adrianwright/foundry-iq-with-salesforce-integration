# SSO and SAML Configuration Guide

**Article Number:** KB-003  
**Product:** NimbusID  
**Category:** Authentication & Identity  
**Last Updated:** February 2026

## Overview

NimbusID is the identity and access management service for the NimbusCloud platform. This article covers single sign-on (SSO) configuration using SAML 2.0 and OIDC, including federation with common identity providers (IdPs) like Azure AD (Entra ID), Okta, and Google Workspace.

## Supported SSO Protocols

| Protocol | Use Case | Status |
|----------|----------|--------|
| SAML 2.0 | Enterprise SSO with on-prem or cloud IdPs | Fully supported |
| OIDC (OpenID Connect) | Modern cloud-native SSO | Fully supported |
| LDAP | Legacy directory bind (read-only) | Supported via NimbusID Bridge |

## SAML 2.0 Configuration

### Prerequisites
- NimbusCloud Enterprise or Business plan
- Admin access to both NimbusAdmin and your IdP
- IdP metadata XML or manual configuration values (Entity ID, SSO URL, Certificate)

### Step-by-Step Setup

1. **In NimbusAdmin**, navigate to: Settings > Identity > SSO Configuration
2. Click **Add Identity Provider** > Select **SAML 2.0**
3. Enter the **Connection Name** (e.g., "Corporate AD")
4. Upload the **IdP Metadata XML** file, or enter manually:
   - **Entity ID**: `https://idp.yourcompany.com/metadata`
   - **SSO URL**: `https://idp.yourcompany.com/sso/saml`
   - **Certificate**: Upload the X.509 signing certificate from your IdP
5. Configure **Attribute Mapping**:
   - `email` → NameID or `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress`
   - `firstName` → `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname`
   - `lastName` → `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname`
   - `groups` → (optional) for role-based access mapping
6. **Download NimbusCloud SP Metadata** from the configuration page
7. Upload the SP metadata to your IdP and create a relying party trust
8. Click **Test Connection** — this will open a new browser tab and attempt a SAML login flow
9. Once the test succeeds, click **Enable** to activate SSO

### NimbusCloud SP (Service Provider) Details
```
Entity ID:       https://auth.nimbuscloud.io/saml/metadata/{tenant-id}
ACS URL:         https://auth.nimbuscloud.io/saml/acs/{tenant-id}
SLO URL:         https://auth.nimbuscloud.io/saml/slo/{tenant-id}
NameID Format:   urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress
```

## Common SSO Issues

### Error: "SAML Response Signature Validation Failed"
**Causes:**
- IdP certificate has been rotated but not updated in NimbusAdmin
- Clock skew between IdP and NimbusCloud exceeds 5 minutes
- Response is signed with SHA-1 but NimbusCloud requires SHA-256

**Resolution:**
1. Re-download the IdP signing certificate and upload to NimbusAdmin > SSO > Certificates
2. Verify NTP sync on the IdP server (clock skew must be < 5 minutes)
3. Configure IdP to sign with SHA-256 (NimbusCloud does not accept SHA-1 as of January 2026)

### Error: "User Not Found — No Matching Account"
**Causes:**
- NameID in SAML assertion doesn't match any NimbusCloud user email
- User hasn't been provisioned in NimbusCloud (SCIM not configured or manual provisioning required)
- Email domain mismatch (e.g., `user@subsidiary.com` vs `user@company.com`)

**Resolution:**
1. Check the NameID value in the SAML assertion (use browser SAML tracer extension)
2. Verify the user exists in NimbusAdmin > Users with the matching email
3. Enable Just-in-Time (JIT) provisioning to auto-create users on first SSO login
4. Add additional email domains under Settings > Identity > Verified Domains

### Error: "SSO Loop — Redirect Cycle Detected"
**Causes:**
- ACS URL misconfigured in the IdP (trailing slash mismatch)
- Multiple IdPs configured and NimbusCloud can't determine which one to use
- Browser cookies blocked or third-party cookie restrictions

**Resolution:**
1. Verify ACS URL exactly matches: `https://auth.nimbuscloud.io/saml/acs/{tenant-id}` (no trailing slash)
2. If multiple IdPs are configured, set a default IdP or use email-domain-based routing
3. Ensure cookies for `*.nimbuscloud.io` are not blocked by browser privacy settings

## OIDC Configuration

For OIDC-based SSO (preferred for Azure AD / Entra ID and Google Workspace):

1. Navigate to NimbusAdmin > Settings > Identity > SSO Configuration
2. Click **Add Identity Provider** > Select **OpenID Connect**
3. Enter the **Discovery URL**: `https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration`
4. Enter the **Client ID** and **Client Secret** from your IdP app registration
5. Configure scopes: `openid profile email`
6. Map claims to NimbusCloud attributes (email, name, groups)
7. Test and enable

## Best Practices

1. **Use OIDC over SAML** when your IdP supports it — simpler configuration, better token refresh
2. **Enable SCIM provisioning** (see KB-004) to automatically sync users and avoid "User Not Found" errors
3. **Set up IdP-initiated and SP-initiated SSO** for maximum compatibility
4. **Rotate IdP certificates proactively** — set a calendar reminder 30 days before expiry
5. **Test SSO with a non-admin account** before rolling out to all users

## Related Articles
- KB-004: NimbusAdmin Tenant and User Provisioning
- KB-006: OAuth 2.0 and OIDC Integration Troubleshooting
- KB-008: MFA Setup and Troubleshooting
- KB-014: Username and UPN Change Procedure
