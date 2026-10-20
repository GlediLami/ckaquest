# Drill: What Is Not Running

## Pattern
Field selectors filter on the server. Pods support `status.phase`, `spec.nodeName`, `metadata.name`, `metadata.namespace` and a few more.

A pod in ImagePullBackOff has phase Pending. STATUS in `k get pods` is not the phase. It is a summary.

Bookmark: https://kubernetes.io/docs/concepts/overview/working-with-objects/field-selectors/

Your notes: kubectl Cheat Sheet, Application Failure
