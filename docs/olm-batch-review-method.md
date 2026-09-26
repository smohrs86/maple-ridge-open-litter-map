# Batch-fixing existing OpenLitterMap tags through the API

A reusable method for reviewing and correcting the tags on photos you have already uploaded and had verified in OpenLitterMap (OLM), in bulk, without using the website or app. Written so that a person, or another AI given this file, can follow it without any other context.

**Status: draft, 2026-09-26.** Only the raw export script exists. Nothing here has been tested by writing to OLM yet. Every claim is marked:
- **[source]** read from OLM's public code (`OpenLitterMap/openlittermap-web`, `master` branch, read 2026-09-26). Production could differ.
- **[tested]** confirmed on a real photo. None yet. Update this file after each test.

## The problem

Legacy tags in OLM can be inconsistent (an object tagged with the wrong key, a custom tag that should be an object, and so on). Fixing thousands of objects one at a time in the app is not practical. OLM's API can rewrite tags, but a careless rewrite could lose data or drop photos from the public map.

## What OLM does when you rewrite tags

- **[source]** `PUT /api/v3/tags` replaces **all** tags on one photo you own. There is no per-tag edit endpoint. Changing one object means resending every tag on that photo. `POST /api/v3/tags` only appends and refuses a photo that already has tags.
- **[source]** The request carries no image. The photo file, location and date are untouched. Only tags are deleted and recreated, so tag-row IDs change.
- **[source]** Verification is reset to 0 and then re-applied in the same database transaction. If the account is trusted (`verification_required = false`) the photo returns to verified = 2 (admin approved), which is what OLM treats as public-ready. If the account is not trusted, the photo ends at 0 and leaves the public map. **Which case applies to an account must be tested, not assumed.**
- **[source]** Verification levels 3 to 5 (bounding boxes drawn or verified, AI-ready) appear to be reset to 2 by a replace. Check whether your photos have any.
- **[source]** OLM recalculates XP and its metrics for each replaced photo.
- **[source]** Ownership is checked, and already-verified photos are explicitly allowed.
- **[source]** The photo list (`GET /api/v3/user/photos`) accepts `per_page` up to 100 and returns each photo's `verified`, `picked_up`, coordinates and tags with OLM's internal IDs.
- **[source]** `picked_up` exists on the photo and on each tag. The list converts it to true or false, so a tag with no value is indistinguishable from "not picked up". Compare the counts in the export summary before trusting a replay of `picked_up`.
- **[source]** OLM's tag list (`GET /api/tags/all`) gives the IDs for each category, object, type, material and brand. A replace request needs those IDs (`category_litter_object_id`, `litter_object_type_id`). Custom tags are plain text.

## The method

1. **Export (read-only).** `scripts/export_raw_olm.py` reads every photo and OLM's tag list into `review/raw/` (untracked, owner-only). This is the backup. It also prints counts only (verified values, `picked_up` values) that are safe to share.
2. **Fill the review spreadsheet.** One row per tagged object (the `Objects` sheet), plus one row per photo (`Photo_Batch`). *Script not written yet.*
3. **Review one group at a time.** Filter by current OLM key (and custom tag) to isolate a group, look at the photos, and type the fix in the `Change_to_…` cells.
4. **Dry run.** A script builds each affected photo's full replacement tag list, shows before and after, and sends nothing. *Not written yet.*
5. **One-photo test.** Send one replace on a low-stakes photo, read it back, and check that the tags match and `verified` is still 2 or higher. If not, stop and restore from the backup. Record the result here and mark the claims above **[tested]**.
6. **Small batch, then the rest.** One group at a time, reading every photo back. Stop at the first failure.

## The spreadsheet

`Objects` (one row per tagged object): `PhotoID`, `Object_No` (position within the photo), `PhotoLink`, `Date`, the current OLM key, secondary, material and custom tag, then reference columns filled from the crosswalk (`MROLM local key`, `Notes`, `OLM data needs fixes`), then the change columns and `Batch_Status`.

Change-column rules:
- **Blank** keeps the current value.
- **`[remove]`** removes it.
- **Anything else** is the new value.

`Photo_Batch` (script-filled, one row per photo): `Batch_Label`, `Current_Tags_JSON` (the full backup), `Target_Tags_JSON`, `Batch_Status`, `Verified_Before`, `Verified_After`, `Done_At`, `Error_Or_Notes`.

`Batch_Status` values: pending, dry-run ok, sent, verified ok, failed, skipped.

## Guardrails

- Never send a photo without a saved backup of its current tags.
- One group at a time. Test one photo before any batch. Stop on the first failure.
- A replace is safe to retry, because it replaces everything rather than adding.
- Reuse the retry and wait pattern from `scripts/sync_data.py` to respect API limits.
- Credentials come only from environment variables in your own terminal, never a file. Never print raw photo records in logs.
- Raw exports contain coordinates and any address OLM holds. Keep them local and out of git.

## Open questions (update as they are answered)

- Is the account trusted, so that verified returns to 2 after a replace? **Not tested.**
- Can a photo be restored exactly from its backup? **Not tested.**
- Does `picked_up` survive a replay unchanged? **Not tested.**
- Are there API rate limits at 100 photos per page or on many replaces? **Unknown.**
- Do any photos sit at verification levels 3 to 5? **Check the export summary.**
