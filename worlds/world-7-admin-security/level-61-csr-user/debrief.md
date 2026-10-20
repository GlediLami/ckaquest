# A New User Called Jane

## What happened
Kubernetes has no user objects. A user is whoever presents a client certificate signed by the cluster CA. The CN becomes the user name and each O becomes a group.

The CSR API lets an admin sign such a certificate without touching the CA key files.

## Steps to know by heart
1. `openssl genrsa` and `openssl req -subj "/CN=jane/O=dev"` (often already done for you in the exam).
2. CSR object with `signerName: kubernetes.io/kube-apiserver-client` and `usages: [client auth]`.
3. `k certificate approve jane`.
4. Pull the cert from `.status.certificate` and base64-decode it.
5. RBAC for the user. Without it, jane can log in but do nothing.

## Exam angle
- The CSR is often given as a file. `base64 -w0` keeps it on one line. Without `-w0` the YAML breaks.
- Check your work with `k auth can-i ... --as=jane`. You do not need a kubeconfig for jane to prove RBAC.
- `k certificate deny` exists too.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/#normal-user

Your notes: Certificates API, RBAC, TLS in Kubernetes
