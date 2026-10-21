# The Disk Is Too Small

## What happened
The API refused the bigger request: "only dynamically provisioned pvc can be resized and the storageclass that provisions the pvc must support resize". The StorageClass decides, through `allowVolumeExpansion: true`. It is one of the few StorageClass fields you can change after creation.

## What happens next on a real driver
1. You raise `spec.resources.requests.storage` on the PVC. You can only grow it, never shrink it.
2. The CSI external-resizer grows the volume in the storage backend.
3. The kubelet grows the filesystem. Some drivers need the pod restarted for that step. The PVC then shows the condition `FileSystemResizePending`.
4. `status.capacity` shows the new size.

The local-path provisioner in this cluster cannot resize anything. So here `status.capacity` stays 1Gi while the request is 2Gi. The API part, which the exam checks, is done.

## Exam angle
- "Expand the PVC" means edit the PVC, not the PV.
- If it is refused, check `allowVolumeExpansion` on the StorageClass.
- `k get pvc` CAPACITY shows status, not the request. Check the spec with `-o yaml`.

Bookmark: https://kubernetes.io/docs/concepts/storage/persistent-volumes/#expanding-persistent-volumes-claims

Your notes: Storage
