# Your Own Resource Type

## What happened
A CRD teaches the API server a new resource. After that, kubectl works with it like any built-in type: get, describe, explain, RBAC. The openAPIV3Schema validates what you store.

## Exam angle
- `k get crd`, `k api-resources --api-group=<group>`, `k explain <kind>.spec` are your tools.
- A CRD alone does nothing. A controller (operator) watches the objects and acts. Next level.
- A cron string with `*` must be quoted in YAML.

Bookmark: https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/

Your notes: Custom Resources and Operators
