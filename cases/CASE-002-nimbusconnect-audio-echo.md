# Support Case: NimbusConnect Audio Echo on Bluetooth Headsets

**Case Number**: CASE-002  
**Status**: Resolved  
**Priority**: Medium  
**Product**: NimbusConnect  
**Category**: Audio & Video  
**Origin**: Phone  
**Contact**: Sarah Whitfield, Office Manager, Greenleaf Consulting  
**Account**: Greenleaf Consulting  
**Created**: January 25, 2026  
**Last Updated**: February 2, 2026

---

## Subject
Audio echo reported by meeting participants when host uses Bluetooth headset with NimbusConnect

## Description
Sarah Whitfield reported that approximately 30 employees at Greenleaf Consulting experience audio echo during NimbusConnect meetings when using Bluetooth headsets. Other participants hear their own voice echoed back with a ~500ms delay. The issue is worst with Apple AirPods and Jabra Evolve2 headsets. Wired headsets do not exhibit the problem.

## Investigation Notes

**2026-01-25 — Initial Triage (Support Engineer: Jordan Kim)**
- Confirmed echo reports from 4 separate meetings logged this week
- All affected users are on Windows 11 with Bluetooth headsets
- NimbusConnect Desktop client v8.4.2 — current version
- Checked Bluetooth audio profile: affected users have headsets defaulting to A2DP (stereo) profile instead of HFP (Hands-Free Profile)
- A2DP provides high-quality audio playback but disables the headset's hardware echo cancellation
- When in A2DP mode, the laptop's built-in microphone is used instead of the headset mic, creating a speaker-to-mic feedback loop

**2026-01-28 — Workaround Distributed**
- Provided instructions to switch Bluetooth headsets to HFP mode:
  - Windows: Settings > System > Sound > Input > select headset microphone (not laptop mic)
  - NimbusConnect: Settings > Audio > Input Device > select "{Headset Name} Hands-Free"
- Alternative: Enable NimbusConnect's built-in echo cancellation: Settings > Audio > Advanced > Enable Acoustic Echo Cancellation
- Tested with 5 users — echo eliminated in all cases

**2026-02-02 — Resolution Confirmed**
- IT team pushed a group policy to default audio input to headset microphone when Bluetooth is connected
- Sarah confirmed echo issues have stopped across the organization
- Suggested NimbusConnect feature request: auto-detect A2DP vs HFP and warn users

## Resolution
Users' Bluetooth headsets were defaulting to A2DP profile, causing the laptop mic to be used instead of the headset mic. Fixed by switching to HFP profile in audio settings. NimbusConnect's built-in echo cancellation enabled as an additional safeguard. KB-002 referenced for ongoing audio troubleshooting.

## Related Articles
- KB-002: NimbusConnect Video Call Quality Troubleshooting
- FORUM-002: NimbusConnect Audio Dropping Mid-Meeting
