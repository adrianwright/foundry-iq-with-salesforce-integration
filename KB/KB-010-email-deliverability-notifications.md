# Email Deliverability and Notification Configuration

**Article Number:** KB-010  
**Product:** NimbusCloud Platform  
**Category:** Email & Notifications  
**Last Updated:** February 2026

## Overview

NimbusCloud sends notifications via email for events across all products — chat mentions in NimbusHub, document shares in NimbusDocs, meeting invitations in NimbusConnect, task assignments in NimbusBoard, and security alerts from NimbusID. This article covers email deliverability configuration (SPF, DKIM, DMARC), custom sender domains, and notification management.

## Default Email Configuration

By default, NimbusCloud sends all notifications from:
```
From: notifications@nimbuscloud.io
Reply-To: no-reply@nimbuscloud.io
```

These emails pass SPF, DKIM, and DMARC checks automatically. No configuration is needed for the default sender.

## Custom Sender Domain

Organizations can send NimbusCloud notifications from their own domain (e.g., `notifications@yourcompany.com`):

### Setup Steps
1. Navigate to NimbusAdmin > Settings > Email > Custom Sender Domain
2. Enter your custom "From" domain (e.g., `yourcompany.com`)
3. NimbusCloud generates DNS records you must add:

**SPF Record:**
```
v=spf1 include:spf.nimbuscloud.io ~all
```
Add this to your existing SPF record, or create one if none exists.

**DKIM Record:**
```
nimbuscloud._domainkey.yourcompany.com  TXT  "v=DKIM1; k=rsa; p=<generated-public-key>"
```

**DMARC Record (recommended):**
```
_dmarc.yourcompany.com  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@yourcompany.com"
```

4. Click **Verify DNS** in NimbusAdmin — the system checks for the SPF and DKIM records
5. Once verified, set the custom domain as active
6. Send a test email to confirm deliverability

### DNS Propagation
DNS changes may take up to 48 hours to propagate. Common timeline:
- CloudFlare: 5 minutes
- AWS Route53: 5-15 minutes
- GoDaddy: 1-24 hours
- On-premise DNS: Depends on TTL settings

## Common Email Deliverability Issues

### Notifications Going to Spam
**Symptoms:** Users report NimbusCloud emails landing in spam/junk folder.

**Common Causes:**
- Custom sender domain configured but SPF/DKIM records missing or incorrect
- Recipient's email server has aggressive spam filtering
- Multiple SPF records on the domain (only one is allowed)
- DKIM key rotation pending — old key expired, new key not yet published

**Resolution Steps:**
1. Verify SPF record: Use an SPF checker tool to confirm `include:spf.nimbuscloud.io` is present
2. Verify DKIM: Use a DKIM validator to test the `nimbuscloud._domainkey` record
3. Check for multiple SPF records — merge them into one: `v=spf1 include:spf.nimbuscloud.io include:_spf.google.com ~all`
4. Ask recipients' IT teams to allowlist `notifications@nimbuscloud.io` or your custom sender address
5. Check DMARC reports for alignment failures

### Notification Emails Not Sent
**Symptoms:** No notification emails received at all — not in inbox or spam.

**Common Causes:**
- User has disabled email notifications: Profile > Notifications > Email
- NimbusAdmin email sending is disabled (admin policy)
- Email suppression list — user's email bounced previously and was auto-suppressed
- Custom domain DNS verification expired after a DNS change

**Resolution Steps:**
1. Check user notification preferences: NimbusAdmin > Users > [user] > Notification Settings
2. Check admin policy: NimbusAdmin > Settings > Email > Sending Status — should show "Active"
3. Check suppression list: NimbusAdmin > Settings > Email > Suppression List — remove the email if it was soft-bounced
4. If using custom domain, re-verify DNS: NimbusAdmin > Settings > Email > Verify DNS

### Bounce Rate Too High
**Symptoms:** NimbusAdmin shows email bounce rate above 5% — custom domain at risk of being disabled.

**Common Causes:**
- Stale user accounts with invalid email addresses
- Distribution lists or aliases that don't resolve correctly
- Typos in email addresses during bulk user import

**Resolution Steps:**
1. Review bounce list: NimbusAdmin > Settings > Email > Bounce Report
2. Deactivate or correct user accounts with invalid emails
3. Re-verify email addresses for bounced recipients
4. Clean up user accounts synced from stale directory sources

## Notification Management

### Per-Product Notification Controls
| Product | Available Notifications | Default |
|---------|----------------------|---------|
| NimbusHub | Mentions, DMs, channel updates | On (mentions + DMs), Off (channel) |
| NimbusDocs | Shares, comments, edit suggestions | On (all) |
| NimbusBoard | Task assignments, due dates, status changes | On (assignments + due dates) |
| NimbusConnect | Meeting invites, recordings ready | On (all) |
| NimbusID | Security alerts, login from new device | On (all) — cannot disable |

### Admin Notification Policies
Admins can enforce notification baselines: NimbusAdmin > Settings > Notifications > Policies
- **Require security notifications** — cannot be disabled by users
- **Set quiet hours** — no notifications between specified hours (except security alerts)
- **Batch digest** — combine multiple notifications into a single hourly or daily digest

## Best Practices

1. **Configure SPF, DKIM, and DMARC** for custom sender domains before activating
2. **Monitor bounce rates** monthly — keep below 2% to maintain sender reputation
3. **Clean the suppression list** quarterly — remove soft bounces that may have been temporary
4. **Use notification digests** for high-volume teams to reduce email fatigue
5. **Keep security notifications mandatory** — do not allow users to disable login alerts

## Related Articles
- KB-015: Custom Notification Sender Address Configuration
- KB-004: NimbusAdmin Tenant and User Provisioning
- KB-008: MFA Setup and Troubleshooting
