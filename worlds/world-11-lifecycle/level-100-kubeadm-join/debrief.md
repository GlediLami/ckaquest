# Add a Worker

## What happened
`kubeadm join` uses the token to authenticate, checks the CA hash, gets a kubelet client certificate through the CSR API (auto-approved for bootstrap tokens), and starts the kubelet. The CNI DaemonSet then lands on the new node and it turns Ready.

You built a whole cluster by hand in this world: node prep, init, CNI, join.

## Exam angle
- If the join token expired, create a new one. Do not re-run `kubeadm init`.
- A failed join leaves files behind. `kubeadm reset` on the worker cleans up before a retry.

Bookmark: https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/

Your notes: Cluster Install (course section 11)
