# 403 From Inside the Pod

## What happened
Every pod runs as a ServiceAccount (`default` if none is set). Its token is mounted at `/var/run/secrets/kubernetes.io/serviceaccount/`. RBAC decides what that identity may do. A new ServiceAccount may do nothing.

## Read the error
`User "system:serviceaccount:reports:report-sa" cannot list resource "configmaps" in API group "" in the namespace "reports"` tells you the who, the verb, the resource, the API group and the namespace. That is all you need for the Role.

## Exam angle
- Grant the least: the verbs and resources from the error, no more.
- `k get deploy report-gen -o jsonpath='{.spec.template.spec.serviceAccountName}'` finds the SA.
- `automountServiceAccountToken: false` stops the token mount when a pod does not need the API.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

Your notes: Service Accounts, RBAC
