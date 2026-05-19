# Community Forum: VPN 504 Errors — Community Workarounds

**Article Number**: FORUM-001  
**Category**: Network & Connectivity  
**Product**: ZavaCloud Platform

---

## Thread: VPN connection keeps timing out when accessing ZavaCloud — 504 errors

**Posted by:** @MarcusR_IT | January 20, 2026

We're onboarding 12 new hires this week and they're all getting 504 Gateway Timeout errors when trying to access ZavaCloud while on our corporate VPN (GlobalProtect). It works fine from the office without VPN. Is anyone else seeing this? We need to get these folks set up ASAP — MFA enrollment is stuck because the pages won't load.

---

### Reply 1

**Posted by:** @NetAdmin_Jake | January 20, 2026

We had the exact same issue when we rolled out ZavaCloud last quarter. The problem was our VPN routing — we had a full-tunnel config that was sending ALL traffic through the VPN, including ZavaCloud SaaS endpoints.

Fix: Update your split-tunnel policy to exclude `*.ZavaCloud.io`. ZavaCloud's SaaS endpoints don't need VPN — they're public internet services. Only `*.internal.ZavaCloud.io` (ZavaAdmin private endpoints) should go through the tunnel.

After that change, our 504s dropped to zero.

---

### Reply 2

**Posted by:** @SysAdmin_Priya | January 20, 2026

Also check your MTU settings! The default 1500 MTU causes fragmentation in VPN tunnels. Set it to 1400:

**Windows:**
```
netsh interface ipv4 set subinterface "VPN Adapter" mtu=1400
```

**macOS:**
```
sudo ifconfig utun0 mtu 1400
```

This fixed intermittent timeouts for us even with split-tunnel enabled.

---

### Reply 3

**Posted by:** @MarcusR_IT | January 22, 2026

Update: Split-tunnel change + MTU fix resolved the issue for 10 of 12 users. The remaining 2 are on macOS Sonoma and their DNS isn't resolving correctly after VPN reconnection.

Anyone dealt with macOS DNS weirdness after VPN connects?

---

### Reply 4

**Posted by:** @MacAdmin_Chris | January 22, 2026

@MarcusR_IT Classic macOS issue. The DNS resolver doesn't always pick up new DNS servers pushed by the VPN client. Run this after connecting:

```
sudo killall -HUP mDNSResponder
```

Or better yet, create a script that runs automatically when the VPN connects. You can hook into the GlobalProtect post-connect script to do this.

We also added `internal.ZavaCloud.io` to the DNS suffix search list in our network profile to fix resolution for ZavaAdmin endpoints.

---

### Reply 5

**Posted by:** @MarcusR_IT | January 23, 2026

That did it — all 12 new hires are now set up. Here's the complete fix for anyone finding this later:

1. **Split-tunnel VPN** — exclude `*.ZavaCloud.io` SaaS endpoints
2. **MTU 1400** on VPN adapter
3. **macOS DNS fix** — restart mDNSResponder after VPN connection
4. **DNS suffix** — add `internal.ZavaCloud.io` for admin access

Opened a support case (CASE-001) that confirmed the same steps. KB-001 has the full VPN troubleshooting guide.

---

### Reply 6

**Posted by:** @NewAdmin_Sam | January 25, 2026

Saving this thread — we're about to deploy ZavaCloud next month and I know we'll hit this. Quick question: does ZavaConnect video traffic also need to be excluded from the VPN tunnel? Our security team wants to keep as much in the tunnel as possible.

---

### Reply 7

**Posted by:** @NetAdmin_Jake | January 25, 2026

@NewAdmin_Sam Absolutely exclude ZavaConnect from the VPN tunnel. Video conferencing latency is brutal through a full-tunnel VPN — you'll get choppy audio and pixelated video. ZavaConnect uses WebRTC with UDP and adding VPN overhead kills the experience. Check KB-002 for the ZavaConnect firewall/network requirements.
