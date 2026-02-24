# Community Forum: NimbusAdmin Analytics Dashboard Tips

**Article Number**: FORUM-004  
**Category**: Admin Console  
**Product**: NimbusAdmin

---

## Thread: NimbusAdmin dashboard widgets blank — "Data unavailable" — what am I missing?

**Posted by:** @LisaP_Summit | February 1, 2026

I'm a new NimbusAdmin admin and the analytics dashboard is completely blank. All widgets show "Data unavailable." Our tenant has been active for 5 days with 200+ users. Is there a setup step I'm missing?

---

### Reply 1

**Posted by:** @AdminVeteran_Ray | February 1, 2026

Two things to check:

1. **Role**: You need the "Analytics Viewer" role, which is separate from "Tenant Admin." Go to NimbusAdmin > Users > find your account > Roles. If you only see "Tenant Admin," you need to add "Analytics Viewer."

2. **Ad-blocker**: Some browser ad-blockers block the analytics endpoints because they match common tracking URL patterns. Try disabling your ad-blocker for `*.nimbuscloud.io` or test in an incognito window.

In my case, it was the role. Took me an hour to figure out!

---

### Reply 2

**Posted by:** @LisaP_Summit | February 1, 2026

@AdminVeteran_Ray It was the role! I had "Tenant Admin" but not "Analytics Viewer." Added it and everything loaded immediately. Why aren't these bundled together?

---

### Reply 3

**Posted by:** @NimbusAdmin_Pro | February 2, 2026

They're separate because some orgs want IT admins who can manage users and settings but shouldn't see usage analytics (privacy/HR concerns). It's a least-privilege design.

**Tip:** Create a custom role template that combines both. Go to NimbusAdmin > Settings > Roles > Create Custom Role > combine "Tenant Admin" + "Analytics Viewer" permissions. Then assign that combined role to future admins.

---

### Reply 4

**Posted by:** @DashboardGuru_Amy | February 3, 2026

Since we're talking dashboards — here are some tips I've learned:

- **Custom widgets:** You can create custom dashboard widgets by going to Dashboard > Add Widget > Custom Query. Super useful for tracking specific metrics like "NimbusConnect meetings per week" or "NimbusDocs active editors."
- **Scheduled reports:** Dashboard > Export > Schedule — set up weekly PDF reports emailed to leadership
- **Data latency:** Most dashboard data refreshes every 4 hours. Real-time data is only available for login events and security dashboards.
- **Comparison mode:** Click the date range selector > enable "Compare" to overlay current period vs previous period. Great for showing adoption trends.

---

### Reply 5

**Posted by:** @LisaP_Summit | February 6, 2026

These tips are gold — thank you everyone. I've set up a weekly scheduled report for our CIO and created a custom widget tracking NimbusHub active daily users. Our adoption metrics are already improving and being able to show the data makes a big difference.

For anyone else hitting this: the CASE-004 support case confirmed the role fix, and KB-004 has the full documentation on admin roles and permissions.
