# Support Case: VPN Timeout During Remote Onboarding

**Case Number**: CASE-001  
**Status**: Resolved  
**Priority**: High  
**Product**: NimbusCloud Platform  
**Category**: Network & Connectivity  
**Origin**: Web  
**Contact**: Marcus Rivera, IT Manager, Pinnacle Dynamics  
**Account**: Pinnacle Dynamics  
**Created**: January 20, 2026  
**Last Updated**: January 27, 2026

---

## Subject
VPN timeouts preventing new hires from completing NimbusCloud onboarding setup

## Description
Marcus Rivera reported that 12 new hires joining this week are unable to complete their NimbusCloud onboarding. When connected to the corporate VPN (GlobalProtect), attempts to access NimbusAdmin and complete MFA enrollment consistently fail with 504 Gateway Timeout errors after approximately 60 seconds. The issue only affects users on the VPN — those on the corporate office network have no problems.

## Investigation Notes

**2026-01-20 — Initial Triage (Support Engineer: Aisha Patel)**
- Confirmed 504 timeouts in access logs for 8 of the 12 new hire accounts
- VPN split-tunnel configuration reviewed — `*.nimbuscloud.io` is routed through the VPN tunnel instead of going direct
- MTU on VPN adapter is set to default 1500 — likely causing fragmentation on the tunnel
- Advised IT team to update split-tunnel rules to exclude `*.nimbuscloud.io` SaaS endpoints

**2026-01-22 — Configuration Change Applied**
- IT team updated GlobalProtect split-tunnel policy to exclude NimbusCloud SaaS domains
- MTU on VPN adapter reduced to 1400 per KB-001 guidance
- 10 of 12 new hires completed onboarding successfully after the change

**2026-01-24 — Remaining Issues**
- 2 new hires still experiencing timeouts — both are on macOS Sonoma
- macOS DNS resolver not updating after VPN reconnection (known macOS behavior)
- Applied workaround: restart mDNSResponder after VPN connection (`sudo killall -HUP mDNSResponder`)
- Both users completed onboarding after DNS fix

**2026-01-27 — Resolution Confirmed**
- All 12 new hires have completed NimbusCloud onboarding and MFA enrollment
- IT team documented the split-tunnel and macOS DNS fixes in their internal runbook

## Resolution
Split-tunnel VPN policy updated to route NimbusCloud SaaS traffic directly (not through VPN). MTU reduced to 1400. macOS DNS resolver workaround applied for remaining users. KB-001 referenced for ongoing VPN troubleshooting guidance.

## Related Articles
- KB-001: VPN Connectivity Troubleshooting
- KB-008: MFA Setup and Troubleshooting
- FORUM-001: VPN 504 Errors — Community Workarounds
