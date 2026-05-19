# Support Case: Scheduled Maintenance Window Overrun

**Case Number**: CASE-012  
**Status**: Resolved  
**Priority**: Critical  
**Product**: All ZavaCloud Products  
**Category**: Operations & Incident Response  
**Origin**: Phone  
**Contact**: Patricia Gomez, VP of Operations, Stellar Manufacturing  
**Account**: Stellar Manufacturing  
**Created**: February 15, 2026  
**Last Updated**: February 16, 2026

---

## Subject
ZavaCloud maintenance window overran by 3 hours — production blocked for overnight shift operations

## Description
Patricia Gomez reported that the scheduled ZavaCloud maintenance window (Saturday 02:00-06:00 UTC) overran until 09:00 UTC. Stellar Manufacturing's overnight shift (which starts at 06:00 UTC) was unable to access ZavaHub for operational communications, ZavaDocs for shift reports, and ZavaBoard for task management. The overrun was not communicated until 07:30 UTC, 90 minutes after the original window was supposed to end.

## Investigation Notes

**2026-02-15 — Incident Timeline**
- 02:00 UTC: Scheduled maintenance began — status page updated to "Maintenance in Progress"
- 04:30 UTC: Database migration step encountered an unexpected schema conflict — required manual intervention
- 06:00 UTC: Original maintenance window end — services not yet restored
- 06:15 UTC: Overrun detected by monitoring — internal escalation began
- 07:30 UTC: Status page updated to "Maintenance Extended — ETA 09:00 UTC" — **90-minute communication gap**
- 08:45 UTC: All services restored and verified
- 09:00 UTC: Status page updated to "All Systems Operational"

**2026-02-15 — Customer Impact**
- Stellar Manufacturing's overnight shift (200+ workers) had no access to ZavaCloud from 06:00-09:00 UTC
- Shift supervisor created paper-based workarounds for task tracking
- Estimated productivity impact: 3 hours × 200 workers = 600 person-hours
- No data loss — all pending messages, documents, and tasks were preserved during maintenance

**2026-02-16 — Post-Incident Actions by ZavaCloud**
- Published post-mortem to status page:
  - Root cause: Database migration for ZavaBoard analytics tables had an undocumented dependency on a ZavaDocs schema
  - Why communication was delayed: Status page update process required manual DBA confirmation that was delayed during the troubleshooting
- Action items:
  1. Implement automated status page updates when maintenance overruns the scheduled window (30-second delay alerts)
  2. Add dependency mapping to migration planning process
  3. Improve maintenance dry-run testing in staging environment
- Offered Stellar Manufacturing a service credit for the overrun

## Resolution
Maintenance overrun caused by an undocumented database schema dependency. Services restored 3 hours after the planned window. Post-mortem published, automated overrun alerts being implemented, service credit offered. KB-012 documents the maintenance overrun protocol.

## Related Articles
- KB-012: System Maintenance and Incident Response Playbook
- FORUM-012: Timezone Display Confusion in ZavaBoard Deadlines
