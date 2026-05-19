# Support Case: OAuth Cert Rotation Breaking Third-Party Integrations

**Case Number**: CASE-006  
**Status**: Resolved  
**Priority**: Critical  
**Product**: ZavaID / ZavaAPI  
**Category**: Authentication & Integration  
**Origin**: Phone  
**Contact**: James Okafor, Integration Architect, Atlas Retail Group  
**Account**: Atlas Retail Group  
**Created**: February 5, 2026  
**Last Updated**: February 8, 2026

---

## Subject
Slack and Jira integrations broken after ZavaCloud JWKS key rotation — all OAuth tokens rejected

## Description
James Okafor reported that all third-party integrations (Slack, Jira, Zapier, and 3 custom internal apps) stopped working at approximately 02:00 UTC on February 5. All API calls return 401 Unauthorized. The issue began immediately after ZavaCloud's scheduled JWKS key rotation.

## Investigation Notes

**2026-02-05 — Initial Triage (Support Engineer: Priya Sharma)**
- Confirmed JWKS key rotation occurred at 01:45 UTC as part of scheduled maintenance
- New signing key (`kid: zava-2026-02`) was published to `/.well-known/jwks.json` 24 hours prior
- Atlas's Slack and Jira integrations are using a middleware proxy that caches the JWKS key set
- The proxy is not refreshing JWKS when it encounters an unknown `kid` — it fails with 401 instead
- Custom internal apps have the JWKS key hardcoded (not fetched dynamically)

**2026-02-05 — Immediate Fix**
- Provided the current JWKS key set to James for manual update in custom apps
- Guided James through updating the middleware proxy configuration to:
  1. Fetch JWKS dynamically from `https://auth.ZavaCloud.io/.well-known/jwks.json`
  2. Cache for 1 hour but refresh when encountering an unknown `kid`
- Slack and Jira integrations restored within 30 minutes of proxy update

**2026-02-06 — Custom Apps Updated**
- James updated all 3 custom internal apps to fetch JWKS dynamically
- Tested with a simulated key rotation — all apps handled the new key correctly

**2026-02-08 — Post-Incident Review**
- Root cause: Static JWKS key caching without refresh-on-unknown-kid logic
- Recommended Atlas subscribe to ZavaCloud's certificate rotation calendar (ZavaAdmin > Notifications > Certificate Events)
- KB-006 provides the full JWKS best practice guidance

## Resolution
Middleware proxy updated to dynamically fetch JWKS keys with refresh-on-unknown-kid logic. Custom apps migrated from hardcoded keys to dynamic JWKS endpoint. All integrations restored. KB-006 referenced for ongoing OAuth/OIDC integration guidance.

## Related Articles
- KB-006: OAuth 2.0 and OIDC Integration Troubleshooting
- KB-003: SSO and SAML Configuration Guide
- FORUM-006: OAuth Cert Renewal Broke Our Slack Integration
