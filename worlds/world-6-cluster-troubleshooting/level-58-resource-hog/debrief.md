# Who Is Eating the CPU?

## kubectl top
- Needs metrics-server. Without it you get `Metrics API not available`.
- `kubectl top pod -A --sort-by=cpu` and `--sort-by=memory`. `--containers` splits by container.
- `kubectl top node --sort-by=cpu`.
- Exam tasks often say "write the name to a file". Use `--no-headers`, `head -1`, `awk '{print $1}'`. Then `cat` the file to check it.

## In-place pod resize (GA in v1.35)
- Before 1.35: resources of a running pod were immutable. You had to recreate the pod.
- Now: `kubectl patch pod <p> --subresource resize -p '...'` or `kubectl edit pod <p> --subresource resize`.
- `spec.containers[].resources` is what you asked for. `status.containerStatuses[].resources` is what the container really has now.
- `resizePolicy` per resource decides if the container must restart (`RestartContainer`) or not (`NotRequired`, default for CPU).
- You cannot change the QoS class with a resize. That is why the pod already had requests and limits.

## Your notes
- 6 Logging & Monitoring / Monitoring
- 7 App Lifecycle / In-Place Pod Resize
- 5 Scheduling / Resource Requirements
