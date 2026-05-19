# MFA Setup and Troubleshooting

**Article Number:** KB-008  
**Product:** ZavaID  
**Category:** Authentication & Security  
**Last Updated:** February 2026

## Overview

ZavaID supports multi-factor authentication (MFA) to protect user accounts across all ZavaCloud products. This article covers MFA setup, supported methods, troubleshooting common failures, and recovery procedures.

## Supported MFA Methods

| Method | Security Level | User Experience | Recommended |
|--------|---------------|-----------------|-------------|
| Authenticator app (TOTP) | High | Good — 6-digit code from app | Yes — primary |
| Push notification (ZavaID app) | High | Best — tap to approve | Yes — primary |
| Hardware security key (FIDO2/WebAuthn) | Highest | Good — tap USB key | Yes — for admins |
| SMS code | Medium | Fair — code via text message | Backup only |
| Email code | Medium | Fair — code via email | Backup only |

## MFA Setup for End Users

### First-Time Setup
1. Log in to ZavaCloud at `https://app.ZavaCloud.io`
2. If MFA is enforced by admin policy, you'll be prompted to set up MFA on next login
3. Choose your preferred method:
   - **Authenticator app**: Scan the QR code with Google Authenticator, Microsoft Authenticator, or Authy
   - **Push notification**: Download the ZavaID app from App Store / Google Play, scan the QR code to link
   - **Hardware key**: Insert USB security key, touch when prompted
4. Enter the verification code to confirm setup
5. **Save your recovery codes** — you'll receive 10 one-time-use recovery codes. Store them in a secure location.

### Adding Backup Methods
Users should configure at least two MFA methods:
1. Go to `https://app.ZavaCloud.io/settings/security`
2. Under "Multi-Factor Authentication," click **Add Method**
3. Follow the setup flow for the additional method
4. Both methods will be available at login — user can choose which to use

## Admin MFA Policy Configuration

### Enabling MFA for the Organization
1. Navigate to ZavaAdmin > Settings > Security > MFA Policy
2. Choose enforcement level:
   - **Optional**: Users can choose to enable MFA
   - **Required for admins**: Only admin accounts require MFA
   - **Required for all**: All users must set up MFA (recommended)
3. Set grace period for enforcement (default: 14 days after policy activation)
4. Choose allowed MFA methods (disable SMS if not desired)
5. Save and communicate the change to users

### Conditional MFA Policies
| Condition | Example |
|-----------|---------|
| User role | Require hardware key for admins, allow TOTP for standard users |
| Network location | Skip MFA on corporate network, require MFA externally |
| Risk level | Require MFA for logins from new devices or locations |
| Application | Require MFA for ZavaAdmin access, optional for ZavaHub |

Configure at: ZavaAdmin > Settings > Security > Conditional Access

## Common MFA Issues

### Push Notifications Not Arriving
**Symptoms:** User selects "Send push notification" at login, but the ZavaID app never receives it.

**Common Causes:**
- Phone's notification permissions for ZavaID app are disabled
- Phone is in Do Not Disturb mode
- ZavaID app needs to be updated (minimum: v3.1)
- Phone changed (new device) and ZavaID app wasn't re-linked
- iOS background app refresh is disabled for ZavaID

**Resolution Steps:**
1. Verify notification permissions: Phone Settings > ZavaID > Notifications > Enable
2. Check Do Not Disturb is off (or ZavaID is added to exceptions)
3. Update the ZavaID app to the latest version
4. If using a new phone, re-link: ZavaCloud Settings > Security > MFA > Remove old device > Add new device
5. On iOS, enable Background App Refresh for ZavaID
6. As a workaround, switch to TOTP code entry (same authenticator app, just enter the 6-digit code manually)

### TOTP Code "Invalid" Error
**Symptoms:** User enters the 6-digit code from their authenticator app, but it's rejected as invalid.

**Common Causes:**
- Phone clock is out of sync (TOTP is time-sensitive, ±30 seconds)
- User is entering the code from the wrong account in their authenticator app
- TOTP secret was reset but authenticator app wasn't updated

**Resolution Steps:**
1. Sync the phone's clock: Settings > Date & Time > Automatic
2. Verify the correct ZavaCloud account is selected in the authenticator app
3. Try the next code (wait for the timer to cycle)
4. If persistent, re-enroll: delete the ZavaCloud entry from the authenticator app, then re-scan the QR code from ZavaCloud Settings > Security > MFA > Reset TOTP

### Account Locked After Failed MFA Attempts
**Symptoms:** User is locked out after 5 failed MFA attempts.

**Resolution Steps:**
1. Wait 15 minutes — the lockout expires automatically
2. If urgent, an admin can unlock: ZavaAdmin > Users > [user] > Security > Unlock Account
3. If the user has lost their MFA device, use a recovery code (see below)
4. If recovery codes are also lost, admin can reset MFA: ZavaAdmin > Users > [user] > Security > Reset MFA

### MFA Recovery
If a user loses access to their MFA device:
1. **Use a recovery code** — enter one of the 10 one-time codes saved during setup
2. **Admin reset** — ZavaAdmin > Users > [user] > Security > Reset MFA (requires admin verification)
3. **Self-service recovery** — If SMS or email backup method is configured, use the "Try another method" link at login

## Best Practices

1. **Require MFA for all users** — not just admins
2. **Mandate saving recovery codes** by requiring acknowledgment during setup
3. **Use authenticator app or push notifications** as primary — avoid SMS as sole method
4. **Require hardware keys for admin accounts** for highest security
5. **Monitor MFA failure rates** in ZavaAdmin > Reports > Authentication to detect account compromise attempts

## Related Articles
- KB-003: SSO and SAML Configuration Guide
- KB-006: OAuth 2.0 and OIDC Integration Troubleshooting
- KB-014: Username and UPN Change Procedure
- KB-001: VPN Connectivity Troubleshooting
