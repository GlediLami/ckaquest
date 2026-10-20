# Find the Old Release

## What happened
Releases live in namespaces. `helm list -A` is the only quick overview. Filter with grep or `--filter <regex>` on the release name.

## Exam angle
- "Delete all releases of chart X" or "the release in pending-install state" are common. `helm list -A -a` also shows failed and pending ones.
- `helm uninstall` needs the right `-n`.

Bookmark: https://helm.sh/docs/helm/helm_list/

Your notes: Helm (course section 12)
