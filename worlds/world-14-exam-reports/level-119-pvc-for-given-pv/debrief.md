# The Database Wants Its Old Disk

## What happened
A PVC binds to a PV when class, access mode and size fit. Leave out `storageClassName` and the PVC gets the default class. Then the provisioner creates a new, empty volume and your data stays on the old PV.

`volumeName` names the PV directly. `storageClassName` must still match the PV's class. The class does not have to exist as an object for static binding.

## Retain
`persistentVolumeReclaimPolicy: Retain` keeps the data after the claim is deleted. The PV then shows `Released` and does not bind again until you remove `spec.claimRef`.

## Exam angle
- Reported as "MariaDB with persistent storage": PVC for a given PV, then edit a Deployment file.
- `k get pv` first. Copy class, mode and size exactly.

Bookmark: https://kubernetes.io/docs/concepts/storage/persistent-volumes/#binding

Your notes: Storage
