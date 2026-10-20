# Bad Upgrade

## What happened
Every install, upgrade and rollback is a numbered revision, stored as a Secret in the release namespace. A rollback creates a new revision that copies an old one.

## Commands to know
- `helm history <release>`
- `helm get values <release> --revision N` and `helm get manifest`
- `helm rollback <release> <revision>`. Without a revision it goes back one step.

## Exam angle
- "Roll back to the last working version" needs history first. The last working one is not always revision 1.
- `kubectl rollout undo` on the Deployment would fight Helm. Use Helm for Helm releases.

Bookmark: https://helm.sh/docs/helm/helm_rollback/

Your notes: Helm (course section 12)
