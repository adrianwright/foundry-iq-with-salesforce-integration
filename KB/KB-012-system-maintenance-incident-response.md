# System Maintenance and Incident Response Playbook

**Article Number:** KB-012  
**Product:** All ZavaCloud Products  
**Category:** Operations & Incident Response  
**Last Updated:** February 2026

## Overview

This article is the reference guide for ZavaCloud system maintenance windows, incident response procedures, and communication protocols. It covers scheduled maintenance, emergency patching, incident severity classification, and rollback procedures.

## Scheduled Maintenance

### Maintenance Windows
| Window | Time (UTC) | Frequency | Typical Duration |
|--------|-----------|-----------|-----------------|
| Standard | Saturday 02:00-06:00 | Monthly | 2-4 hours |
| Extended | Saturday 00:00-08:00 | Quarterly | 4-8 hours |
| Emergency | Any time | As needed | 30-120 minutes |

### Maintenance Notifications
- **14 days before**: Email notification to tenant admins
- **7 days before**: In-app banner in ZavaAdmin
- **24 hours before**: Email reminder + status page update at `status.ZavaCloud.io`
- **At start**: Status page updated to "Maintenance in Progress"
- **At completion**: Status page updated to "All Systems Operational" + completion email

### What Happens During Maintenance
| Product | Impact | User Experience |
|---------|--------|----------------|
| ZavaHub | Brief interruption (< 5 min) | Messages queue and deliver after maintenance |
| ZavaDocs | Read-only mode | Users can view but not edit documents |
| ZavaBoard | Brief interruption (< 5 min) | Auto-save preserves in-progress work |
| ZavaConnect | Active meetings unaffected | New meetings may fail to start during window |
| ZavaVault | Read-only mode | File uploads paused, downloads available |
| ZavaAdmin | Full downtime | Admin console unavailable during window |
| ZavaAPI | Degraded | Read endpoints available, write endpoints return 503 |

## Incident Severity Classification

| Severity | Definition | Response Time | Example |
|----------|-----------|---------------|---------|
| SEV-1 (Critical) | Complete service outage affecting all users | 15 minutes | ZavaCloud login down for all tenants |
| SEV-2 (High) | Major feature unavailable or severe degradation | 30 minutes | ZavaConnect meetings failing for 30%+ users |
| SEV-3 (Medium) | Minor feature unavailable or moderate degradation | 2 hours | ZavaDocs export feature returning errors |
| SEV-4 (Low) | Cosmetic issue or minor inconvenience | Next business day | Dashboard chart rendering incorrectly |

## Incident Response Procedure

### 1. Detection
- **Automated monitoring**: PagerDuty alerts on error rate spikes, latency thresholds, and health check failures
- **Customer reports**: Support cases tagged as "Service Disruption" auto-escalate
- **Status page monitors**: External uptime monitoring from multiple regions

### 2. Triage (First 15 Minutes)
1. On-call engineer acknowledges the alert
2. Confirm the scope: which products, which regions, how many tenants
3. Classify severity (SEV-1 through SEV-4)
4. Open an incident channel in the internal communications tool
5. Update status page to "Investigating"

### 3. Mitigation
1. Identify the root cause or most likely cause
2. Determine if a rollback, hotfix, or infrastructure change is needed
3. Execute the mitigation (see Rollback Procedures below)
4. Update status page to "Identified" with ETA

### 4. Resolution
1. Confirm the fix has resolved the issue for all affected users
2. Monitor for 30 minutes post-fix to ensure stability
3. Update status page to "Resolved"
4. Send resolution notification to affected tenants

### 5. Post-Incident Review
1. Schedule a blameless post-mortem within 48 hours
2. Document: timeline, root cause, impact, mitigation steps, and follow-up actions
3. Publish a summary to the status page (for SEV-1 and SEV-2 incidents)
4. Track follow-up action items to prevent recurrence

## Rollback Procedures

### Application Rollback
1. Identify the last known good deployment version
2. Execute rollback via CI/CD pipeline: `zava-deploy rollback --version <last-good>`
3. Verify health checks pass on the rolled-back version
4. Monitor error rates for 15 minutes post-rollback

### Database Rollback
1. Identify the point-in-time for recovery
2. For schema changes: run the reverse migration script
3. For data corruption: restore from the nearest backup (RPO: 5 minutes, hourly snapshots)
4. Verify data integrity with automated consistency checks

### Infrastructure Rollback
1. If infrastructure change caused the incident, revert via Infrastructure as Code
2. Redeploy the previous infrastructure version
3. Verify all dependent services reconnect successfully

## Maintenance Overrun Protocol

If a scheduled maintenance window overruns:
1. **At window end time**: Post status page update "Maintenance Extended — ETA [time]"
2. **15 minutes after window**: Email admins of affected tenants with new ETA
3. **If > 2x planned duration**: Escalate to engineering leadership; consider rollback
4. **Every 30 minutes**: Update status page with progress

## Best Practices for Administrators

1. **Subscribe to the status page** at `status.ZavaCloud.io` for real-time updates
2. **Communicate maintenance windows** to your organization's end users proactively
3. **Avoid scheduling critical work** during published maintenance windows
4. **Configure webhook notifications** for status page events (ZavaAdmin > Notifications > Status Page)
5. **Keep emergency contacts updated** in ZavaAdmin > Settings > Support Contacts

## Related Articles
- KB-001: VPN Connectivity Troubleshooting
- KB-002: ZavaConnect Video Call Quality Troubleshooting
- KB-011: ZavaAPI Rate Limits and Integration Best Practices
