# Email Deliverability and Notification Configuration

**Article Number:** KB-010  
**Product:** ZavaCloud Platform  
**Category:** Email & Notifications  
**Last Updated:** February 2026

## Overview

ZavaCloud sends notifications via email for events across all products — chat mentions in ZavaHub, document shares in ZavaDocs, meeting invitations in ZavaConnect, task assignments in ZavaBoard, and security alerts from ZavaID. This article covers email deliverability configuration (SPF, DKIM, DMARC), custom sender domains, and notification management.

## Default Email Configuration

By default, ZavaCloud sends all notifications from:
```
From: notifications@ZavaCloud.io
Reply-To: no-reply@ZavaCloud.io
```

These emails pass SPF, DKIM, and DMARC checks automatically. No configuration is needed for the default sender.

## Custom Sender Domain

Organizations can send ZavaCloud notifications from their own domain (e.g., `notifications@yourcompany.com`):

### Setup Steps
1. Navigate to ZavaAdmin > Settings > Email > Custom Sender Domain
2. Enter your custom "From" domain (e.g., `yourcompany.com`)
3. ZavaCloud generates DNS records you must add:

**SPF Record:**
```
v=spf1 include:spf.ZavaCloud.io ~all
```
Add this to your existing SPF record, or create one if none exists.

**DKIM Record:**
```
ZavaCloud._domainkey.yourcompany.com  TXT  "v=DKIM1; k=rsa; p=<generated-public-key>"
```

**DMARC Record (recommended):**
```
_dmarc.yourcompany.com  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@yourcompany.com"
```

4. Click **Verify DNS** in ZavaAdmin — the system checks for the SPF and DKIM records
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
**Symptoms:** Users report ZavaCloud emails landing in spam/junk folder.

**Common Causes:**
- Custom sender domain configured but SPF/DKIM records missing or incorrect
- Recipient's email server has aggressive spam filtering
- Multiple SPF records on the domain (only one is allowed)
- DKIM key rotation pending — old key expired, new key not yet published

**Resolution Steps:**
1. Verify SPF record: Use an SPF checker tool to confirm `include:spf.ZavaCloud.io` is present
2. Verify DKIM: Use a DKIM validator to test the `ZavaCloud._domainkey` record
3. Check for multiple SPF records — merge them into one: `v=spf1 include:spf.ZavaCloud.io include:_spf.google.com ~all`
4. Ask recipients' IT teams to allowlist `notifications@ZavaCloud.io` or your custom sender address
5. Check DMARC reports for alignment failures

### Notification Emails Not Sent
**Symptoms:** No notification emails received at all — not in inbox or spam.

**Common Causes:**
- User has disabled email notifications: Profile > Notifications > Email
- ZavaAdmin email sending is disabled (admin policy)
- Email suppression list — user's email bounced previously and was auto-suppressed
- Custom domain DNS verification expired after a DNS change

**Resolution Steps:**
1. Check user notification preferences: ZavaAdmin > Users > [user] > Notification Settings
2. Check admin policy: ZavaAdmin > Settings > Email > Sending Status — should show "Active"
3. Check suppression list: ZavaAdmin > Settings > Email > Suppression List — remove the email if it was soft-bounced
4. If using custom domain, re-verify DNS: ZavaAdmin > Settings > Email > Verify DNS

### Bounce Rate Too High
**Symptoms:** ZavaAdmin shows email bounce rate above 5% — custom domain at risk of being disabled.

**Common Causes:**
- Stale user accounts with invalid email addresses
- Distribution lists or aliases that don't resolve correctly
- Typos in email addresses during bulk user import

**Resolution Steps:**
1. Review bounce list: ZavaAdmin > Settings > Email > Bounce Report
2. Deactivate or correct user accounts with invalid emails
3. Re-verify email addresses for bounced recipients
4. Clean up user accounts synced from stale directory sources

## Notification Management

### Per-Product Notification Controls
| Product | Available Notifications | Default |
|---------|----------------------|---------|
| ZavaHub | Mentions, DMs, channel updates | On (mentions + DMs), Off (channel) |
| ZavaDocs | Shares, comments, edit suggestions | On (all) |
| ZavaBoard | Task assignments, due dates, status changes | On (assignments + due dates) |
| ZavaConnect | Meeting invites, recordings ready | On (all) |
| ZavaID | Security alerts, login from new device | On (all) — cannot disable |

### Admin Notification Policies
Admins can enforce notification baselines: ZavaAdmin > Settings > Notifications > Policies
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
- KB-004: ZavaAdmin Tenant and User Provisioning
- KB-008: MFA Setup and Troubleshooting
