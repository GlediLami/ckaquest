# A Reader Next to the Writer

## What happened
`kubectl logs` only shows what a container writes to stdout and stderr. An app that logs to a file is invisible. A second container in the same pod can read that file through a shared volume and print it to its own stdout.

## Two ways
- Plain second container (this level, and what the reported task asked): starts together with the app, no order.
- Native sidecar (level 87): an init container with `restartPolicy: Always`. Starts first and does not block Jobs from finishing.

Read the task. "Add a container named sidecar" means a normal container. "A sidecar that starts first" means the native one.

## Exam angle
- Reported: "update a Deployment with a co-located container that runs tail -f on the shared log". Candidates say early `tail` errors in the logs are a trick, ignore them if the pod runs.

Bookmark: https://kubernetes.io/docs/concepts/cluster-administration/logging/

Your notes: Multi-Container Pods
