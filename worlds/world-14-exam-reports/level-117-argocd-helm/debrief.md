# Argo CD Without Its CRDs

## What happened
Many charts ship CRDs and have a switch to leave them out, here `crds.install`. Teams turn it off when CRDs are managed separately, for example so an uninstall can never delete every Application.

Helm refuses to take over objects it did not create. With CRDs on, the install fails because the CRDs exist without Helm's ownership labels.

## Patterns
- `helm show values <chart> --version <v>`: find the switch.
- `helm template ... -n <ns> > file`: render, review, or hand to GitOps.
- `helm install` with the same `--version` and `--set`.
- `helm get values <release> -n <ns>`: what a release was installed with.

## Exam angle
- People report this exact task with Argo CD: add repo, template without CRDs to a file, install.
- Always pass `--version` and `-n`. The task usually checks both.

Bookmark: https://helm.sh/docs/helm/helm_template/

Your notes: Helm Basics
