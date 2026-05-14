You are syncing the Truss fork of `unit-python-sdk` with Unit's upstream API documentation.

## Before you do anything else

1. Read [.cursor/skills/sdk-guide/SKILL.md](.cursor/skills/sdk-guide/SKILL.md) and [.cursor/rules/python-sdk.mdc](.cursor/rules/python-sdk.mdc). These define the SDK architecture and conventions you must follow.
2. Idempotency gate. Run:

```bash
gh pr list --repo Truss-pmts/unit-python-sdk --state open --search 'in:title "Sync SDK DTOs with Unit API docs"'
```

If any open PR matches, exit immediately without changes — the previous run's PR is still being reviewed.
3. Fetch upstream for context only (do **not** gate on this — the Truss fork is intentionally divergent from `unit-finance/unit-python-sdk` and there are hundreds of unmerged upstream commits going back to 2022):

```bash
git fetch upstream master
```

Later, when building each per-resource PR body, run:

```bash
git log --since="30 days ago" --pretty=format:'%h %ad %s' --date=short HEAD..upstream/master -- unit/models/<file>.py
```

for the specific DTO file you edited. If anything shows up, include it under a "Recent upstream activity" section of the PR body so reviewers can decide whether to cherry-pick. Empty result → omit the section.

## Sources of truth (in priority order)

1. **Primary**: `https://docs.unit.co/resources` — the attribute tables (name, type, description, "Optional" suffix) define what Unit actually ships. This page covers resources only; events live at `https://docs.unit.co/events`. **Scope this automation to resources, not events** (events are touched by a separate workflow).
2. **Supplementary**: `unit-finance/openapi-unit-sdk` (default branch `main`). Use `gh api repos/unit-finance/openapi-unit-sdk/contents/schemas/<family>` to list and read structured schemas for exact types, enums, and nested object shapes.
3. **Conflict rule**: if a field is in the docs page but not in OpenAPI, trust the docs. If a field is in OpenAPI but not the docs, ignore it (Unit's spec sometimes drifts the other way too).

## SDK architecture you must respect

- DTOs live in `unit/models/*.py`. Each DTO stores its data in `self.attributes`, which is a **dict keyed by camelCase JSON API names** (e.g. `dto.attributes["declineReason"]`). `__init__` accepts snake_case kwargs and assembles `self.attributes` internally.
- Deserialization is `@staticmethod from_json_api(...)` (not `@classmethod`). Signatures vary by DTO — match the existing pattern in the file you're editing. Inside `from_json_api`, fetch optional fields with `attributes.get("camelCaseKey")`, not `attributes["camelCaseKey"]`.
- All construction uses **keyword arguments** per [.cursor/rules/keyword-arguments.mdc](.cursor/rules/keyword-arguments.mdc).
- New **top-level** JSON:API resource types (anything appearing as `{"data": {"type": "X"}}` in a response) require both a DTO file and a lambda entry in `unit/models/codecs.py` `mappings`.
- New **nested sub-objects** (e.g. `CardVerificationData`, `RichMerchantDataAddress`) get a class with `from_json_api` in `unit/models/__init__.py` (or alongside the parent DTO) and are deserialized by their parent. **Do not** add them to `codecs.py`.

## What to change (and what NOT to change)

For each resource type on the docs page, find the matching DTO and compare:

- **ADD** any missing field that the docs mark `Optional`: snake_case kwarg defaulted to `None` in `__init__`, camelCase entry in `self.attributes`, and `attributes.get(...)` in `from_json_api`. If the field type is a nested object that doesn't exist yet in `unit/models/`, create it as a sub-object class with its own `from_json_api` (no codec entry).
- **DO NOT** silently change anything else. For each of the following, leave the code alone and add the case to a "Manual review needed" section of the PR body:
  - Field present in code but absent from docs (possible removal)
  - Field rename (e.g. casing or wording change)
  - Type change (e.g. string → enum, int → string)
  - Required ↔ Optional flip (docs no longer mark Optional, or now does)
  - Any new **required** (non-Optional) field — flag as a breaking-change candidate

## One PR per run, one commit per resource (cloud-runner constraint)

The Cursor cloud-agent runner is locked to a single branch per agent run, so you cannot open N parallel PRs. Bundle all resource updates into a single PR with **one commit per resource** (clear commit messages so reviewers can split or revert per resource).

Cap each run at **5 resources**. If more resources have drift, list the remaining ones at the end of the PR body and queue them for the next scheduled run.

For each run with drift:

1. Create branch: `cursor/unit-sdk-docs-sync-<short-hash>` (the runner's default is fine).
2. For each resource (max 5), make the additive edits described above and commit them with the message `Sync <ResourceDTO> with Unit API docs` plus a body listing the added fields and the docs anchor URL.
3. Verify imports still resolve:

```bash
python -c "from unit.models.codecs import DtoDecoder, mappings; print(len(mappings))"
```

If it errors, fix the diff or abort the PR.
4. Open PR against `Truss-pmts/unit-python-sdk` base `master` as a **draft** (`gh pr create --draft`). The Mirror automation triggers on `Draft opened` and will open a paired draft PR in `Truss-pmts/api` so API CI runs against this SDK PR. A human reviews this PR, marks it ready, and merges; the merge fires Mirror Section B which promotes the paired api PR.

- **Title**: `Sync SDK DTOs with Unit API docs (automated, YYYY-MM-DD)`
- **Body**:

```markdown
## Summary

Automated sync against https://docs.unit.co/resources#<anchor>.

## Added fields

| Field | Type | Docs note |
|-------|------|-----------|
| ... | ... | ... |

## Manual review needed

<empty, or a list of renames/removals/type-changes/required-flips found>

## Backward compatibility

All additions are optional kwargs with `None` defaults; existing callers are unaffected.

## Recent upstream activity (last 30 days, optional)

<empty, or list of recent upstream commits touching this DTO's file — informational only, not auto-cherry-picked>

---

_Opened by the docs-sync automation. Paired API PR will be opened by automation 2._

```

If no drift is found across the whole docs page, exit silently — do nothing.

## Slack notification (only after PRs are opened)

Post a single message to `#software` tagging `@software` with:

- Summary line: `Unit SDK docs drift detected: N PR(s) opened, M resource(s) queued for next run.`
- Bullet list of PR titles + links.
- Bullet list of any "Manual review needed" items aggregated across the PRs.

(Automation 2 watches for `(automated, ` in the PR title and opens a paired draft PR in `Truss-pmts/api` against each one.)
