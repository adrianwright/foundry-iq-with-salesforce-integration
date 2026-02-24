# Accessibility Compliance in NimbusCloud Products

**Article Number:** KB-005  
**Product:** All NimbusCloud Products  
**Category:** Accessibility & Compliance  
**Last Updated:** February 2026

## Overview

NimbusCloud is committed to accessibility across all products. This article covers WCAG 2.1 AA compliance status, screen reader compatibility, keyboard navigation support, and resources for customers preparing for Section 508 or ADA accessibility audits.

## Compliance Status by Product

| Product | WCAG 2.1 AA | Section 508 | VPAT Available | Last Audit |
|---------|-------------|-------------|----------------|------------|
| NimbusHub | Compliant | Compliant | Yes | January 2026 |
| NimbusDocs | Compliant | Compliant | Yes | January 2026 |
| NimbusBoard | Partially Compliant | Partially Compliant | Yes | November 2025 |
| NimbusConnect | Compliant | Compliant | Yes | December 2025 |
| NimbusVault | Compliant | Compliant | Yes | January 2026 |
| NimbusAdmin | Partially Compliant | Partially Compliant | Yes | October 2025 |
| NimbusID (Login) | Compliant | Compliant | Yes | January 2026 |

**VPATs** (Voluntary Product Accessibility Templates) are available at: `https://nimbuscloud.io/accessibility/vpats`

## Screen Reader Compatibility

### Tested Screen Readers
| Screen Reader | Platform | Compatibility |
|--------------|----------|---------------|
| JAWS 2024+ | Windows | Fully compatible |
| NVDA 2024.1+ | Windows | Fully compatible |
| VoiceOver | macOS / iOS | Fully compatible |
| TalkBack | Android | Compatible (NimbusHub mobile only) |

### Known Screen Reader Issues
1. **NimbusBoard** — Drag-and-drop kanban cards not accessible via screen reader. Workaround: use the keyboard shortcut (Alt+M) to move cards via a modal dialog.
2. **NimbusAdmin** — Some dashboard chart widgets lack proper ARIA labels. Fix targeted for Q1 2026.
3. **NimbusDocs** — Real-time collaboration cursors not announced by screen readers. Collaborator list panel (Alt+C) provides accessible alternative.

## Keyboard Navigation

All NimbusCloud products support full keyboard navigation:

### Global Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Tab` / `Shift+Tab` | Navigate between elements |
| `Enter` / `Space` | Activate buttons, links, checkboxes |
| `Escape` | Close modals, dismiss menus |
| `Alt+H` | Open keyboard shortcut help panel |
| `Alt+S` | Skip to main content |

### Product-Specific Shortcuts
- **NimbusHub**: `Ctrl+K` — Quick channel search, `Ctrl+Shift+M` — Toggle mute
- **NimbusDocs**: `Ctrl+/` — Open command palette, `Ctrl+Alt+H` — Insert heading
- **NimbusBoard**: `Alt+M` — Move card (accessible modal), `Alt+N` — New card
- **NimbusConnect**: `Ctrl+D` — Toggle camera, `Ctrl+M` — Toggle microphone

## Preparing for an Accessibility Audit

### Pre-Audit Checklist

1. **Download current VPATs** from `https://nimbuscloud.io/accessibility/vpats`
2. **Document your configuration** — Custom themes, embedded content, and third-party integrations may affect compliance
3. **Test with assistive technology** — Run through critical workflows with JAWS/NVDA and VoiceOver
4. **Check color contrast** — Custom branding/themes must maintain 4.5:1 contrast ratio (AA standard)
5. **Review document accessibility** — Uploaded PDFs and documents in NimbusDocs should have proper tags, alt text, and reading order
6. **Test keyboard navigation** — Verify all interactive elements are reachable and operable without a mouse
7. **Check focus indicators** — Ensure visible focus rings on all interactive elements (NimbusCloud default theme includes these)

### Common Audit Findings and Remediation

| Finding | Product | Remediation |
|---------|---------|-------------|
| Missing alt text on images | NimbusDocs, NimbusHub | Authors must add alt text; admin can enforce via policy: NimbusAdmin > Policies > Require Alt Text |
| Insufficient color contrast in custom themes | All products | Revert to default theme or adjust custom colors to meet 4.5:1 ratio |
| Focus not visible on custom buttons | NimbusHub (custom integrations) | Custom integrations must follow NimbusCloud UI toolkit accessibility guidelines |
| Video content lacks captions | NimbusConnect recordings | Enable auto-captioning: NimbusAdmin > NimbusConnect > Settings > Auto-Caption Recordings |
| Form fields missing labels | NimbusBoard custom forms | Use the form builder label field; never leave labels blank |

## Accessibility Support

- **Accessibility feedback**: accessibility@nimbuscloud.io
- **Accessibility documentation**: `https://docs.nimbuscloud.io/accessibility`
- **VPAT requests**: Available for all products at `https://nimbuscloud.io/accessibility/vpats`
- **Custom audit support**: Contact your NimbusCloud Customer Success Manager for pre-audit guidance

## Best Practices

1. **Enforce alt text policy** in NimbusAdmin for all uploaded images
2. **Use the default theme** or test custom themes for WCAG color contrast compliance
3. **Enable auto-captioning** for all NimbusConnect meetings and recordings
4. **Train content creators** on accessible document authoring (headings, alt text, reading order)
5. **Run quarterly accessibility checks** using browser extensions (axe DevTools, WAVE)

## Related Articles
- KB-002: NimbusConnect Video Call Quality Troubleshooting
- KB-010: Email Deliverability and Notification Configuration
- KB-012: System Maintenance and Incident Response Playbook
