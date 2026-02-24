# Community Forum: Notification Emails Marked as Spam — SPF/DKIM Help

**Article Number**: FORUM-010  
**Category**: Email & Notifications  
**Product**: NimbusCloud Platform

---

## Thread: NimbusCloud emails going straight to spam after we set up a custom sender domain

**Posted by:** @DianeF_LCCU | February 8, 2026

We just configured a custom sender domain (`notifications@lakeshoreccu.org`) in NimbusAdmin and now ALL NimbusCloud notifications are going to everyone's spam folder. Any idea what we messed up? We were trying to make the emails look more professional by coming from our own domain.

---

### Reply 1

**Posted by:** @EmailAdmin_Pat | February 8, 2026

Classic custom domain setup issue. Let me guess — you set up the SPF record but forgot the DKIM record?

When you configure a custom sender domain, NimbusCloud signs emails with DKIM. But if the DKIM DNS record isn't published for your domain, the signature validation fails. And if your DMARC policy is set to `p=quarantine` or `p=reject`, failing DKIM = spam folder.

Check:
1. **SPF**: `v=spf1 include:spf.nimbuscloud.io ~all` — is this in your DNS?
2. **DKIM**: `nimbuscloud._domainkey.yourdomain.com TXT "v=DKIM1; k=rsa; p=<key>"` — did you add this?
3. **DMARC**: What's your DMARC policy? If `p=quarantine`, missing DKIM will absolutely land in spam.

---

### Reply 2

**Posted by:** @DianeF_LCCU | February 8, 2026

@EmailAdmin_Pat You called it. We had SPF but not DKIM. The DKIM key was shown during setup in NimbusAdmin but I thought it was just informational — didn't realize we had to add it to our DNS.

Adding it now... do you know how long Cloudflare DNS propagation takes?

---

### Reply 3

**Posted by:** @DNS_Expert_Marco | February 8, 2026

Cloudflare is usually 5 minutes or less. After adding the DKIM record:

1. Wait 5-10 minutes
2. Go to NimbusAdmin > Settings > Email > Custom Sender Domain > click **Verify DNS**
3. If all green: SPF ✅, DKIM ✅, DMARC ✅ — you're good
4. Send a test email to verify it lands in inbox

If you want to double-check, use MXToolbox's DKIM lookup:
```
https://mxtoolbox.com/dkim.aspx
Selector: nimbuscloud
Domain: lakeshoreccu.org
```

---

### Reply 4

**Posted by:** @DianeF_LCCU | February 9, 2026

DKIM record added, verified in NimbusAdmin, test email landed in inbox! Gmail even stopped showing the "via nimbuscloud.io" badge. 

For posterity, here's the complete DNS setup for NimbusCloud custom sender domain:

**SPF** (add to existing record):
```
v=spf1 include:spf.nimbuscloud.io [your other includes] ~all
```

**DKIM** (new TXT record):
```
nimbuscloud._domainkey.yourdomain.com  TXT  "v=DKIM1; k=rsa; p=<key from NimbusAdmin>"
```

**DMARC** (if not already set):
```
_dmarc.yourdomain.com  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@yourdomain.com"
```

---

### Reply 5

**Posted by:** @EmailAdmin_Pat | February 10, 2026

One more tip: don't forget about the **SPF 10-lookup limit**. If your SPF record already has a lot of `include:` entries (e.g., Google Workspace, SendGrid, Mailchimp), adding NimbusCloud might push you over the 10 DNS lookups allowed in SPF. Use an SPF flattening tool if needed.

KB-010 has the full email deliverability guide with all the DNS details.

---

### Reply 6

**Posted by:** @NewIT_Admin_Jo | February 12, 2026

Thank you for this thread — I'm setting up our custom sender domain next week and this saved me from making the same mistake. Bookmarking this and KB-010!
