# Solution

```bash
k edit cm coredns -n kube-system
```

```
.:53 {
    errors
    health
    ready
    hosts {
       10.10.10.10 legacy.internal
       fallthrough
    }
    kubernetes cluster.local in-addr.arpa ip6.arpa {
    ...
```

```bash
k rollout restart deploy coredns -n kube-system
k run t --rm -it --image=busybox:1.36 -- nslookup legacy.internal
```
