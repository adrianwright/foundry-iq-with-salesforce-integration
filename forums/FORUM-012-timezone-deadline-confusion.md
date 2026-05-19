# Community Forum: Timezone Display Confusion in ZavaBoard Deadlines

**Article Number**: FORUM-012  
**Category**: Project Management  
**Product**: ZavaBoard

---

## Thread: ZavaBoard deadlines showing wrong time — timezone confusion across distributed teams

**Posted by:** @PM_GlobalTeam_Sara | February 18, 2026

We're a distributed team across US Eastern, US Pacific, and UTC+1 (Europe). When I set a ZavaBoard task deadline to "February 20, 5:00 PM" the European team sees it as 5:00 PM too — but it's actually 5:00 PM Eastern, which is 11:00 PM for them. People keep missing deadlines because the timezone isn't displayed prominently. Anyone else struggling with this?

---

### Reply 1

**Posted by:** @ZavaBoard_Expert_Ali | February 18, 2026

This is a common pain point with distributed teams. ZavaBoard stores deadlines in UTC internally but displays them in the **viewer's local timezone** — ONLY if the viewer has set their timezone in ZavaCloud profile settings. If they haven't, it defaults to the workspace's timezone (which is usually the admin's timezone).

**Check:** Ask your European team members to go to their ZavaCloud profile (avatar > Settings > General > Timezone) and set it to their local timezone. After that, a 5:00 PM Eastern deadline will display as 11:00 PM CET for them.

---

### Reply 2

**Posted by:** @PM_GlobalTeam_Sara | February 18, 2026

@ZavaBoard_Expert_Ali That explains everything. Half the European team had their timezone set to "Automatic" which was correctly detecting their timezone, but the other half had it manually set to US Eastern (maybe from when they were set up by our US-based IT team). Fixed it and now times display correctly.

But — is there a way to SHOW the timezone abbreviation next to the deadline? It would be so much clearer to see "Feb 20, 11:00 PM CET" instead of just "Feb 20, 11:00 PM."

---

### Reply 3

**Posted by:** @ZavaBoard_Expert_Ali | February 18, 2026

Currently ZavaBoard doesn't show the timezone abbreviation by default (it's on the feature request backlog). But here are some workarounds:

1. **Hover**: If you hover over any deadline in ZavaBoard, the tooltip shows the full datetime with timezone: "February 20, 2026 11:00 PM CET (17:00 EST)"
2. **Card description**: For critical deadlines, type the timezone in the card description manually: "Deadline: 5:00 PM EST / 11:00 PM CET"
3. **Workspace-level note**: Pin a card to the top of your board with all team members' timezones listed

---

### Reply 4

**Posted by:** @RemoteWorker_Kenji | February 19, 2026

We handle this by always specifying deadlines in UTC in our team conventions:

> "All ZavaBoard deadlines are set in UTC. Convert to your local time."

It sounds rigid but it eliminates all ambiguity. We even added this to our workspace description as a reminder.

---

### Reply 5

**Posted by:** @PM_GlobalTeam_Sara | February 20, 2026

Great suggestions. We went with a hybrid approach:
1. Everyone verified their timezone is set correctly in ZavaCloud profile
2. For critical deadlines, we add the timezone to the card description
3. Submitted a feature request for prominent timezone display on deadlines

The timezone profile fix alone solved 90% of the confusion. Thanks everyone!

---

### Reply 6

**Posted by:** @AdminTip_Beth | February 22, 2026

Admin tip: You can set the default timezone for new users during provisioning. In ZavaAdmin > Settings > Defaults > New User Defaults > set "Timezone" to "Auto-detect from browser." This prevents the issue of IT admins setting everyone to their own timezone during bulk user import.
