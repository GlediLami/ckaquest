# A Production Overlay

## What happened
Kustomize builds YAML from a base plus overlays, without templates. Common changes have their own fields. Everything else is a patch (next level).

## Commands
- `kubectl kustomize <dir>` prints the result.
- `kubectl apply -k <dir>` applies it. `kubectl delete -k <dir>` removes it.

## Exam angle
- Know the built-in fields: `namespace`, `namePrefix`, `nameSuffix`, `labels` (or `commonLabels`), `images`, `replicas`, `configMapGenerator`, `patches`.
- `-k` takes a folder, not a file.

Bookmark: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/

Your notes: Kustomize (course section 13)
