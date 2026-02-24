# Community Forum: NimbusConnect Audio Dropping Mid-Meeting

**Article Number**: FORUM-002  
**Category**: Audio & Video  
**Product**: NimbusConnect

---

## Thread: Audio keeps cutting out every 15-20 seconds in NimbusConnect meetings

**Posted by:** @SarahW_GreenLeaf | January 25, 2026

Our team has been experiencing audio drops during NimbusConnect meetings. The audio cuts out for about 1-3 seconds every 15-20 seconds. It's happening for about 30 of our employees. Video seems fine — it's just the audio. We're using a mix of Bluetooth headsets (AirPods, Jabra Evolve2). Has anyone dealt with this?

---

### Reply 1

**Posted by:** @AudioEngineer_Mike | January 25, 2026

This sounds like a Bluetooth audio profile issue. When your headset connects in A2DP (stereo) mode, it uses the laptop mic instead of the headset mic. The laptop mic picks up the speaker output, and NimbusConnect's echo cancellation kicks in aggresively, causing those brief audio drops.

Quick test: do the audio drops happen with wired headphones? If not, it's definitely the Bluetooth profile.

Fix: Go to Windows Settings > System > Sound > Input — make sure it says your headset name with "(Hands-Free)" not your laptop mic. In NimbusConnect: Settings > Audio > Input Device > select the Hands-Free profile.

---

### Reply 2

**Posted by:** @SarahW_GreenLeaf | January 26, 2026

@AudioEngineer_Mike You're a genius — it was exactly that. I tested with wired headphones and no drops at all. Switched my AirPods to the Hands-Free profile and the drops stopped immediately.

One annoying thing though — the audio quality in Hands-Free mode sounds noticeably worse than A2DP. Is that expected?

---

### Reply 3

**Posted by:** @AudioEngineer_Mike | January 26, 2026

Yeah, that's the trade-off. A2DP is designed for high-quality audio playback (music, podcasts). HFP is designed for two-way communication — it uses a lower bitrate narrow-band codec. For meetings it's perfectly fine and clear, just not "music quality."

Some newer headsets (Jabra Evolve2 85, Sony WH-1000XM5) support Bluetooth LE Audio with LC3 codec which gives you better quality in both directions. But that requires Bluetooth 5.2 on the laptop too.

---

### Reply 4

**Posted by:** @IT_Admin_Derek | January 27, 2026

We dealt with this org-wide. Here's what we did:

1. Pushed a Group Policy to set the default audio input to the Bluetooth headset mic (not laptop mic) when a Bluetooth device is connected
2. Enabled NimbusConnect's built-in Acoustic Echo Cancellation as a safety net: Settings > Audio > Advanced > Enable AEC
3. Created a one-pager for employees on setting up their headsets correctly

Audio drop tickets went from 30/week to 2/week after these changes.

---

### Reply 5

**Posted by:** @RemoteWorker_Lisa | January 28, 2026

I've also noticed that 2.4 GHz interference kills Bluetooth audio quality. If you're near a microwave, baby monitor, or Wi-Fi router, the Bluetooth connection gets flaky. I moved my laptop further from my router and it made a huge difference.

Also, for AirPods specifically — make sure both buds are in and connected. If one bud runs out of battery mid-meeting, it switches profiles and causes the drops.

---

### Reply 6

**Posted by:** @SarahW_GreenLeaf | February 2, 2026

Update for anyone finding this thread: we rolled out the changes @IT_Admin_Derek suggested and audio drops have stopped for all 30 affected users. Thanks everyone! I also submitted a feature request to NimbusCloud asking them to auto-detect A2DP mode and warn users at the start of a meeting.
