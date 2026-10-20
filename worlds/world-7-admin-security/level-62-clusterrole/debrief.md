# Nodes Are Cluster-Wide

## What happened
Nodes, PersistentVolumes, StorageClasses, ClusterRoles and namespaces themselves are cluster-scoped. Only a ClusterRole can grant access to them, and only a ClusterRoleBinding makes that grant cluster-wide.

## The four combinations
- Role + RoleBinding: namespaced resources, one namespace.
- ClusterRole + RoleBinding: reuse one ClusterRole, but only inside the RoleBinding's namespace.
- ClusterRole + ClusterRoleBinding: everywhere, including cluster-scoped resources.
- Role + ClusterRoleBinding: not possible.

## Exam angle
- `--serviceaccount=<ns>:<name>` is the format. A missing namespace is a common mistake.
- `k api-resources --namespaced=false` lists what needs a ClusterRole.
- Test as the SA: `--as=system:serviceaccount:<ns>:<name>`.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

Your notes: Cluster Roles, RBAC, Service Accounts
