# Room for More Control Planes

## What happened
A highly available control plane is several control plane nodes behind one stable address. In production that address is a load balancer or a virtual IP. Here it is a name in `/etc/hosts`.

`--control-plane-endpoint` writes that name into every kubeconfig and into the API server certificate. You cannot add it later without regenerating certificates. That is why it has to be there from the first `kubeadm init`.

`--upload-certs` puts the CA and other shared keys into the Secret `kubeadm-certs`, encrypted with the certificate key. A joining control plane node downloads them with `--certificate-key`. The Secret is deleted after 2 hours. `kubeadm init phase upload-certs --upload-certs` uploads them again with a new key.

## Two join commands
- Worker: `kubeadm join <endpoint> --token ... --discovery-token-ca-cert-hash ...`
- Control plane: the same plus `--control-plane --certificate-key <key>`

## Stacked or external etcd
- Stacked: etcd runs on each control plane node. This is the kubeadm default. Use 3 control plane nodes for quorum.
- External: etcd runs on its own hosts. You need more machines, but losing a control plane node does not cost an etcd member.

## Exam angle
- The exam cannot give you three machines and a load balancer. Expect questions about the flags, the join command and the endpoint.
- Search "high availability" in the docs. The kubeadm HA page has every command.

Bookmark: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/

Your notes: Cluster Install (course sections 10 and 11)
