# Feature Tracking Rules

All features are tracked in [`feature-list.json`](../feature-list.json) in the project root.

---

## Adding a Feature

- Add every new functionality to `feature-list.json` **before** starting implementation
- Include: `id` (kebab-case), `name`, `description`, `status: "planned"`, `phase`, `location`, `dependencies`
- The `id` becomes the canonical reference for the feature across the project

---

## Marking a Feature as Done

A feature is `implemented` when ALL of the following are true:

- [ ] Code exists at the specified `location`
- [ ] All listed `dependencies` are installed and working
- [ ] The feature passes its own basic validation (run or test)
- [ ] `status` is changed from `"planned"` to `"implemented"`
- [ ] `phase` reflects the current/actual phase (may differ from original plan)

---

## Feature Schema

```json
{
  "id": "feature-name",
  "name": "Feature Name",
  "description": "1-2 sentences on what it does",
  "status": "planned|implemented|in_progress",
  "phase": "1" | "1-3" | "13-18",
  "location": "src/path/",
  "dependencies": ["package"]
}
```

### Field Descriptions

| Field        | Required | Description                                              |
|--------------|----------|----------------------------------------------------------|
| `id`         | Yes      | Unique kebab-case identifier, used in references         |
| `name`       | Yes      | Human-readable feature title                             |
| `description`| Yes      | Brief explanation of what the feature does               |
| `status`     | Yes      | `planned` → `in_progress` → `implemented` → `deprecated`|
| `phase`      | Yes      | Learning path phase (e.g., `"1"`, `"8-12"`, `"13-18"`)   |
| `location`   | Yes      | File path or directory where code lives                   |
| `dependencies`| No     | External packages required to run this feature            |

---

## Status Transitions

```
planned ──► in_progress ──► implemented
                        └──► deprecated (if superseded)
```

- `planned` — Feature is defined but no work has started
- `in_progress` — Development is underway
- `implemented` — Feature is complete and working
- `deprecated` — Feature is obsolete (add note to description)

---

## When to Update

- Set `status: "in_progress"` when development begins
- Set `status: "implemented"` and finalize `phase` when all done criteria are met
- Never remove features from the JSON — mark obsolete ones with `status: "deprecated"` and a note in the description

---

## Feature Naming Conventions

- `id`: lowercase kebab-case (e.g., `sec-filing-extractor`, `graphrag`)
- `name`: Title Case with spaces (e.g., "SEC Filing Extractor", "GraphRAG")
- `location`: relative path from project root (e.g., `src/ingestion/`, `streamlit_app/app.py`)

---

## Valid Statuses

| Status        | Meaning                                      |
|---------------|----------------------------------------------|
| `planned`    | Feature is defined but not started            |
| `in_progress` | Feature is currently being developed         |
| `implemented` | Feature is complete and working               |
| `deprecated`  | Feature is superseded — do not use            |