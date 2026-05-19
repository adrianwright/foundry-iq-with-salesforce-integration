# Community Forum: Bulk Workspace Cloning Tips and Gotchas

**Article Number**: FORUM-009  
**Category**: Data Migration & Templates  
**Product**: ZavaBoard

---

## Thread: Quarterly workspace cloning — 73 of 200 failed. How do you handle bulk clones?

**Posted by:** @KarenJ_PMO | February 12, 2026

We clone all 200 of our ZavaBoard project workspaces at the start of each quarter for Q+1 planning. This quarter, 73 of 200 failed. Errors were: "workspace exceeds 10,000 cards," "integration clone failed," and "attachment size exceeded." How does everyone else handle bulk cloning without these headaches?

---

### Reply 1

**Posted by:** @PMO_Veteran_Raj | February 12, 2026

We clone 150+ workspaces every quarter and here's our pre-clone checklist:

1. **Archive old cards:** Before cloning, archive all cards created more than 6 months ago. Keeps workspaces under the 10,000 card limit. We use the API for this: `POST /api/v2/workspaces/{id}/cards/archive?created_before=YYYY-MM-DD`

2. **Clone without integrations:** Always uncheck "Automations and rules" during bulk clone. Re-add integrations manually to the new workspace with updated webhook URLs for the new quarter's Slack channels.

3. **Clone without attachments:** Large workspaces have GB of attachments. Clone the structure, then selectively migrate needed files via ZavaVault.

4. **Use templates instead of cloning** for workspaces that follow the same structure every quarter. Save the workspace as a template once, create new workspaces from the template.

Our failure rate dropped from ~30% to < 5% after implementing this checklist.

---

### Reply 2

**Posted by:** @KarenJ_PMO | February 13, 2026

@PMO_Veteran_Raj That archive tip is huge — we had workspaces with 15,000+ cards from 3 years of quarterly cloning. Archived everything older than 6 months and re-ran the 41 oversized workspaces. All succeeded.

For the 22 integration failures — cloning without integrations worked. Re-adding Slack webhooks is tedious but I see why it's necessary (old webhook URLs point to last quarter's channels).

---

### Reply 3

**Posted by:** @AutomationWiz_Nina | February 14, 2026

For the integration re-add problem, here's a trick: Use ZavaBoard's automation **import/export** feature. Before cloning:

1. Go to each workspace > Settings > Automations > Export (JSON)
2. Edit the JSON to update webhook URLs, channel IDs, etc.
3. After cloning, import the updated automation JSON to the new workspace

This way you only need to update the JSON file once (find-and-replace URLs) and can import to multiple workspaces. Still some manual work but faster than re-creating each automation from scratch.

---

### Reply 4

**Posted by:** @ProjectManager_Steve | February 15, 2026

We took a different approach entirely: **workspaces as templates**.

Instead of cloning last quarter's workspace (which accumulates stale cards and outdated automations), we maintain a set of "golden templates" in ZavaAdmin > ZavaBoard > Templates. Each quarter, we create fresh workspaces from templates and migrate only active cards from the previous quarter.

Yes, it's more work upfront to set up the templates. But zero clone errors ever, and each new quarter starts clean.

---

### Reply 5

**Posted by:** @KarenJ_PMO | February 18, 2026

Update: All 200 workspaces cloned successfully for Q2 after following the advice here. Our process going forward:

1. **Week before quarter end**: Archive cards > 6 months old
2. **Clone**: Without integrations and without attachments
3. **Post-clone**: Import updated automation JSONs, migrate needed files
4. **Next quarter**: Evaluate @ProjectManager_Steve's template approach

KB-009 has the complete guide to workspace cloning and migration. Thanks everyone!

---

### Reply 6

**Posted by:** @NewPM_Jessica | February 20, 2026

Just a heads-up for anyone on the ZavaCloud Business plan — the bulk clone feature has a limit of 200 workspaces per job. If you need more, split into multiple jobs. Also, run bulk clones during off-peak hours — our 200-workspace clone took about 25 minutes on a Saturday morning vs. 90 minutes on a Tuesday afternoon.
