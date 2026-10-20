# Solution

```bash
helm history blog -n helm-blog
helm get values blog -n helm-blog --revision 3      # image.tag: 1.28-alpine-broken
helm rollback blog 2 -n helm-blog
k get pods -n helm-blog
```
