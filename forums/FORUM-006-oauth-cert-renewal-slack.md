# Community Forum: OAuth Cert Renewal Broke Our Slack Integration

**Article Number**: FORUM-006  
**Category**: Authentication & Integration  
**Product**: ZavaID / ZavaAPI

---

## Thread: ZavaCloud JWKS key rotation broke ALL our third-party integrations overnight

**Posted by:** @JamesO_Atlas | February 5, 2026

At approximately 02:00 UTC today, every single one of our third-party integrations (Slack, Jira, Zapier, and 3 custom apps) stopped working. All API calls are returning 401 Unauthorized. I believe it's related to the JWKS key rotation that was mentioned in the maintenance notice. Anyone else affected?

---

### Reply 1

**Posted by:** @DevOps_Sandra | February 5, 2026

Same here. Our Slack integration died at the exact same time. After some digging, the issue is:

The new signing key (`kid: zava-2026-02`) was published to the JWKS endpoint 24 hours before the rotation, but if your app cached the old JWKS keys and doesn't refresh on unknown `kid`, it rejects all new tokens.

**Quick fix:** Manually fetch the current JWKS from `https://auth.ZavaCloud.io/.well-known/jwks.json` and update your app config.

**Permanent fix:** Make your app fetch JWKS dynamically and refresh the cache when it encounters an unknown `kid`.

---

### Reply 2

**Posted by:** @JamesO_Atlas | February 5, 2026

@DevOps_Sandra That was it — our middleware proxy was caching the JWKS statically. Updated the proxy to fetch dynamically and everything is back. ZavaCloud support (CASE-006) confirmed the same approach.

But I'm frustrated that this broke things. Shouldn't ZavaCloud keep the old key valid for a grace period?

---

### Reply 3

**Posted by:** @Security_Expert_Dana | February 5, 2026

@JamesO_Atlas ZavaCloud actually does — the old key is still in the JWKS endpoint for 7 days after rotation. Tokens signed with the old key remain valid during that grace period. The issue is when your app ONLY accepts tokens with a specific `kid` and doesn't fetch the JWKS dynamically.

This is actually standard OAuth/OIDC behavior. AWS, Azure AD, and Google all rotate keys the same way. The OIDC spec expects relying parties to fetch JWKS dynamically.

---

### Reply 4

**Posted by:** @JamesO_Atlas | February 6, 2026

Fair point. For anyone else reading this, here's what I changed in our Node.js middleware:

```javascript
// BEFORE (broken) — static key
const publicKey = fs.readFileSync('./zava-public-key.pem');

// AFTER (correct) — dynamic JWKS
const jwksClient = require('jwks-rsa');
const client = jwksClient({
  jwksUri: 'https://auth.ZavaCloud.io/.well-known/jwks.json',
  cache: true,
  cacheMaxAge: 3600000, // 1 hour
  rateLimit: true
});
```

The `jwks-rsa` library automatically refreshes the key set when it encounters an unknown `kid`.

---

### Reply 5

**Posted by:** @DevOps_Sandra | February 6, 2026

Good approach. We also subscribed to ZavaCloud's certificate rotation calendar (ZavaAdmin > Notifications > Certificate Events) so we get a heads-up 7 days before any rotation. Gives us time to verify our integrations are ready.

KB-006 has the complete guide on OAuth/OIDC integration patterns and JWKS best practices.

---

### Reply 6

**Posted by:** @IntegrationNewbie_Alex | February 8, 2026

Thanks for this thread — I was about to hardcode our JWKS key for our new custom app. Definitely going with the dynamic fetch approach now!
