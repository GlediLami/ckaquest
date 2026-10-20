# A New Default

## What happened
A PVC without `storageClassName` gets the default class at creation. If two classes are default, the newest wins, which is confusing. Keep exactly one.

`storageClassName: ""` (empty string) is different: it means "no class, bind to a pre-created PV only".

## Exam angle
- `k get sc` shows `(default)` next to the name.
- StorageClass fields cannot be edited after creation, except annotations and labels. Delete and recreate to change them.
- Retain keeps the PV and its data after the PVC is deleted. Delete removes both.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/change-default-storage-class/

Your notes: Storage
