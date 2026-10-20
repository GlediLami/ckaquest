# Install From a Repo

## What happened
A chart is a package of templates. A release is one installation of a chart in a namespace. Values fill the templates.

## Commands to know
- `helm repo add / update / list`
- `helm search repo <name> --versions`
- `helm show values <chart>` before you install
- `helm install <release> <chart> --version X -n <ns> [--create-namespace] --set k=v | -f values.yaml`
- `helm list -A` shows releases in all namespaces

## Exam angle
- Helm commands need `-n`. A release in the wrong namespace is a lost task.
- Pin `--version` when the task names one.

Bookmark: https://helm.sh/docs/helm/helm_install/

Your notes: Helm (course section 12)
