# Custom Notification Sender Address Configuration

**Article Number:** KB-015  
**Product:** ZavaCloud Platform  
**Category:** Email & Notifications  
**Last Updated:** February 2026

## Overview

By default, ZavaCloud sends all notification emails from `notifications@ZavaCloud.io`. This article covers how to configure custom sender addresses per product, set up reply-to routing, and manage bounce handling for custom domains.

## Default Sender Addresses

| Product | Default From Address | Purpose |
|---------|---------------------|---------|
| ZavaHub | `hub-notifications@ZavaCloud.io` | Chat mentions, DM notifications, channel alerts |
| ZavaDocs | `docs-notifications@ZavaCloud.io` | Document shares, comments, version updates |
| ZavaBoard | `board-notifications@ZavaCloud.io` | Task assignments, due dates, status changes |
| ZavaConnect | `connect-notifications@ZavaCloud.io` | Meeting invitations, recordings, schedule changes |
| ZavaVault | `vault-notifications@ZavaCloud.io` | File shares, permission changes, storage alerts |
| ZavaID | `security@ZavaCloud.io` | Login alerts, MFA events, password resets |

## Custom Sender Address Configuration

### Per-Product Custom Addresses
Organizations can replace the default ZavaCloud sender addresses with their own domain:

1. **Prerequisites**: Complete the custom domain setup in KB-010 (SPF, DKIM, DMARC)
2. Navigate to ZavaAdmin > Settings > Email > Sender Addresses
3. For each product, enter the custom sender address:
   - Example: `hub-notifications@ZavaCloud.io` → `collaboration@yourcompany.com`
   - Example: `security@ZavaCloud.io` → `it-security@yourcompany.com`
4. Enter the custom **Reply-To** address (where user replies should go):
   - Example: `it-helpdesk@yourcompany.com` (routes replies to your support team)
5. Click **Save** for each product
6. Click **Send Test Email** to verify deliverability

### Display Name Configuration
Customize the "From" display name shown to recipients:
- Default: `ZavaCloud Notifications <notifications@ZavaCloud.io>`
- Custom: `Contoso IT Team <collaboration@contoso.com>`

Configure at: ZavaAdmin > Settings > Email > Sender Addresses > Display Name

## Reply-To Routing

### Use Cases
| Scenario | Reply-To Configuration |
|----------|----------------------|
| Route replies to IT helpdesk | `helpdesk@yourcompany.com` |
| Route replies to no-reply address | `no-reply@yourcompany.com` |
| Route replies to specific team | `support-team@yourcompany.com` |
| Route meeting replies to organizer | Enable "Dynamic Reply-To" for ZavaConnect (uses meeting organizer's email) |

### Dynamic Reply-To
For ZavaConnect meeting invitations, enable dynamic reply-to so that replies go to the meeting organizer instead of a generic mailbox:

1. ZavaAdmin > Settings > Email > ZavaConnect > Reply-To Settings
2. Select **Dynamic — Use organizer's email**
3. Save

For all other products, reply-to is static (configured at the admin level).

## Bounce Handling

### How Bounces Are Processed
1. Email sent from ZavaCloud (or custom domain)
2. If the recipient's server rejects the email, a **bounce notification** is returned
3. ZavaCloud categorizes the bounce:
   - **Hard bounce**: Invalid email address → address added to suppression list
   - **Soft bounce**: Temporary issue (mailbox full, server busy) → retry up to 3 times over 24 hours
4. Suppressed addresses do not receive further emails until manually removed

### Monitoring Bounce Rates
- ZavaAdmin > Settings > Email > Delivery Dashboard
- **Healthy**: < 2% bounce rate
- **Warning**: 2-5% bounce rate — review and clean distribution lists
- **Critical**: > 5% bounce rate — custom domain may be auto-disabled to protect sender reputation

## Common Issues

### Custom Sender Emails Rejected by Recipients
**Symptoms:** Emails sent from your custom domain are bounced or rejected by recipient mail servers.

**Resolution:**
1. Verify SPF record includes `include:spf.ZavaCloud.io` (see KB-010)
2. Verify DKIM alignment — the `d=` value in the DKIM signature must match the From domain
3. Check DMARC policy — if set to `p=reject`, ensure SPF and DKIM are both passing
4. Test with MXToolbox or similar tool: enter your custom domain and check SPF/DKIM/DMARC alignment

### "Via ZavaCloud.io" Showing in Gmail
**Symptoms:** Gmail recipients see "via ZavaCloud.io" next to the sender address.

**Cause:** DKIM signature `d=` domain doesn't match the From address domain.

**Resolution:**
1. Ensure DKIM is configured for your custom domain (not using ZavaCloud's default DKIM)
2. The DKIM `d=yourcompany.com` must match the From address `sender@yourcompany.com`
3. Re-verify the DKIM record in ZavaAdmin > Settings > Email > Custom Sender Domain > Verify DKIM

## Best Practices

1. **Use product-specific sender addresses** so users can filter and recognize notification types
2. **Set meaningful reply-to addresses** — don't let user replies go to an unmonitored mailbox
3. **Enable dynamic reply-to for ZavaConnect** so meeting replies reach the organizer
4. **Monitor delivery dashboard weekly** to catch deliverability issues early
5. **Keep SPF record concise** — too many includes can cause DNS lookup limit issues (max 10 lookups)

## Related Articles
- KB-010: Email Deliverability and Notification Configuration
- KB-004: ZavaAdmin Tenant and User Provisioning
- KB-012: System Maintenance and Incident Response Playbook
