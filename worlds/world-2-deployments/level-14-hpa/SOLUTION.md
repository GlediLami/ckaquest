# Solution for Level 14: HPA Can't Scale

## The Problem
The HorizontalPodAutoscaler (HPA) cannot scale because metrics-server is not installed in the cluster.

## The Solution

### Option 1: Install metrics-server using kubectl
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# For kind/minikube, you may need to add --kubelet-insecure-tls flag:
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

### Option 2: For kind clusters (recommended)
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch -n kube-system deployment metrics-server --type=json -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

### Option 3: Using Helm
```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system
```

## Verification

Wait for metrics-server to be ready:
```bash
kubectl wait --for=condition=ready pod -l k8s-app=metrics-server -n kube-system --timeout=60s
```

Check if metrics are available:
```bash
kubectl top nodes
kubectl top pods -n k8squest
```

Check HPA status:
```bash
kubectl get hpa web-backend-hpa -n k8squest
```

The HPA should now show CPU metrics and be able to scale!

## Expected Result
- metrics-server pods running in kube-system namespace
- `kubectl top` commands work
- HPA shows current/target CPU metrics
- HPA can scale the deployment based on load
