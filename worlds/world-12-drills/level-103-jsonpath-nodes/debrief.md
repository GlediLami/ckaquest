# Drill: Node IPs

## Pattern
`{range .items[*]}<fields>{"\n"}{end}` is the template for one line per object. Filters `[?(@.key=="value")]` pick one element of a list.

## Exam angle
- The kubectl quick reference page has many JSONPath examples. Search it for "jsonpath".
- `-o wide` shows INTERNAL-IP too, but the task asks for an exact format.

Bookmark: https://kubernetes.io/docs/reference/kubectl/jsonpath/

Your notes: JSONPath
