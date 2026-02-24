# Community Forum: MFA Failures After iOS/Android Update

**Article Number**: FORUM-008  
**Category**: Authentication & Security  
**Product**: NimbusID

---

## Thread: MFA push notifications stopped working after iOS 19.3 update — 40% of our users locked out

**Posted by:** @RobertT_CISO | February 10, 2026

Major issue this morning. About 200 of our 500 users can't log in to NimbusCloud because MFA push notifications aren't arriving on their phones. This started over the weekend after iOS 19.3 and the Android 15 February security patch rolled out via MDM. Users who set up TOTP as a backup can still get in, but the rest are stuck. Anyone else seeing this?

---

### Reply 1

**Posted by:** @MobileAdmin_Eric | February 10, 2026

Yes, same here. About 30% of our users are affected. Two separate issues:

**iOS 19.3:** Apple changed how notification permissions work. Apps need to re-request notification permission after the update. If users have NimbusID app v3.0.x, it doesn't handle this properly — it just silently fails to receive push notifications.

**Fix:** Update NimbusID app to v3.2 (released February 11). It prompts users to re-grant notification permissions.

**Android 15 (Feb patch):** The new battery optimization defaults put NimbusID into "Restricted" mode, which prevents background push delivery.

**Fix:** Settings > Apps > NimbusID > Battery > set to "Unrestricted"

---

### Reply 2

**Posted by:** @RobertT_CISO | February 10, 2026

How are people handling the 200 locked-out users RIGHT NOW? We can't wait for app updates.

---

### Reply 3

**Posted by:** @IT_Admin_Derek | February 10, 2026

For immediate triage:

1. **Users with TOTP backup**: Tell them to enter the 6-digit code from their authenticator app instead of waiting for push. The "Try another method" link on the login screen switches to TOTP.

2. **Users with NO backup MFA method**: Admins can generate a temporary access code in NimbusAdmin > Users > [user] > Security > Generate Temporary Code. Valid for 24 hours, single use.

3. **Enforce backup MFA going forward**: NimbusAdmin > Settings > Security > MFA Policy > require at least 2 methods. This prevents mass lockouts from a single MFA channel failing.

We had to issue temp codes for about 85 users. Took a couple hours but everyone got in.

---

### Reply 4

**Posted by:** @SecurityEngineer_Nina | February 11, 2026

NimbusID v3.2 just dropped on both App Store and Google Play. We pushed it via MDM and the push notification issues are resolved. Here's our post-incident checklist:

- [x] Update NimbusID app to v3.2 (iOS and Android)
- [x] Whitelist NimbusID from Android battery optimization in MDM profile
- [x] Require all users to configure at least 2 MFA methods
- [x] Add NimbusID to app update priority list (auto-update ASAP, don't defer)

---

### Reply 5

**Posted by:** @RobertT_CISO | February 17, 2026

All resolved on our end. MFA push failure rate back to normal (2%). Key takeaways:

1. **Always require multiple MFA methods** — single point of failure is bad
2. **Add MFA apps to your MDM app update priority list** — can't afford stale versions
3. **Whitelist critical apps from battery optimization** on Android from day one
4. **Test MFA after OS updates** — add it to your patch testing checklist

CASE-008 has the full investigation if NimbusCloud support needs to look at your logs. KB-008 has the ongoing MFA troubleshooting guide.

---

### Reply 6

**Posted by:** @NewAdmin_Sam | February 18, 2026

We haven't deployed MFA yet (starting next month). This thread is a goldmine of "what NOT to do." Setting up dual-method MFA requirements from day one, whitelisting the NimbusID app in MDM, and scheduling MFA testing after every OS update cycle. Thank you all!
