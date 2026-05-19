# Support Case: MFA Push Notifications Failing After OS Update

**Case Number**: CASE-008  
**Status**: Resolved  
**Priority**: High  
**Product**: ZavaID  
**Category**: Authentication & Security  
**Origin**: Phone  
**Contact**: Robert Tanaka, CISO, Meridian Logistics  
**Account**: Meridian Logistics  
**Created**: February 10, 2026  
**Last Updated**: February 17, 2026

---

## Subject
40% of users unable to log in — MFA push notifications failing after iOS 19.3 and Android 15 updates

## Description
Robert Tanaka reported that approximately 200 of 500 users at Meridian Logistics cannot log in to ZavaCloud. MFA push notifications from the ZavaID app are not arriving on users' phones. The issue started after the weekend when iOS 19.3 and Android 15 (February security patch) were deployed via MDM. Users who configured TOTP as a backup MFA method can still log in.

## Investigation Notes

**2026-02-10 — Initial Triage (Support Engineer: Nadia Volkov)**
- Confirmed ZavaID push authentication failure rate spiked from 2% to 41% starting February 8
- iOS 19.3 changed notification permission handling — apps must re-request notification permissions after the update
- Android 15 February patch modified battery optimization defaults — ZavaID app is being aggressively backgrounded
- ZavaID app version 3.0.x (installed on many devices) does not handle the iOS 19.3 permission change gracefully — v3.1+ required

**2026-02-10 — Immediate Workaround**
- Communicated to all affected users: switch to TOTP code entry as temporary MFA method
- Users who don't have TOTP configured: admins can generate a temporary access code in ZavaAdmin > Users > [user] > Security > Generate Temporary Code (valid for 24 hours)
- IT team issued temporary codes for 85 users who had no backup MFA method

**2026-02-12 — Root Cause Fix**
- iOS users: ZavaID app update to v3.2 (released February 11) handles the iOS 19.3 notification permission change — prompts users to re-grant permissions
- Android users: Disable battery optimization for ZavaID app (Settings > Apps > ZavaID > Battery > Unrestricted)
- MDM team pushed ZavaID v3.2 to all iOS devices and battery optimization whitelist for Android

**2026-02-17 — Resolution Confirmed**
- MFA push authentication failure rate back to 2% (normal baseline)
- Robert confirmed all 200 affected users are now able to log in normally
- Meridian IT added ZavaID to their app update priority list and battery optimization whitelist in MDM policy

## Resolution
iOS 19.3 changed notification permissions and ZavaID app v3.0.x didn't handle the change. Android 15 February patch aggressively backgrounded the ZavaID app. Fixed by updating ZavaID to v3.2 and whitelisting it from battery optimization on Android. KB-008 documents MFA troubleshooting steps.

## Related Articles
- KB-008: MFA Setup and Troubleshooting
- KB-003: SSO and SAML Configuration Guide
- FORUM-008: MFA Failures After iOS/Android Update
