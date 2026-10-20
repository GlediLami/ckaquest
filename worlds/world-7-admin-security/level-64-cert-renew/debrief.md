# Certificate Renewal

## What happened
kubeadm certificates last one year. `kubeadm upgrade` renews them, so clusters that are upgraded often never expire. Otherwise you renew by hand.

`kubeadm certs renew` only writes new files. Static pods read their certs at start, so you must restart them.

## Restarting a static pod
There is no `kubectl rollout restart` for static pods. Deleting the mirror pod does nothing. Move the manifest out of the manifests folder, wait for the kubelet to stop the container, move it back.

## Exam angle
- `kubeadm certs check-expiration` is the fastest overview.
- `openssl x509 -in <crt> -noout -text` shows issuer, SANs and dates. `-enddate` only the expiry.
- Cert files live in `/etc/kubernetes/pki/`. The etcd ones in `/etc/kubernetes/pki/etcd/`.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/

Your notes: TLS in Kubernetes, Cluster Upgrade
