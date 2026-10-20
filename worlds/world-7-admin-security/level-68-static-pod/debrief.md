# A Pod Without the API

## What happened
The kubelet runs every manifest in its `staticPodPath`, without the scheduler or the API server. It then creates a read-only mirror pod in the API so you can see it. The name gets `-<node name>` appended.

## Facts to remember
- Delete the file to delete the pod. `k delete pod` only removes the mirror, which comes back.
- Static pods cannot use ServiceAccounts, ConfigMaps or Secrets from the API.
- The control plane of a kubeadm cluster is static pods: etcd, apiserver, controller-manager, scheduler.

## Exam angle
- Generate YAML with `k run ... $do` on your terminal, then paste it on the node.
- Always check `staticPodPath` in `/var/lib/kubelet/config.yaml`. A task may have changed it.
- `ps aux | grep kubelet` shows which config file the kubelet uses.

Bookmark: https://kubernetes.io/docs/tasks/configure-pod-container/static-pod/

Your notes: Static Pods
