#!/usr/bin/env bash
# Offline proof: build a cluster whose nodes cannot reach the internet, load the offline pack,
# and run a few levels through the harness. Needs "bin/cq-offline prepare" first.
#
#   tests/offline-check.sh [level filter ...]     default: a small mixed set
#
# It uses its own cluster name and kubeconfig, so the normal ckaquest cluster is not touched.
# Stop the normal cluster first if RAM is tight (about 1.2 GB each).
set -uo pipefail
source "$(dirname "$0")/../lib/common.sh"
NAME=ckaquest-offline
export CKAQUEST_KUBECONFIG="$CQ_HOME/kubeconfig-offline"
export KUBECONFIG="$CKAQUEST_KUBECONFIG"
FILTERS=("${@:-level-1-pods level-23-dns level-65-etcd-backup level-83-kustomize-overlay}")

[ -d "$CQ_HOME/offline/images" ] || { echo "no offline pack: run bin/cq-offline prepare first"; exit 1; }
echo "==> cluster $NAME"
img="$(grep -m1 -oE 'kindest/node:[^ ]+' "$CQ_ROOT/cluster/kind-config.yaml")"
ver="$(echo "$img" | sed -E 's/.*:(v[0-9.]+).*/\1/')"
docker image inspect "ckaquest-node:$ver" >/dev/null 2>&1 || { echo "no ckaquest-node:$ver image: run bin/cq-offline prepare"; exit 1; }
sed "s|$img|ckaquest-node:$ver|" "$CQ_ROOT/cluster/kind-config.yaml" > "$CQ_HOME/kind-config-offline.yaml"
"$CQ_KIND" create cluster --name "$NAME" \
  --config "$CQ_HOME/kind-config-offline.yaml" --kubeconfig "$KUBECONFIG" --wait 180s || exit 1
for node in $("$CQ_KIND" get nodes --name "$NAME"); do
  role=worker; [[ "$node" == *control-plane ]] && role=controlplane
  docker cp "$CQ_ROOT/cluster/node-bootstrap.sh" "$node:/root/.cq-node-bootstrap.sh"
  docker exec "$node" bash /root/.cq-node-bootstrap.sh "$role" || echo "bootstrap failed on $node"
done

# A Docker --internal network breaks kind's DNS setup, so cut the internet inside each node instead:
# only private ranges (nodes, pods, services, Docker DNS) stay reachable.
echo "==> cutting the internet on every node"
for node in $("$CQ_KIND" get nodes --name "$NAME"); do
  docker exec "$node" bash -c '
for chain in OUTPUT FORWARD; do
  iptables -I $chain 1 -j REJECT
  for net in 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16 127.0.0.0/8; do iptables -I $chain 1 -d $net -j ACCEPT; done
done'
done

echo "==> proof that nodes have no internet"
if docker exec "$NAME-control-plane" curl -s -m 5 https://registry.k8s.io >/dev/null; then
  echo "FAIL: the node can reach the internet, the test would prove nothing"; exit 1
fi

echo "==> loading the offline pack"
for node in $("$CQ_KIND" get nodes --name "$NAME"); do
  for f in "$CQ_HOME"/offline/images/*.tar; do
    docker exec -i "$node" ctr -n k8s.io images import - < "$f" >/dev/null 2>&1
  done
done
kubectl apply -f "$CQ_HOME/offline/manifests/metrics-server.yaml" >/dev/null
kubectl apply --server-side -f "$CQ_HOME/offline/manifests/gateway-api.yaml" >/dev/null

echo "==> levels"
for f in ${FILTERS[@]}; do CQ_CLUSTER="$NAME" "$CQ_ROOT/tests/run-levels.sh" "$f"; done

echo "==> cleanup"
"$CQ_KIND" delete cluster --name "$NAME" --kubeconfig "$KUBECONFIG" >/dev/null
