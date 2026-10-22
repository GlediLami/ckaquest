# Roles That Grow by Themselves

## What happened
An aggregated ClusterRole has an `aggregationRule` instead of its own rules. A controller in kube-controller-manager watches for ClusterRoles that match the label selector and copies their rules into the aggregated role. Add a new labeled role later and everyone bound to the aggregate gets it at once.

## Where you have seen this
The built-in `admin`, `edit` and `view` roles are aggregated. A CRD author adds `rbac.authorization.k8s.io/aggregate-to-view: "true"` to a ClusterRole, and every user with `view` can read the new resource.

## Gotchas
- Rules you write by hand into an aggregated role are overwritten by the controller.
- `k auth can-i ... --as=system:serviceaccount:<ns>:<name>` checks a ServiceAccount.

## Exam angle
- Know `aggregationRule` and the `aggregate-to-*` labels. Creating the parts imperatively and labeling them afterwards is fastest.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#aggregated-clusterroles

Your notes: RBAC
