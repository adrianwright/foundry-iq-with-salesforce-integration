# OAuth 2.0 and OIDC Integration Troubleshooting

**Article Number:** KB-006  
**Product:** NimbusID / NimbusAPI  
**Category:** Authentication & Integration  
**Last Updated:** February 2026

## Overview

NimbusCloud supports OAuth 2.0 and OpenID Connect (OIDC) for third-party application integrations. This article covers common integration issues including token refresh failures, JWKS key rotation problems, and third-party app SSO breakages after certificate renewals.

## Supported OAuth 2.0 Flows

| Flow | Use Case | Token Lifetime |
|------|----------|---------------|
| Authorization Code + PKCE | Web and mobile apps with user interaction | Access: 1 hour, Refresh: 30 days |
| Client Credentials | Server-to-server (no user context) | Access: 1 hour |
| Device Authorization | CLI tools, smart devices | Access: 1 hour, Refresh: 30 days |
| Implicit (deprecated) | Legacy SPAs — migrate to Auth Code + PKCE | Access: 30 minutes, no refresh |

## OAuth Endpoints
```
Authorization: https://auth.nimbuscloud.io/oauth2/authorize
Token:         https://auth.nimbuscloud.io/oauth2/token
UserInfo:      https://auth.nimbuscloud.io/oauth2/userinfo
JWKS:          https://auth.nimbuscloud.io/.well-known/jwks.json
Discovery:     https://auth.nimbuscloud.io/.well-known/openid-configuration
```

## Common Integration Issues

### Token Refresh Failure ("invalid_grant")
**Symptoms:** Third-party integrations stop working after the access token expires. Refresh token request returns `invalid_grant`.

**Common Causes:**
- Refresh token has expired (30-day lifetime)
- Refresh token was already used (NimbusCloud uses single-use refresh tokens with rotation)
- User's password was changed or account was deactivated
- OAuth app permissions were revoked by an admin

**Resolution Steps:**
1. Check if the refresh token is within its 30-day lifetime
2. Verify the app isn't attempting to reuse a consumed refresh token — each refresh returns a new refresh token
3. Check if the user's account is still active: NimbusAdmin > Users > search by email
4. Re-authorize the integration: have the user complete the OAuth flow again
5. For client credentials flow: verify the client secret hasn't expired (check NimbusAdmin > Apps > [app] > Credentials)

### JWKS Key Rotation Breaking Integrations
**Symptoms:** Third-party apps that validate NimbusCloud JWT tokens start rejecting all tokens after a key rotation.

**Common Causes:**
- App caches the JWKS key set and doesn't refresh it when encountering an unknown `kid` (Key ID)
- Static JWKS key imported into the app instead of fetching dynamically from the JWKS endpoint
- Key rotation happened during a maintenance window and the new key wasn't available for a few minutes

**Resolution Steps:**
1. Ensure the third-party app fetches JWKS dynamically from `https://auth.nimbuscloud.io/.well-known/jwks.json`
2. The app should cache JWKS keys but refresh when it encounters an unrecognized `kid` in a JWT header
3. NimbusCloud publishes the new key 24 hours before rotating. Set up monitoring on the JWKS endpoint to detect changes
4. If using a static key, re-download the current JWKS and update the app configuration

### Certificate Renewal Breaking Third-Party SSO
**Symptoms:** After NimbusCloud's TLS or SAML signing certificate is renewed, third-party integrations that rely on certificate pinning break.

**Common Causes:**
- App uses certificate pinning instead of trusting the CA chain
- SAML IdP trust is configured with a specific certificate thumbprint that changed
- Certificate renewal changed the intermediate CA (rare but possible)

**Resolution Steps:**
1. Download the new certificate from NimbusAdmin > Settings > Identity > Certificates
2. Update the certificate in all relying party trusts / third-party apps
3. Migrate from certificate pinning to CA-chain trust where possible
4. Subscribe to NimbusCloud's certificate rotation calendar: NimbusAdmin > Notifications > Certificate Events

### Third-Party App Integration Examples

| App | Integration Type | Common Issues |
|-----|-----------------|---------------|
| Slack | OAuth 2.0 (Auth Code) | Token refresh; redirect URI mismatch |
| Jira | OAuth 2.0 (Auth Code) | Scope changes after Jira upgrade |
| Zapier | OAuth 2.0 (Auth Code + PKCE) | Rate limiting on webhook triggers |
| Custom internal apps | Client Credentials | Secret expiration; IP allowlist |
| Power Automate | OAuth 2.0 (Auth Code) | Consent prompt for new scopes |

## Registering a Third-Party OAuth App

1. Navigate to NimbusAdmin > Settings > Apps > Register App
2. Enter app name, description, and redirect URIs
3. Select the OAuth flow type and required scopes
4. Generate client ID and client secret
5. Set client secret expiration (90 days, 180 days, or 1 year)
6. Configure allowed origins for CORS (web apps)
7. Save and distribute credentials securely to the app developer

## Best Practices

1. **Use Auth Code + PKCE** for all new web and mobile integrations
2. **Never embed client secrets** in client-side code — use backend proxy or PKCE
3. **Handle token rotation** — always store the new refresh token returned from a refresh request
4. **Set up secret expiration alerts** — NimbusAdmin > Notifications > App Credential Events
5. **Use the minimum required scopes** — follow principle of least privilege

## Related Articles
- KB-003: SSO and SAML Configuration Guide
- KB-011: NimbusAPI Rate Limits and Integration Best Practices
- KB-008: MFA Setup and Troubleshooting
