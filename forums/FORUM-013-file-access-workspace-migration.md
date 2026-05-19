# Community Forum: File Access Denied After Workspace Migration

**Article Number**: FORUM-013  
**Category**: File Management & Permissions  
**Product**: ZavaVault

---

## Thread: 350 users can't access files after workspace restructuring — "Access Denied" everywhere

**Posted by:** @MichelleT_Ops | February 17, 2026

We just consolidated 12 department-level ZavaCloud workspaces into 4 division-level workspaces and moved ZavaVault folders accordingly. Now 350 users are getting "Access Denied" on files they could access yesterday. The folder structure looks correct — it's just permissions that are broken. How do we fix this without re-sharing thousands of files?

---

### Reply 1

**Posted by:** @VaultAdmin_Casey | February 17, 2026

When you move folders in ZavaVault, **inherited permissions from the old parent are dropped**. Only direct (explicit) permissions on the folder/file are preserved. If most of your users had access via inheritance (which is the normal/recommended way), moving the folder stripped their access.

**Quick fix:** On each moved folder, go to Sharing & Permissions > Advanced > click **"Re-inherit from parent"**. This will apply the new parent folder's permissions to the moved folder and all its contents.

But before you do that — make sure the new parent folders have the right groups added with the right access level.

---

### Reply 2

**Posted by:** @MichelleT_Ops | February 17, 2026

@VaultAdmin_Casey That makes sense. Our new division-level parent folders only have division-level groups, but users are still in department-level groups. So re-inheriting from the new parent would give access to the division groups but not the department-specific users.

Do I need to add all 12 department groups to the 4 division groups?

---

### Reply 3

**Posted by:** @IAM_Specialist_Ravi | February 18, 2026

Yes — nest the department groups inside the division groups. In ZavaAdmin > Groups:

1. Open the division group (e.g., "Engineering Division")
2. Add department groups as members: "Frontend Team," "Backend Team," "DevOps Team"
3. Now anyone in a department group automatically gets the division group's permissions

Then run "Re-inherit from parent" on the moved folders. Department users will get access through the chain: Department Group → Division Group → Folder Permissions.

---

### Reply 4

**Posted by:** @MichelleT_Ops | February 19, 2026

Nested the groups and re-inherited permissions on all 8 moved folders. Access is restored! Verified with 10 sample users across different departments — all working.

One follow-up issue: we had ~200 external shared links (documents shared with clients via link). Those are all broken because the file IDs changed during the move. Is there a way to fix those in bulk?

---

### Reply 5

**Posted by:** @VaultAdmin_Casey | February 19, 2026

For broken shared links:
1. ZavaAdmin > ZavaVault > Shared Links > filter by "Broken" status
2. You'll see all links pointing to files that moved or were deleted
3. For each broken link, you can click "Locate file" — ZavaVault will try to find the file in its new location
4. Click "Regenerate link" to create a new sharing URL

Unfortunately, for 200 links there's no bulk fix — you'll need to regenerate each one and send the new URL to the recipients. This is a good argument for using file IDs instead of path-based sharing in the future.

---

### Reply 6

**Posted by:** @MichelleT_Ops | February 22, 2026

All resolved. Here's our migration checklist for anyone moving ZavaVault folders:

1. **Before migration**: Run a permission audit (ZavaAdmin > ZavaVault > Permission Audit) and document current state
2. **Plan group nesting**: Ensure new parent folder groups include all needed sub-groups
3. **Move folders**: Drag-and-drop or use ZavaAdmin > ZavaVault > Move
4. **Re-inherit permissions**: Sharing & Permissions > Advanced > Re-inherit from parent
5. **Fix shared links**: ZavaAdmin > ZavaVault > Shared Links > filter "Broken" > regenerate
6. **After migration**: Run permission audit again to verify

KB-013 has the full documentation. CASE-013 has our specific investigation with ZavaCloud support. Never moving folders without this checklist again!
