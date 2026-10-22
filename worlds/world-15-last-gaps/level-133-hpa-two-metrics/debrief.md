# Scale on Two Signals

## What happened
With several metrics the HPA computes a desired replica count for each one and takes the **highest**. So either signal alone can scale the Deployment up.

## Target types
- `Utilization`: percent of the pod's **request**. Only for `Resource` metrics, and the containers need requests.
- `AverageValue`: an absolute value per pod, like `50Mi` or `200m`.
- `Value`: one absolute value for the whole target. Used with `Object` and `External` metrics.

## Metric sources
- `Resource` (cpu, memory): from metrics-server.
- `ContainerResource`: one container of the pod, ignores sidecars.
- `Pods`, `Object`, `External`: custom metrics. They need an adapter such as prometheus-adapter or KEDA. Without one the HPA shows `<unknown>`.

## Exam angle
- `k autoscale` writes CPU only. Know the v2 YAML for memory and for a second metric.

Bookmark: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/

Your notes: Autoscaling
