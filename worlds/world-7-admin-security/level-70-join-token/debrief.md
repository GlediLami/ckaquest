# A Ticket to Join

## What happened
`kubeadm join` needs a bootstrap token (who may join) and the CA cert hash (proof the worker talks to the right cluster). The token from `kubeadm init` expires after 24 hours.

## Commands
- `kubeadm token create --print-join-command` makes a new token and prints the whole command.
- `kubeadm token list`, `kubeadm token delete <token>`.
- The hash by hand: `openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | openssl dgst -sha256 -hex`.

## Exam angle
- Adding a node is part of the curriculum. Run the printed command on the new node as root.
- `--ttl 0` means the token never expires. Avoid it.

Bookmark: https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-token/

Your notes: Cluster Upgrade, Control Plane
