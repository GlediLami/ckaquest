# The Pod That Will Not Die

## Mirror pods
A static pod is created by the kubelet from a file, not by the API server. The kubelet publishes a read-only copy, the mirror pod, so you can see it with kubectl. Its owner is the Node (`ownerReferences[0].kind: Node`) and its name ends with `-<nodename>`. Deleting the mirror pod does nothing. The kubelet recreates it from the file.

## Finding the static pod folder
1. `ps -ef | grep kubelet` shows `--config=/var/lib/kubelet/config.yaml`.
2. `grep staticPodPath /var/lib/kubelet/config.yaml`.
3. The folder can be anything. The exam likes to move it.

## Creating a static pod (common exam task)
`kubectl run x --image=nginx:1.27 $do > x.yaml`, copy it to the node, put it into the staticPodPath folder. The kubelet starts it. No kubectl apply needed.

## Your notes
- 5 Scheduling / Static Pods
- 2 Components / Worker Node / kubelet
