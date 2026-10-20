# Admission Control

## What happened
After authentication and authorization, every write request passes admission plugins. They can reject it (validating) or change it (mutating). NamespaceAutoProvision creates a missing namespace on the fly.

## Facts to remember
- Many plugins are on by default. `kube-apiserver -h | grep enable-admission-plugins` lists them. Run it inside the apiserver container with crictl exec, or read the docs.
- `--enable-admission-plugins` adds to the defaults. `--disable-admission-plugins` removes defaults.
- NamespaceExists and NamespaceLifecycle are related. NamespaceAutoProvision is off by default.

## Exam angle
- Edit the flag, keep the existing values, use commas, no spaces.
- A typo in a plugin name stops the API server. Check `crictl logs` if it does not come back.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/

Your notes: Admission Controllers
