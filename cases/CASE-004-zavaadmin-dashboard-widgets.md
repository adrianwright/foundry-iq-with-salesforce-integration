# Support Case: ZavaAdmin Dashboard Widgets Not Loading

**Case Number**: CASE-004  
**Status**: Resolved  
**Priority**: Medium  
**Product**: ZavaAdmin  
**Category**: Admin Console  
**Origin**: Web  
**Contact**: Lisa Park, IT Director, Summit Healthcare Group  
**Account**: Summit Healthcare Group  
**Created**: February 1, 2026  
**Last Updated**: February 6, 2026

---

## Subject
ZavaAdmin analytics dashboard showing blank widgets and "Data unavailable" errors

## Description
Lisa Park reported that the ZavaAdmin analytics dashboard has been showing blank widgets for the past 3 days. The user activity charts, license utilization graph, and login trend widget all display "Data unavailable." The issue affects all admin users at Summit Healthcare Group, not just Lisa's account.

## Investigation Notes

**2026-02-01 — Initial Triage (Support Engineer: Kevin Nguyen)**
- Confirmed blank dashboard across 3 admin accounts at Summit Healthcare Group
- Tenant was provisioned 5 days ago — within the 24-hour initial data pipeline window, but past it
- Checked analytics pipeline status — data pipeline shows "Healthy" for this tenant
- Browser console shows 403 errors when loading dashboard widgets from `analytics.internal.ZavaCloud.io`
- Root cause identified: Admin users have the "Tenant Admin" role but not the "Analytics Viewer" role — these are separate permissions

**2026-02-02 — Fix Applied**
- Added "Analytics Viewer" role to all 3 admin accounts
- Advised Lisa to add this role to the default admin role template for future admin users
- Dashboard widgets loaded successfully after role assignment
- All historical data (5 days) appeared correctly — no data loss

**2026-02-06 — Follow-Up**
- Lisa confirmed all dashboard widgets are working and have been stable for 4 days
- Updated their admin onboarding checklist to include "Analytics Viewer" role assignment

## Resolution
Admin users were missing the "Analytics Viewer" role, which is separate from "Tenant Admin." Adding the role immediately restored dashboard widget access. KB-004 documents required admin roles.

## Related Articles
- KB-004: ZavaAdmin Tenant and User Provisioning
- FORUM-004: ZavaAdmin Analytics Dashboard Tips
