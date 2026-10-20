# Debrief

An HPA with `type: Utilization` needs a CPU request on every container of the target pods. Without it the HPA shows `<unknown>` and ScalingActive is False.

Other reasons for `<unknown>`:
- metrics-server is missing or broken. Check with `k top pods`.
- The pods just started. Metrics need up to a minute.
- The HPA points at the wrong Deployment name.

Exam angle: you may be asked to create an HPA with `k autoscale deploy NAME --cpu-percent=50 --min=1 --max=5`. Check that the pods have requests, or the HPA will never work.

Your notes: HPA, Resource Requests and Limits, Metrics Server
