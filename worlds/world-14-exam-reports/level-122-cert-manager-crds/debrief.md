# Read the Operator's Manual

## What happened
An operator is a controller plus CRDs. The CRDs carry an OpenAPI schema, so `kubectl explain` documents custom resources exactly like built-in ones.

## Useful commands
- `k get crd | grep <name>`: the types an operator adds.
- `k api-resources --api-group=cert-manager.io`: short names and scope.
- `k explain <kind>.<field> --recursive`: the whole tree of a field.

## Exam angle
- Reported as "list the cert-manager CRDs to a file, save the explain output of Certificate spec.subject".
- Save exactly what kubectl prints. No editing, no extra lines.

Bookmark: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_explain/

Your notes: CRDs and Operators
