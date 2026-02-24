# Support Case: WCAG Accessibility Audit Preparation

**Case Number**: CASE-005  
**Status**: In Progress  
**Priority**: Medium  
**Product**: All NimbusCloud Products  
**Category**: Accessibility & Compliance  
**Origin**: Web  
**Contact**: Ellen Rodriguez, Compliance Officer, Cascadia Public Schools  
**Account**: Cascadia Public Schools  
**Created**: February 3, 2026  
**Last Updated**: February 10, 2026

---

## Subject
Requesting VPATs and guidance for upcoming Section 508 accessibility audit

## Description
Ellen Rodriguez is preparing for a Section 508 accessibility audit covering all NimbusCloud products used by Cascadia Public Schools: NimbusHub, NimbusDocs, NimbusBoard, NimbusConnect, and NimbusVault. The audit is scheduled for March 2026 and requires current VPATs, known accessibility gaps, and remediation plans.

## Investigation Notes

**2026-02-03 — Initial Response (Support Engineer: Tom Williams)**
- Provided links to current VPATs for all 5 products at `https://nimbuscloud.io/accessibility/vpats`
- Shared the pre-audit checklist from KB-005
- Noted known accessibility gaps:
  - NimbusBoard: Drag-and-drop kanban not accessible via screen reader (Alt+M modal workaround available)
  - NimbusAdmin: Some dashboard chart ARIA labels missing (fix in progress)
  - NimbusDocs: Real-time collaboration cursors not announced by screen readers

**2026-02-05 — Detailed Gap Assessment**
- Ran automated accessibility scan (axe DevTools) against Cascadia's NimbusCloud instance
- Findings:
  - 3 color contrast issues in Cascadia's custom theme (below 4.5:1 ratio on secondary buttons)
  - 2 missing form labels in NimbusBoard custom project templates created by Cascadia
  - 1 image without alt text in a NimbusHub custom welcome message
- Provided remediation steps for customer-controlled items (theme colors, form labels, alt text)

**2026-02-10 — Remediation In Progress**
- Ellen's team corrected the 3 custom theme contrast issues
- NimbusBoard custom form labels updated
- NimbusHub welcome message alt text added
- Remaining items are NimbusCloud product-level gaps (kanban drag-and-drop, ARIA labels) — communicated to Ellen with workarounds and ETA for fixes

## Resolution
In progress. Customer-controlled accessibility gaps remediated. NimbusCloud product-level gaps documented with workarounds. VPATs and pre-audit documentation delivered.

## Related Articles
- KB-005: Accessibility Compliance in NimbusCloud Products
- FORUM-005: Preparing for Accessibility Audit — Checklist Sharing
