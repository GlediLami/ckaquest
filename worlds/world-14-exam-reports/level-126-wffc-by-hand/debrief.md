# Bound Only When Needed

## What happened
With `Immediate` binding, a PVC binds as soon as a fitting PV exists. For node-local storage that can be wrong: the PV is on node02, but the pod might need to run elsewhere.

`WaitForFirstConsumer` delays binding until a pod using the PVC is scheduled. The scheduler then picks a node that fits both the pod and the PV's `nodeAffinity`. Until then the PVC is Pending with the event "waiting for first consumer to be created before binding".

## Local volumes
- `provisioner: kubernetes.io/no-provisioner`: nothing creates PVs, you do.
- `local.path` must exist on the node.
- `nodeAffinity` is required. It tells the scheduler where the disk is.

## Exam angle
- Reported: "create SC with WaitForFirstConsumer, PV and PVC, observe Pending, create a pod, verify Bound".
- Pending here is not a bug. Read the PVC events before you change anything.

Bookmark: https://kubernetes.io/docs/concepts/storage/storage-classes/#local

Your notes: Storage
