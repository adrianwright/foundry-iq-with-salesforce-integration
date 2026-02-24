# Support Case: Email Notifications Going to Spam

**Case Number**: CASE-010  
**Status**: Resolved  
**Priority**: Medium  
**Product**: NimbusCloud Platform  
**Category**: Email & Notifications  
**Origin**: Web  
**Contact**: Diane Foster, IT Systems Admin, Lakeshore Community Credit Union  
**Account**: Lakeshore Community Credit Union  
**Created**: February 8, 2026  
**Last Updated**: February 13, 2026

---

## Subject
NimbusCloud notification emails consistently going to spam for all users — custom sender domain configured

## Description
Diane Foster reported that NimbusCloud notification emails (task assignments from NimbusBoard, document shares from NimbusDocs, meeting invites from NimbusConnect) are all being delivered to users' spam/junk folders. Lakeshore recently configured a custom sender domain (`notifications@lakeshoreccu.org`) but notifications started going to spam shortly after activation.

## Investigation Notes

**2026-02-08 — Initial Triage (Support Engineer: Ben Kowalski)**
- Confirmed custom sender domain `lakeshoreccu.org` was activated on February 5
- Ran email header analysis on a spam-filtered notification:
  - SPF: Pass ✅ (`include:spf.nimbuscloud.io` present)
  - DKIM: **Fail** ❌ — DKIM signature `d=nimbuscloud.io` doesn't align with From address `notifications@lakeshoreccu.org`
  - DMARC: **Fail** ❌ — DMARC policy `p=quarantine` and neither SPF nor DKIM aligned
- Root cause: DKIM record for `lakeshoreccu.org` was not published. The NimbusCloud-generated DKIM key was provided during setup but Diane hadn't added it to their DNS yet

**2026-02-09 — DNS Records Updated**
- Diane added the DKIM record: `nimbuscloud._domainkey.lakeshoreccu.org TXT "v=DKIM1; k=rsa; p=<key>"`
- DNS propagation confirmed after 2 hours (hosted on Cloudflare)
- Re-verified in NimbusAdmin: SPF ✅, DKIM ✅, DMARC ✅ (all passing)

**2026-02-10 — Testing**
- Sent test notifications to 5 users across different email providers (Gmail, Outlook, Yahoo)
- All delivered to inbox — no spam filtering
- Gmail no longer showing "via nimbuscloud.io" badge

**2026-02-13 — Resolution Confirmed**
- Diane confirmed all NimbusCloud notifications are landing in inboxes for the past 3 days
- Bounce rate at 0.3% (healthy)
- Advised Diane to monitor the delivery dashboard monthly (NimbusAdmin > Settings > Email > Delivery Dashboard)

## Resolution
DKIM DNS record was missing for the custom sender domain, causing DKIM and DMARC alignment failures. Adding the DKIM record resolved spam filtering. KB-010 provides the complete email deliverability setup guide.

## Related Articles
- KB-010: Email Deliverability and Notification Configuration
- KB-015: Custom Notification Sender Address Configuration
- FORUM-010: Notification Emails Marked as Spam — SPF/DKIM Help
