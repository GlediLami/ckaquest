# Solution

```bash
k edit cm nginx-tls -n tls-lab        # ssl_protocols TLSv1.2 TLSv1.3;
k rollout restart deploy/web -n tls-lab
k rollout status deploy/web -n tls-lab
k run t -n tls-lab --rm -it --image=curlimages/curl:8.11.1 --restart=Never -- \
  curl -k --tls-max 1.2 https://web.tls-lab
k patch cm nginx-tls -n tls-lab -p '{"immutable":true}'
```
