# ZavaConnect Video Call Quality Troubleshooting

**Article Number:** KB-002  
**Product:** ZavaConnect  
**Category:** Audio & Video  
**Last Updated:** February 2026

## Overview

ZavaConnect is ZavaCloud's video conferencing and virtual meeting platform. This article covers common audio and video quality issues including echo, dropped audio, pixelated video, and connection failures. ZavaConnect uses WebRTC for peer-to-peer media and falls back to a relay server (TURN) when direct connections are blocked.

## System Requirements

### Minimum Requirements
- **Browser:** Chrome 110+, Edge 110+, Firefox 115+, Safari 17+
- **Bandwidth:** 1.5 Mbps up/down per participant for HD video
- **Ports:** UDP 3478 (STUN), UDP 10000-20000 (media), TCP 443 (fallback)
- **Audio:** Echo-canceling microphone recommended for shared rooms

### Network Requirements
| Mode | Minimum Bandwidth | Recommended |
|------|-------------------|-------------|
| Audio only | 100 Kbps | 200 Kbps |
| Video (SD) | 500 Kbps | 1 Mbps |
| Video (HD) | 1.5 Mbps | 3 Mbps |
| Screen share | 500 Kbps | 2 Mbps |

## Common Issues

### Audio Echo or Feedback
**Symptoms:** Other participants hear their own voice echoed back with a slight delay.

**Common Causes:**
- Built-in laptop speakers/microphone creating a feedback loop
- Multiple browser tabs or devices connected to the same meeting
- External speakers too close to the microphone
- Echo cancellation disabled in OS audio settings

**Resolution Steps:**
1. Use headphones or a headset — this eliminates 90% of echo issues
2. Check for duplicate meeting connections (multiple tabs or devices)
3. Mute when not speaking, especially in large meetings
4. Enable echo cancellation: ZavaConnect Settings > Audio > Enable Acoustic Echo Cancellation
5. On Bluetooth headsets, ensure the headset profile is set to "Headset" (HSP/HFP) not "Stereo" (A2DP) — A2DP disables the microphone on most devices

### Audio Dropping or Cutting Out
**Symptoms:** Audio intermittently drops for 1-3 seconds, sometimes repeatedly.

**Common Causes:**
- Network jitter exceeding 50ms causing packet loss
- Wi-Fi interference or weak signal strength
- VPN full-tunnel adding latency (see KB-001)
- Bluetooth headset range exceeded or interference from other 2.4 GHz devices

**Resolution Steps:**
1. Run ZavaConnect network test: Settings > Network > Run Diagnostics
2. Switch from Wi-Fi to Ethernet if available
3. Close bandwidth-heavy applications (streaming, large file uploads)
4. If on VPN, switch to split-tunnel or disconnect VPN for the meeting duration
5. For Bluetooth issues, move closer to the device and clear 2.4 GHz interference (microwave, other Bluetooth devices)

### Video Pixelated or Frozen
**Symptoms:** Video feed becomes blocky, pixelated, or freezes while audio continues.

**Common Causes:**
- Insufficient upload bandwidth (below 1.5 Mbps)
- CPU overloaded from screen sharing + video simultaneously
- Camera driver conflicts with other applications (Teams, Zoom running in background)

**Resolution Steps:**
1. Reduce video quality: ZavaConnect Settings > Video > Set to "Standard" (SD) instead of "HD"
2. Turn off video when screen sharing to free up bandwidth
3. Close other applications that may be using the camera
4. Check CPU usage — if above 80%, close unnecessary applications
5. Update camera drivers from the manufacturer's website

### Cannot Join Meeting (Connection Failed)
**Symptoms:** "Connection failed" or "Unable to establish media connection" error when joining.

**Common Causes:**
- Firewall blocking UDP ports 3478 and 10000-20000
- Corporate proxy not allowing WebRTC traffic
- Browser permissions denying camera/microphone access

**Resolution Steps:**
1. Check browser permissions: click the lock icon in the address bar > ensure camera and microphone are "Allow"
2. Test on a non-corporate network (mobile hotspot) to isolate firewall issues
3. Ask IT to allowlist: `*.ZavaConnect.io`, UDP 3478, UDP 10000-20000
4. Try TCP fallback: append `?transport=tcp` to the meeting URL
5. Clear browser cache and cookies for `ZavaConnect.io`

## Firewall and Proxy Configuration

IT administrators should allowlist the following for ZavaConnect:

```
Domains:
  *.ZavaConnect.io
  *.ZavaCloud.io
  turn.ZavaConnect.io

Ports:
  UDP 3478        (STUN/TURN)
  UDP 10000-20000 (Media)
  TCP 443         (Signaling + TURN fallback)
```

## Meeting Best Practices

1. **Join 2 minutes early** to test audio/video before the meeting starts
2. **Use a wired connection** for important meetings or presentations
3. **Close other conferencing apps** before joining (Teams, Zoom, WebEx)
4. **Use the built-in diagnostics** (Settings > Network > Run Diagnostics) to proactively identify issues
5. **Mute when not speaking** in meetings with 5+ participants to reduce background noise

## Related Articles
- KB-001: VPN Connectivity Troubleshooting
- KB-012: System Maintenance and Incident Response Playbook
- KB-008: MFA Setup and Troubleshooting
