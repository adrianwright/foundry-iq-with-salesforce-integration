# VPN Connectivity Troubleshooting

**Article Number:** KB-001  
**Product:** ZavaCloud Platform  
**Category:** Network & Connectivity  
**Last Updated:** February 2026

## Overview

This article covers common VPN connectivity issues when accessing ZavaCloud services remotely. ZavaCloud supports both split-tunnel and full-tunnel VPN configurations. Understanding the connection architecture helps diagnose timeout, DNS resolution, and client compatibility problems.

## VPN Architecture for ZavaCloud Access

### Supported Configurations
ZavaCloud services are accessible through the following network paths:

1. **Direct internet access** — No VPN required for ZavaHub, ZavaDocs, and ZavaConnect (SaaS endpoints)
2. **Split-tunnel VPN** — Recommended. Routes only internal traffic (ZavaAdmin, ZavaAPI private endpoints) through the corporate VPN while SaaS traffic goes direct
3. **Full-tunnel VPN** — All traffic routes through corporate network. May introduce latency for ZavaConnect video calls

### DNS Resolution Requirements
- `*.ZavaCloud.io` — Primary SaaS domain, must resolve via public DNS or internal forwarders
- `*.internal.ZavaCloud.io` — Admin and API private endpoints, require corporate DNS
- `api.ZavaCloud.io` — ZavaAPI public endpoint, must be reachable from VPN clients

## Common VPN Issues

### Issue: Connection Timeout (504 Gateway Timeout)
**Symptoms:** ZavaCloud web apps fail to load or API calls time out after 30-60 seconds while connected to VPN.

**Common Causes:**
- VPN client MTU size mismatch (default 1500 vs required 1400 for tunneled traffic)
- DNS resolution falling back to public DNS for internal-only endpoints
- VPN concentrator at capacity during peak hours (9-10 AM, 1-2 PM)

**Resolution Steps:**
1. Test connectivity without VPN to confirm the issue is VPN-specific
2. Check VPN client version — minimum supported: GlobalProtect 6.1, Cisco AnyConnect 4.10, or WireGuard 1.0
3. Reduce MTU to 1400: `netsh interface ipv4 set subinterface "VPN Adapter" mtu=1400`
4. Flush DNS cache: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (macOS)
5. If persistent, contact IT to check VPN concentrator load and split-tunnel route tables

### Issue: DNS Resolution Failures
**Symptoms:** `*.internal.ZavaCloud.io` addresses do not resolve. ZavaAdmin console returns "Server not found."

**Common Causes:**
- VPN client not pushing corporate DNS servers to the local resolver
- DNS suffix search list missing `internal.ZavaCloud.io`
- macOS DNS configuration not updated after VPN reconnection

**Resolution Steps:**
1. Verify DNS servers while connected: `nslookup admin.internal.ZavaCloud.io`
2. Check that corporate DNS (10.0.1.10, 10.0.1.11) appears in resolver config
3. On macOS, restart mDNSResponder: `sudo killall -HUP mDNSResponder`
4. Add DNS suffix manually if needed: `internal.ZavaCloud.io` in network adapter settings
5. Reconnect VPN if DNS servers are not being pushed correctly

### Issue: Intermittent Disconnections
**Symptoms:** VPN drops every 15-30 minutes, requiring manual reconnection.

**Common Causes:**
- Aggressive power management on Wi-Fi adapter putting the NIC to sleep
- VPN idle timeout set too low (default 30 minutes on some configurations)
- Network switching between Wi-Fi and Ethernet triggering VPN teardown

**Resolution Steps:**
1. Disable Wi-Fi power management: Device Manager > Wi-Fi Adapter > Power Management > uncheck "Allow the computer to turn off this device"
2. Set VPN keep-alive interval to 20 seconds in client settings
3. Disable network roaming/auto-switch if using a docking station with Ethernet
4. Contact IT to check if DPD (Dead Peer Detection) interval on the concentrator is too aggressive

## Split-Tunnel vs Full-Tunnel Guidance

| Feature | Split-Tunnel (Recommended) | Full-Tunnel |
|---------|---------------------------|-------------|
| ZavaConnect video quality | Best (direct path) | May degrade (added latency) |
| ZavaAdmin access | Routed via VPN | Routed via VPN |
| Internet browsing speed | Unaffected | Reduced (all traffic through VPN) |
| Security posture | Moderate | Higher (all traffic inspected) |
| Bandwidth on VPN concentrator | Lower | Higher |

## Best Practices

1. **Use split-tunnel VPN** unless security policy requires full-tunnel
2. **Keep VPN client updated** to the latest supported version
3. **Test connectivity** after VPN connection before joining ZavaConnect meetings
4. **Report chronic issues** to IT with VPN client logs (Help > Export Logs in most clients)
5. **Use the ZavaCloud status page** (status.ZavaCloud.io) to rule out service-side outages

## Related Articles
- KB-002: ZavaConnect Video Call Quality Troubleshooting
- KB-003: SSO and SAML Configuration Guide
- KB-008: MFA Setup and Troubleshooting
