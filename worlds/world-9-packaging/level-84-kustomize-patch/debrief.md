# Patch It In

## What happened
Strategic merge patches merge lists by key. Containers merge by `name`, so the patch only needs `name: web` and the new fields.

`configMapGenerator` adds a content hash to the name. When the data changes, the name changes and the Deployment rolls out. That is the main reason to use it.

## Patch types
- Strategic merge (a partial object) for most changes.
- JSON 6902 (`op: replace, path: /spec/...`) for exact edits, also on CRDs.
- Both go under `patches:`. `patchesStrategicMerge` is the old field name.

## Exam angle
- Build first with `k kustomize`, read it, then apply.

Bookmark: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/

Your notes: Kustomize (course section 13)
