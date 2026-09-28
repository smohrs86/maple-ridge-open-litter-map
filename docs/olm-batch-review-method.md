# Batch-fixing existing OpenLitterMap tags through the API

A reusable method for reviewing and correcting the tags on photos you have already uploaded and had verified in OpenLitterMap (OLM), in bulk, without using the website or app. Written so that a person, or another AI given this file, can follow it without any other context.

**Status: draft, updated 2026-09-28.** The raw export script, the review workbook builder and the dry-run script exist and have been run (all offline or read-only). Nothing has been written to OLM yet. The first batch (`alcohol/packaging`, 19 photos) has passed its dry run and is waiting for the one-photo test. Every claim is marked:
- **[source]** read from OLM's public code (`OpenLitterMap/openlittermap-web`, `master` branch, read 2026-09-26). Production could differ.
- **[tested]** confirmed against a real account. Read-only export results are marked **[tested: export]**. Update this file after each test.

## The problem

Legacy tags in OLM can be inconsistent (an object tagged with the wrong key, a custom tag that should be an object, and so on). Fixing thousands of objects one at a time in the app is not practical. OLM's API can rewrite tags, but a careless rewrite could lose data or drop photos from the public map.

## What OLM does when you rewrite tags

- **[source]** `PUT /api/v3/tags` replaces **all** tags on one photo you own. There is no per-tag edit endpoint. Changing one object means resending every tag on that photo. `POST /api/v3/tags` only appends and refuses a photo that already has tags.
- **[source]** The request carries no image. The photo file, location and date are untouched. Only tags are deleted and recreated, so tag-row IDs change.
- **[source]** Verification is reset to 0 and then re-applied in the same database transaction. If the account is trusted (`verification_required = false`) the photo returns to verified = 2 (admin approved), which is what OLM treats as public-ready. If the account is not trusted, the photo ends at 0 and leaves the public map. **Which case applies to an account must be tested, not assumed.**
- **[source]** Verification levels 3 to 5 (bounding boxes drawn or verified, AI-ready) appear to be reset to 2 by a replace. Check whether your photos have any.
- **[source]** OLM recalculates XP and its metrics for each replaced photo.
- **[source]** Ownership is checked, and already-verified photos are explicitly allowed.
- **[source]** The photo list (`GET /api/v3/user/photos`) accepts `per_page` up to 100 and returns each photo's `verified`, `picked_up`, coordinates and tags with OLM's internal IDs. **[tested: export]** `per_page=100` works: 2,491 photos came back in 25 pages plus one empty page, with no rate-limit errors. A second export the same day returned 2,680 photos, matching the photo count in the OLM app.
- **[tested: export]** In both real exports, `verified` was 0 on **every** photo, even though the photos display on the public map and the account behaves like a trusted uploader. So the list's `verified` value cannot be used alone to tell whether a photo is still visible. Why is unresolved (the list may report a different value than the one that controls display).
- **[source]** `picked_up` exists on the photo and on each tag. The list converts it to true or false, so a tag with no value is indistinguishable from "not picked up". **[tested: export]** The list does report real false values: in one account, 66 of 68 dog-waste tag rows read false (not picked up), so not-picked-up is preserved by the list. The account's default-picked-up setting was on. Whether a missing value can be told apart from false is still unknown, so check the counts before trusting a replay of `picked_up`. **[tested: export]** Not-picked-up set at upload carries through to the tags: the maintainer uploaded 189 photos with 23 items marked not picked up, and the next export showed 14 not-picked-up objects totalling exactly 23 items. No existing tag's value changed between the two exports. The photo-level value can disagree with its tags: 2 of those photos were picked up at photo level but held one not-picked-up object. **Use the per-tag value, never copy the photo-level value onto tags.**
- **[tested]** The OLM website's keyword search can't filter by a single key, but it is a usable cross-check. It matches the **item** name (so `dumping` finds `dumping/dumping` but not `dumping/other`, and `dogshit` finds both `dogshit` and `dogshit_in_bag`) and custom tags, and reports the number of photos and the total of **all** tags on them (litter quantities plus materials, brands, and custom tags). Predicting those two numbers from an export and comparing them with the website confirmed the export exactly on 2026-09-26.
- **[source]** OLM's tag list (`GET /api/tags/all`) gives the IDs for each category, object, type, material and brand. A replace request needs those IDs (`category_litter_object_id`, `litter_object_type_id`). Custom tags are plain text.
- **[source]** The replace body (`ReplacePhotoTagsRequest`, `AddTagsToPhotoAction::createTagFromClo`) is `{"photo_id": N, "tags": [...]}`, one entry per object: `category_litter_object_id`, `litter_object_type_id` (null or a type valid for that key in `category_object_types`), `quantity`, `picked_up` (true, false or null), `materials` (list of material IDs), `brands` (list of `{"id", "quantity"}`) and `custom_tags` (list of plain text, created if new). An empty `tags` list clears the photo, so never send one. Custom tags with no object (orphans) use a different, legacy format and are not handled yet.
- **[tested: export]** Each photo's `summary.tags` is OLM's own compact copy of its tags. Brands appear there as `{"<brand id>": quantity}` (sometimes a single dict rather than a list). Rebuilding the replace body from `new_tags` and comparing it with the summary matched exactly on 2,679 of 2,680 photos (2026-09-26 export), so a replay of unchanged tags is exact. The one mismatch, photo 552998, has an object whose tag says picked up while the summary says not picked up; the maintainer confirmed the litter was picked up, so **the per-tag value is right and the summary can be stale**. A replace regenerates the summary.

## The method

1. **Export (read-only).** `scripts/export_raw_olm.py` reads every photo and OLM's tag list into `review/raw/` (untracked, owner-only). This is the backup. It also prints counts only (verified values, `picked_up` values) that are safe to share. Credentials come from the `OLM_EMAIL` / `OLM_PASSWORD` environment variables, or else a local, untracked, owner-only credentials file (email on line 1, password on line 2).
2. **Build the review workbook.** `scripts/build_review_workbook.py` reads the newest raw export and `config/crosswalk.csv` (no login, no network) and writes a new dated workbook in `review/`: one row per tagged object (`Objects`), one row per photo (`Photo_Batch`), dropdown values (`Lists`) and a `Guide`. Each object gets a status (OK, REVIEW, RECLASS, UNCLASS, ORPHAN TAG, UNMAPPED) from the matching rules in `scripts/crosswalk.py`, which follow the README's matching rules and have unit tests (`python3 -m unittest discover -s tests`). It never overwrites an existing workbook. After a fresh export, rebuild with `--carry-from <previous workbook>` to keep your edits; they are matched by OLM's tag ID, and any edit whose tag no longer exists is reported, not dropped silently. **[tested: export]** The first build reproduced the maintainer's earlier snapshot exactly for total objects, OK, orphan tags, UNMAPPED and UNCLASS. REVIEW and RECLASS differed by 22, which is the count of `alcohol/packaging` objects; by the README's rules they are REVIEW because their crosswalk row is included and carries a fix note. **[tested: export]** A same-day rebuild from a second export worked with `--out review/legacy_tag_review_<date>b.xlsx --carry-from <previous workbook>`: a second build on the same day needs its own `--out` name, because the default name is dated and existing files are never overwritten.
3. **Review one group at a time.** Filter by current OLM key (and custom tag) to isolate a group, look at the photos, and type the fix in the `Change_to_…` cells. Note that REVIEW is decided by the object's **key**, not by when or how carefully it was tagged. A new photo tagged correctly under the current protocol still shows REVIEW if its key's crosswalk row carries a fix note, so the REVIEW count can rise after an upload even when nothing new is wrong. Filter by `Date` to separate legacy objects from new ones.
4. **Dry run.** `scripts/olm_batch_replace.py --workbook <workbook> --label <group>` is offline and has no send option. For every photo with a filled `Change_to_…` cell it rebuilds the full replacement tag list from the newest raw export, checks it against OLM's summary, applies the edits (matched by OLM tag ID), and blocks the photo if a key, type or material is unknown, a type is invalid for the new key, a quantity or `picked_up` would change, an edited tag is gone, or the photo has an orphan custom tag. It prints before and after for each object with the crosswalk layer the changed object would land in, and saves the backup and target request bodies to `review/batches/<label>_dryrun_<time>.json` (owner-only). Always re-export and rebuild the workbook just before a send, so the replacement is built from current tags. **[tested: export]** `alcohol/packaging`, 2026-09-28: 19 photos ready, 0 blocked, on both the old and a fresh export.
5. **One-photo test.** Send one replace on a low-stakes photo, read it back, and check that the tags match and that the photo is still shown publicly. Because the list's `verified` read 0 for every photo in the first export, compare `verified` before and after, and also confirm visibility another way (for example the public map). If anything is lost or hidden, stop and restore from the backup. Record the result here and mark the claims above **[tested]**.
6. **Small batch, then the rest.** One group at a time, reading every photo back. Stop at the first failure.

## Quick start for a new session

After the maintainer says they have finished editing a group in their review copy of the workbook:
1. Ask where the OLM credentials are for this session (don't go looking for them).
2. `python3 scripts/export_raw_olm.py --credentials-file <path>` (read-only).
3. `python3 scripts/build_review_workbook.py --carry-from "<their review copy>"` (check "Carried over N of N").
4. `python3 scripts/olm_batch_replace.py --workbook review/legacy_tag_review_<date>.xlsx --label <group>`.
5. Report the result, any unedited objects left under the group's key (ask whether they are correct as is), and any new objects under that key uploaded since the last export.
6. Send nothing until the maintainer has seen the dry run and explicitly says to send.

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
- Credentials come from environment variables in your own terminal, or from one local file that is untracked, owner-only and refused if other users can read it. Never commit them and never print them. Never print raw photo records in logs.
- Raw exports contain coordinates and any address OLM holds. Keep them local and out of git.

## Open questions (update as they are answered)

- Is the account trusted, so that verified returns to 2 after a replace? **Not tested.** The export showed `verified` = 0 on all photos, which does not match the account behaviour, so the test must compare before and after rather than expect 2.
- Can a photo be restored exactly from its backup? **Not tested.**
- Does `picked_up` survive a replay unchanged? **Not tested.** Not-picked-up values do read correctly from the list. The dry run sends each tag's own value and blocks any change.
- When a new photo appears under a key being reclassed, is it a mistake? Not necessarily: REVIEW is by key, so correctly tagged objects under that key still show REVIEW (see step 3). Ask the maintainer.
- Are there API rate limits on many replaces? **Unknown.** Reading at 100 per page showed none.
- Do any photos sit at verification levels 3 to 5? **No** in both exports: every photo read 0.
