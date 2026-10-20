# Solution

```bash
cd ~/ckaquest-work/61
cat <<EOF > csr.yaml
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: jane
spec:
  request: $(base64 -w0 < jane.csr)
  signerName: kubernetes.io/kube-apiserver-client
  usages: [client auth]
EOF
k apply -f csr.yaml
k certificate approve jane
k get csr jane -o jsonpath='{.status.certificate}' | base64 -d > jane.crt
k create role pod-reader -n dev-team --verb=get,list,watch --resource=pods
k create rolebinding jane-pod-reader -n dev-team --role=pod-reader --user=jane
k auth can-i list pods -n dev-team --as=jane    # yes
```
