# Render, Don't Install

## What happened
`helm template` runs the templates locally and prints YAML. Nothing reaches the cluster, no release is stored.

## Related
- `helm install --dry-run=client` does nearly the same but goes through the install path.
- `helm get manifest <release>` shows what an installed release rendered.

## Exam angle
- Useful to answer "what image would this chart deploy" without installing.

Bookmark: https://helm.sh/docs/helm/helm_template/

Your notes: Helm (course section 12)
