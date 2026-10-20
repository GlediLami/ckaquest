#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
W="$CQ_WORK/61"
cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: jane
spec:
  request: $(base64 -w0 < "$W/jane.csr")
  signerName: kubernetes.io/kube-apiserver-client
  usages: [client auth]
EOF
kubectl certificate approve jane
cq_wait 30 bash -c '[ -n "$(kubectl get csr jane -o jsonpath={.status.certificate})" ]'
kubectl get csr jane -o jsonpath='{.status.certificate}' | base64 -d > "$W/jane.crt"
kubectl create role pod-reader -n dev-team --verb=get,list,watch --resource=pods
kubectl create rolebinding jane-pod-reader -n dev-team --role=pod-reader --user=jane
