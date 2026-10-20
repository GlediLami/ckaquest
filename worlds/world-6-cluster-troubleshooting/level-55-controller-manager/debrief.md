# Scale Does Nothing

## What happened
The controller manager pointed to a kubeconfig file that does not exist. It crashed on start. The API server still accepted the Deployment object, but no controller turned it into a ReplicaSet and pods.

## Which component does what
| Symptom | Suspect |
|---|---|
| Pods Pending, no events | kube-scheduler |
| Deployment exists, no ReplicaSet, scaling does nothing | kube-controller-manager |
| Node NotReady | kubelet or container runtime on that node |
| kubectl connection refused | kube-apiserver (or etcd behind it) |
| Service has no endpoints | selector mismatch, or controller manager (EndpointSlice controller) |
| Service IP does not answer, endpoints fine | kube-proxy |

## The kubeconfig files on a kubeadm control plane
`/etc/kubernetes/admin.conf`, `super-admin.conf`, `controller-manager.conf`, `scheduler.conf`, `kubelet.conf`. Each component uses its own identity. Know these names. The exam likes to break one of these paths.

## Your notes
- 14 Troubleshooting / Control Plane Failure
- 2 Components / Control Plane / kube-controller-manager
