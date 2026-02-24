# Community Forum: Phantom Accounts from SCIM — Anyone Else Seeing This?

**Article Number**: FORUM-003  
**Category**: Identity & Provisioning  
**Product**: NimbusID / NimbusAdmin

---

## Thread: SCIM creating duplicate/phantom user accounts — 47 extra users appeared overnight

**Posted by:** @DavidC_DirServices | January 28, 2026

After migrating our directory from on-prem AD to Entra ID, we discovered 47 phantom user accounts in NimbusAdmin that shouldn't exist. They appear to be duplicates of real users but with different email formats (firstname.lastname@ vs flastname@). Our SCIM connector is creating new accounts instead of updating existing ones when the UPN format changes. Has anyone dealt with this?

---

### Reply 1

**Posted by:** @IAM_Specialist_Ravi | January 28, 2026

Yes, this is a classic SCIM matching issue. Most SCIM connectors default to matching on `userName` (which is usually the email/UPN). When your UPN format changes during a migration, SCIM sees it as a completely new user.

**The fix:** Change your SCIM connector's matching attribute from `userName` to `externalId`. In Azure/Entra ID, `externalId` maps to the Object ID which is immutable — it never changes regardless of UPN changes.

In your Entra ID SCIM provisioning config:
1. Go to Enterprise Applications > NimbusCloud > Provisioning > Edit Attribute Mappings
2. Find the mapping for `externalId` — ensure it maps to `objectId`
3. Set the matching precedence to use `externalId` first (not `userName`)

---

### Reply 2

**Posted by:** @DavidC_DirServices | January 29, 2026

@IAM_Specialist_Ravi That makes sense. Before I change the matching attribute — how do I clean up the 47 phantom accounts? Some of them have actually been used (people logged in with the wrong account and created documents in NimbusDocs).

---

### Reply 3

**Posted by:** @NimbusAdmin_Pro | January 29, 2026

For cleanup, you need to merge the phantom accounts into the real accounts:

1. **NimbusAdmin > Users** — search for each phantom account
2. Check if the phantom account has any data (files, messages, task assignments)
3. If it has data: Select both the phantom and real account > click **Merge Accounts** — this transfers all data from the phantom to the real account
4. If it's empty: Just delete it

For 47 accounts, I'd use the NimbusAPI to script this instead of doing it manually. Here's a rough approach:

```python
# For each phantom account, check for content and merge or delete
for phantom in phantom_accounts:
    real_account = find_matching_real_account(phantom)
    if has_content(phantom):
        merge_accounts(phantom.id, real_account.id)
    else:
        delete_account(phantom.id)
```

---

### Reply 4

**Posted by:** @DavidC_DirServices | February 3, 2026

Update: Followed the advice here and in CASE-003 that NimbusCloud support helped with. Here's the full resolution:

1. Changed SCIM matching from `userName` to `externalId` ✅
2. Merged 9 phantom accounts that had data ✅
3. Deleted 38 empty phantom accounts ✅
4. Re-ran full SCIM sync — all users matched correctly, zero duplicates ✅

**Pro tip for anyone migrating directories:** Change your SCIM matching attribute BEFORE the migration, not after. Would have saved us a lot of cleanup.

---

### Reply 5

**Posted by:** @IAM_Specialist_Ravi | February 3, 2026

Glad it worked out. I'd also recommend submitting a feature request to NimbusCloud for fuzzy duplicate detection during SCIM provisioning. Something like "Warning: New user `jane.doe@company.com` closely matches existing user `jdoe@company.com` — potential duplicate" would catch this before it becomes a cleanup project.

---

### Reply 6

**Posted by:** @NewAdmin_Tina | February 5, 2026

We're about to set up SCIM for the first time — saving this thread as a cautionary tale! Using `externalId` from day one. KB-004 also has great guidance on SCIM configuration.
