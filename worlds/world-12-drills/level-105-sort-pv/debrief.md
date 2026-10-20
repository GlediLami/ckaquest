# Drill: Sort by Capacity

## Pattern
`--sort-by` compares quantities correctly, so 500Mi sorts before 1Gi. Then filter with grep or a label selector.

## Exam angle
- "Sort PVs by capacity" and "sort pods by creation time" (`--sort-by=.metadata.creationTimestamp`) are classic.

Bookmark: https://kubernetes.io/docs/reference/kubectl/quick-reference/

Your notes: kubectl Cheat Sheet
