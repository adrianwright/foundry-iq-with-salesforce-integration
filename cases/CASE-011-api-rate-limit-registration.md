# Support Case: API Rate Limit Hits During Peak Registration Sync

**Case Number**: CASE-011  
**Status**: Escalated  
**Priority**: High  
**Product**: ZavaAPI  
**Category**: API & Developer  
**Origin**: Web  
**Contact**: Alex Dubois, Lead Developer, Horizon University  
**Account**: Horizon University  
**Created**: February 14, 2026  
**Last Updated**: February 20, 2026

---

## Subject
ZavaAPI returning 429 errors during nightly student registration sync — 15,000 API calls failing

## Description
Alex Dubois reported that Horizon University's nightly student registration sync (which provisions ZavaCloud accounts for enrolled students) is hitting API rate limits. The sync job makes approximately 25,000 API calls to create and update user accounts but consistently gets throttled after 10,000 calls, causing 15,000 to fail with 429 Too Many Requests. The sync must complete within a 4-hour overnight window.

## Investigation Notes

**2026-02-14 — Initial Triage (Support Engineer: Fatima Al-Hassan)**
- Confirmed Horizon University is on the Business plan: 300 requests/minute, 100,000 requests/day
- The sync job is sending requests as fast as possible without throttle — averaging 600 requests/minute, 2x the limit
- No exponential backoff implemented — on 429, the job retries immediately, exacerbating the throttling
- Individual `POST /api/v2/users` calls for each student instead of using the batch endpoint

**2026-02-15 — Optimization Recommendations**
- Switch from individual user creation to batch endpoint: `POST /api/v2/users/batch` (100 users per request)
  - This reduces 25,000 API calls to 250 batch requests
  - Batch requests count as a single rate-limited request regardless of batch size
- Implement exponential backoff with jitter per KB-011 guidance
- Spread the sync across the full 4-hour window instead of bursting

**2026-02-17 — Code Changes Deployed**
- Alex refactored the sync job:
  - Batch endpoint: 25,000 users / 100 per batch = 250 API calls (down from 25,000)
  - Added exponential backoff with jitter on 429 responses
  - Paced requests at 5 per minute (well within the 300/minute limit)
- Test run completed in 52 minutes with zero 429 errors

**2026-02-20 — Production Validation**
- Full nightly sync ran successfully for 3 consecutive nights with zero rate limit errors
- Average completion time: 48 minutes (down from 4+ hours with failures)
- Alex requested a temporary rate limit increase for annual enrollment surge in August — escalated to ZavaCloud support for Enterprise plan evaluation

## Resolution
Sync job refactored to use batch API endpoints (250 calls instead of 25,000) and exponential backoff with jitter. Rate limit errors eliminated. Escalated Enterprise plan evaluation for annual enrollment surge. KB-011 provides API rate limit and integration best practices.

## Related Articles
- KB-011: ZavaAPI Rate Limits and Integration Best Practices
- KB-004: ZavaAdmin Tenant and User Provisioning
- FORUM-011: API Rate Limit Strategies — Share Your Approach
