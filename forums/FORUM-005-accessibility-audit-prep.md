# Community Forum: Preparing for Accessibility Audit — Checklist Sharing

**Article Number**: FORUM-005  
**Category**: Accessibility & Compliance  
**Product**: All NimbusCloud Products

---

## Thread: Section 508 audit coming up — what should we prepare for NimbusCloud?

**Posted by:** @EllenR_Compliance | February 3, 2026

Our organization (public school district) has a Section 508 accessibility audit scheduled for March. We use NimbusHub, NimbusDocs, NimbusBoard, NimbusConnect, and NimbusVault. Has anyone been through an audit with NimbusCloud products? What should we prepare?

---

### Reply 1

**Posted by:** @A11y_Expert_Maya | February 3, 2026

We went through a WCAG 2.1 AA audit last year. Here's what we learned:

**Step 1 — Get the VPATs**
Download current VPATs for all products from `https://nimbuscloud.io/accessibility/vpats`. Your auditors will want these as a baseline.

**Step 2 — Know the gaps**
The VPATs are honest about known issues:
- NimbusBoard's drag-and-drop kanban isn't screen-reader accessible (use Alt+M for the accessible modal instead)
- NimbusAdmin has some missing ARIA labels on dashboard charts
- NimbusDocs real-time collaboration cursors aren't announced to screen readers

None of these were deal-breakers in our audit because workarounds exist.

**Step 3 — Audit YOUR configuration**
Most audit findings are about content your team creates, not the platform itself:
- Custom themes with insufficient color contrast
- Documents without alt text
- NimbusBoard forms with missing labels
- Untagged PDFs uploaded to NimbusVault

---

### Reply 2

**Posted by:** @ScreenReader_Phil | February 4, 2026

I'm a daily JAWS user on NimbusCloud. My experience:

- **NimbusHub**: Works great with JAWS 2024. All messages, channels, and DMs are fully navigable.
- **NimbusDocs**: Works well for document editing. The command palette (Ctrl+/) is a lifesaver.
- **NimbusBoard**: The kanban view is the weak spot. Alt+M for moving cards works but it's clunky. List view is fully accessible though.
- **NimbusConnect**: Meetings are accessible. Ctrl+M to mute, Ctrl+D for camera. Chat panel during meetings could be better.
- **NimbusVault**: File browser works fine. Drag-and-drop upload isn't accessible but there's an "Upload" button.

Tell your auditors about the keyboard shortcuts — they make a big difference.

---

### Reply 3

**Posted by:** @EllenR_Compliance | February 5, 2026

This is incredibly helpful. We ran an automated scan using axe DevTools on our instance and found:
- 3 color contrast issues in our custom theme (we set a light gray on white — oops)
- 2 missing form labels in custom NimbusBoard templates
- 1 image without alt text in our NimbusHub welcome message

All solvable on our end. Thanks for the heads-up about focusing on our own content!

---

### Reply 4

**Posted by:** @IT_Director_Pat | February 6, 2026

One more thing — **enable auto-captioning** for NimbusConnect meetings before the audit. Go to NimbusAdmin > NimbusConnect > Settings > Auto-Caption Recordings. Auditors love seeing that video content is captioned.

Also check KB-005 — it has a comprehensive pre-audit checklist and the full compliance status table for all NimbusCloud products. Our auditor actually complimented us on having everything organized because we followed that guide.

---

### Reply 5

**Posted by:** @EllenR_Compliance | February 10, 2026

Thank you all! We've fixed all our custom content issues and enabled auto-captioning. Feeling much more confident about the March audit now. NimbusCloud support (CASE-005) has also been helpful — they provided a detailed gap assessment specific to our tenant.
