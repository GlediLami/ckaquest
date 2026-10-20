# Right-Size the Pods

## What happened
VPA recommends requests from observed usage. Modes:
- `Off`: only recommendations in `.status`.
- `Initial`: applies on pod creation only.
- `Recreate`: evicts pods to apply new values.
- `InPlaceOrRecreate`: uses in-place resize where it can (new with in-place pod resize).

## Exam angle
- VPA is an add-on, not built in. The exam may have it installed and ask for a manifest.
- `"Off"` must be quoted in YAML.
- Do not run HPA on CPU and VPA on CPU for the same Deployment. They fight.

Bookmark: https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/

Your notes: Vertical Pod Autoscaler
