# Solution

```bash
k logs deploy/report-gen -n reports
# User "system:serviceaccount:reports:report-sa" cannot list resource "configmaps"
k create role cm-reader -n reports --verb=get,list --resource=configmaps
k create rolebinding cm-reader-binding -n reports --role=cm-reader --serviceaccount=reports:report-sa
k logs deploy/report-gen -n reports -f
```
