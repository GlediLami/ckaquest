# The Operator Cannot See

## What happened
RBAC rules match on API group plus resource. Core resources have group `""`. Custom resources have the CRD's group. A rule with the wrong group grants nothing, without any error.

## Facts to remember
- `--resource=<plural>.<group>` in `kubectl create clusterrole` sets the group for you.
- Subresources (`status`, `scale`, `log`, `exec`) need their own entry.
- An operator that watches all namespaces needs a ClusterRoleBinding.

## Exam angle
- Operators and CRDs are in the curriculum. Expect to install one from a manifest and fix its RBAC.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

Your notes: Custom Resources and Operators, Cluster Roles
