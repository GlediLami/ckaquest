"""Writes World 8 (networking: Gateway API, Ingress, NetworkPolicy, CoreDNS)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from genlib import level

W = "world-8-networking-2"
CURL = "curlimages/curl:8.11.1"
GW_DOCS = "https://gateway-api.sigs.k8s.io/guides/http-routing/"
K8S_GW = "https://kubernetes.io/docs/concepts/services-networking/gateway/"


def echo_app(ns, name, text, port=8080):
    """Deployment + Service that answer with a fixed text."""
    return f"""cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: {ns}
spec:
  replicas: 1
  selector:
    matchLabels: {{app: {name}}}
  template:
    metadata:
      labels: {{app: {name}}}
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0
        args: ["-text={text}", "-listen=:{port}"]
        ports:
        - containerPort: {port}
---
apiVersion: v1
kind: Service
metadata:
  name: {name}
  namespace: {ns}
spec:
  selector: {{app: {name}}}
  ports:
  - port: 80
    targetPort: {port}
EOF"""


def gateway(ns, name="web-gw", extra_listener=""):
    return f"""cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: {name}
  namespace: {ns}
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    protocol: HTTP
    port: 80{extra_listener}
EOF
cq_wait 120 bash -c '[ -n "$(kubectl get svc -n {ns} -l gateway.networking.k8s.io/gateway-name={name} -o name)" ]'"""


GET = 'curl_host() { in_cluster_out "$1" ' + CURL + ' curl -s -m 5 -H "Host: $2" "http://$(gw_addr "$3")$4"; }'
ACCEPTED = """route_ok() { [ "$(kubectl get httproute "$2" -n "$1" -o jsonpath='{.status.parents[0].conditions[?(@.type=="Accepted")].status} {.status.parents[0].conditions[?(@.type=="ResolvedRefs")].status}')" = "True True" ]; }"""

level(W, "level-71-httproute", dict(
    name="First Route Through the Gateway",
    description="The shop has a Gateway and a frontend, but nothing connects them",
    objective="Create an HTTPRoute that sends shop.example.com to the frontend",
    xp=250, difficulty="intermediate", expected_time="8m", domain="networking", course_section=9,
    namespace="shop", requires=["gateway"], concepts=["Gateway API", "HTTPRoute", "parentRefs", "hostnames"],
    task="""Namespace **shop** has a Gateway **web-gw** (class `nginx`, HTTP listener on port 80) and a Service **shop-frontend** on port 80.

Create an HTTPRoute **shop-route** in namespace **shop** that attaches to **web-gw** and sends all requests for host `shop.example.com` to **shop-frontend** on port 80.""",
    docs=[K8S_GW, GW_DOCS]),
    setup=echo_app("shop", "shop-frontend", "shop frontend") + "\n" + gateway("shop"),
    validate=GET + "\n" + ACCEPTED + """
check "HTTPRoute shop-route attaches to web-gw" field_eq shop httproute/shop-route '{.spec.parentRefs[0].name}' web-gw
check "it matches host shop.example.com" field_eq shop httproute/shop-route '{.spec.hostnames[0]}' shop.example.com
check "route is Accepted and its backend resolves" route_ok shop shop-route
check 3 "shop.example.com through the Gateway answers 'shop frontend'" out_match "shop frontend" curl_host shop shop.example.com web-gw /""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shop-route
  namespace: shop
spec:
  parentRefs:
  - name: web-gw
  hostnames: ["shop.example.com"]
  rules:
  - backendRefs:
    - name: shop-frontend
      port: 80
EOF""",
    hints=["`k get gateway,svc -n shop`. A Gateway alone routes nothing. Routes attach to it.",
           "The HTTPRoute needs `parentRefs` (the Gateway), `hostnames`, and a rule with `backendRefs` (Service name and port).",
           "Copy the HTTPRoute example from the Gateway docs page. No match block means everything under /."],
    solution="""```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shop-route
  namespace: shop
spec:
  parentRefs:
  - name: web-gw
  hostnames: ["shop.example.com"]
  rules:
  - backendRefs:
    - name: shop-frontend
      port: 80
```

```bash
k apply -f route.yaml
k describe httproute shop-route -n shop     # Accepted: True, ResolvedRefs: True
```""",
    debrief="""# First Route Through the Gateway

## What happened
Gateway API splits the old Ingress into roles:
- **GatewayClass**: which controller (here NGINX Gateway Fabric, class `nginx`). Set up by the platform team.
- **Gateway**: the listeners (ports, protocols, TLS). Owned by the cluster operator.
- **HTTPRoute**: host and path rules to Services. Owned by the app team.

## Check the status, not just the YAML
`k describe httproute` shows conditions per parent Gateway:
- `Accepted: False` means the route did not attach (wrong Gateway name, wrong namespace, listener does not allow it).
- `ResolvedRefs: False` means a backend Service or port is wrong.

## Exam angle
- Gateway API is in the CKA curriculum since 2025. Expect to write an HTTPRoute from the docs.
- There is no `kubectl create httproute`. Copy from the docs and edit.
- `k get gateway` shows the address and whether it is Programmed.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/gateway/

Your notes: Gateway API""")

level(W, "level-72-route-broken", dict(
    name="The Route Goes Nowhere",
    description="An HTTPRoute exists, but blog.example.com returns 404 or 500",
    objective="Fix the HTTPRoute so the blog is reachable through the Gateway",
    xp=300, difficulty="intermediate", expected_time="8m", domain="troubleshooting", course_section=9,
    namespace="blog", requires=["gateway"], concepts=["HTTPRoute status", "ResolvedRefs", "parentRefs"],
    task="""Requests for `blog.example.com` through Gateway **web-gw** in namespace **blog** do not reach the blog.

HTTPRoute **blog-route** should send them to Service **blog** on port 80. Find what is wrong with the route and fix it. Do not change the Gateway or the Service.""",
    docs=[K8S_GW, "https://gateway-api.sigs.k8s.io/reference/spec/#httproute"]),
    setup=echo_app("blog", "blog", "blog home") + "\n" + gateway("blog") + """
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: blog-route
  namespace: blog
spec:
  parentRefs:
  - name: web-gateway
  hostnames: ["blog.example.com"]
  rules:
  - backendRefs:
    - name: blog
      port: 8080
EOF""",
    validate=GET + "\n" + ACCEPTED + """
check "Gateway web-gw is unchanged" field_eq blog gateway/web-gw '{.spec.listeners[0].port}' 80
check "Service blog is unchanged" field_eq blog svc/blog '{.spec.ports[0].port}' 80
check 2 "blog-route is Accepted and resolves" route_ok blog blog-route
check 2 "blog.example.com answers 'blog home'" out_match "blog home" curl_host blog blog.example.com web-gw /""",
    solve="""kubectl patch httproute blog-route -n blog --type=json -p '[{"op":"replace","path":"/spec/parentRefs/0/name","value":"web-gw"},{"op":"replace","path":"/spec/rules/0/backendRefs/0/port","value":80}]'""",
    hints=["`k describe httproute blog-route -n blog`. Read the Conditions under Status.",
           "Two things are wrong: the Gateway it attaches to, and the backend port.",
           "`k get gateway -n blog` for the real name. `k get svc blog -n blog` for the real port. Then `k edit httproute blog-route -n blog`."],
    solution="""```bash
k describe httproute blog-route -n blog     # no parent status, or ResolvedRefs False
k get gateway,svc -n blog
k edit httproute blog-route -n blog
#   parentRefs: - name: web-gw
#   backendRefs: - name: blog, port: 80
```""",
    debrief="""# The Route Goes Nowhere

## What happened
The route pointed at a Gateway that does not exist (`web-gateway`), so no controller picked it up. It also pointed at port 8080, but the Service listens on 80. The container port does not matter to a route. Only the Service port does.

## How to read route status
- No `status.parents` at all: no Gateway accepted the route. Check the parentRef name and namespace.
- `Accepted: False, reason NotAllowedByListeners`: the listener's `allowedRoutes` does not include this namespace.
- `ResolvedRefs: False, reason BackendNotFound`: wrong Service name or port.

## Exam angle
- Troubleshooting a route is a likely task. `k describe` first, then fix.
- `backendRefs.port` is the Service port, like `service.port.number` in an Ingress.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/gateway/

Your notes: Gateway API, Network Troubleshooting""")

level(W, "level-73-traffic-split", dict(
    name="80/20",
    description="v2 of the API is ready for a small share of the traffic",
    objective="Split traffic between two versions with HTTPRoute weights",
    xp=300, difficulty="intermediate", expected_time="8m", domain="networking", course_section=9,
    namespace="api-split", requires=["gateway"], concepts=["HTTPRoute", "weights", "canary"],
    task="""Namespace **api-split** has Services **api-v1** and **api-v2** (both port 80) and Gateway **web-gw**.

Create HTTPRoute **api-route** for host `api.example.com` that sends **80%** of requests to api-v1 and **20%** to api-v2.""",
    docs=["https://gateway-api.sigs.k8s.io/guides/traffic-splitting/", K8S_GW]),
    setup=echo_app("api-split", "api-v1", "api v1") + "\n" + echo_app("api-split", "api-v2", "api v2") + "\n" + gateway("api-split"),
    validate=GET + "\n" + ACCEPTED + """
weights() { kubectl get httproute api-route -n api-split -o jsonpath='{range .spec.rules[0].backendRefs[*]}{.name}={.weight} {end}'; }
both_seen() {
  local out; out="$(in_cluster_out api-split """ + CURL + """ sh -c 'for i in $(seq 40); do curl -s -m 3 -H "Host: api.example.com" http://'"$(gw_addr web-gw)"'/; done')"
  grep -q "api v1" <<<"$out" && grep -q "api v2" <<<"$out"
}
check 2 "weights are api-v1=80 and api-v2=20" out_match "api-v1=80 api-v2=20|api-v2=20 api-v1=80" weights
check "api-route is Accepted and resolves" route_ok api-split api-route
check 2 "40 requests reach both versions" both_seen""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: api-route
  namespace: api-split
spec:
  parentRefs:
  - name: web-gw
  hostnames: ["api.example.com"]
  rules:
  - backendRefs:
    - name: api-v1
      port: 80
      weight: 80
    - name: api-v2
      port: 80
      weight: 20
EOF""",
    hints=["One rule, two backendRefs.", "Each backendRef takes a `weight`. Weights are relative, 80 and 20 (or 4 and 1).",
           "See 'Traffic splitting' in the Gateway API guides. Test: `for i in $(seq 20); do curl -s -H 'Host: api.example.com' <gateway>; done`."],
    solution="""```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: api-route
  namespace: api-split
spec:
  parentRefs:
  - name: web-gw
  hostnames: ["api.example.com"]
  rules:
  - backendRefs:
    - name: api-v1
      port: 80
      weight: 80
    - name: api-v2
      port: 80
      weight: 20
```""",
    debrief="""# 80/20

## What happened
`weight` on backendRefs splits traffic per request. With plain Services you could only split by pod count (level 18). Here the split is exact and independent of replicas.

## Facts to remember
- Weights are relative. 80/20, 8/2 and 4/1 are the same.
- Weight 0 sends nothing to that backend. Handy for a quick rollback.
- No weight means 1.

## Exam angle
- Canary and blue/green with Gateway API is a natural exam task.
- Ingress has no standard weights. It needs controller annotations, which is why Gateway API exists.

Bookmark: https://gateway-api.sigs.k8s.io/guides/traffic-splitting/

Your notes: Gateway API""")

level(W, "level-74-https-listener", dict(
    name="HTTPS on the Gateway",
    description="The shop must serve HTTPS",
    objective="Add an HTTPS listener with a TLS Secret to the Gateway",
    xp=350, difficulty="advanced", expected_time="12m", domain="networking", course_section=9,
    namespace="secure-shop", requires=["gateway"], concepts=["TLS Secret", "Gateway listener", "certificateRefs"],
    task="""A certificate and key for `secure.example.com` are in `~/ckaquest-work/74/` (`tls.crt`, `tls.key`).

1. Create a TLS Secret **secure-tls** in namespace **secure-shop** from them.
2. Add a listener **https** to Gateway **web-gw**: protocol HTTPS, port 443, hostname `secure.example.com`, TLS mode Terminate with that Secret.
3. Attach HTTPRoute **secure-route** (it exists) to the new listener as well, so `https://secure.example.com` reaches Service **secure-app**.""",
    docs=["https://gateway-api.sigs.k8s.io/guides/tls/", K8S_GW]),
    setup=echo_app("secure-shop", "secure-app", "secure shop") + "\n" + gateway("secure-shop") + """
W="$(cq_work_dir 74)"
openssl req -x509 -nodes -newkey rsa:2048 -days 365 -subj "/CN=secure.example.com" \\
  -addext "subjectAltName=DNS:secure.example.com" -keyout "$W/tls.key" -out "$W/tls.crt" 2>/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: secure-route
  namespace: secure-shop
spec:
  parentRefs:
  - name: web-gw
    sectionName: http
  hostnames: ["secure.example.com"]
  rules:
  - backendRefs:
    - name: secure-app
      port: 80
EOF""",
    validate="""https_ok() { in_cluster_out secure-shop """ + CURL + """ curl -sk -m 5 --resolve "secure.example.com:443:$(kubectl get svc -n secure-shop -l gateway.networking.k8s.io/gateway-name=web-gw -o jsonpath='{.items[0].spec.clusterIP}')" https://secure.example.com/ | grep -q "secure shop"; }
listener() { kubectl get gateway web-gw -n secure-shop -o jsonpath='{range .spec.listeners[?(@.name=="https")]}{.protocol} {.port} {.hostname} {.tls.mode} {.tls.certificateRefs[0].name}{end}'; }
check "Secret secure-tls is type kubernetes.io/tls" field_eq secure-shop secret/secure-tls '{.type}' kubernetes.io/tls
check 2 "listener https: HTTPS 443 secure.example.com Terminate secure-tls" out_eq "HTTPS 443 secure.example.com Terminate secure-tls" listener
check "HTTP listener is still there" field_eq secure-shop gateway/web-gw '{.spec.listeners[?(@.name=="http")].port}' 80
check 3 "https://secure.example.com answers 'secure shop'" https_ok""",
    solve="""kubectl create secret tls secure-tls -n secure-shop --cert="$CQ_WORK/74/tls.crt" --key="$CQ_WORK/74/tls.key"
kubectl patch gateway web-gw -n secure-shop --type=json -p '[{"op":"add","path":"/spec/listeners/-","value":{"name":"https","protocol":"HTTPS","port":443,"hostname":"secure.example.com","tls":{"mode":"Terminate","certificateRefs":[{"kind":"Secret","name":"secure-tls"}]}}}]'
kubectl patch httproute secure-route -n secure-shop --type=json -p '[{"op":"add","path":"/spec/parentRefs/-","value":{"name":"web-gw","sectionName":"https"}}]'
sleep 10""",
    hints=["`k create secret tls secure-tls --cert=... --key=... -n secure-shop`.",
           "A listener with `protocol: HTTPS` needs a `tls:` block with `mode: Terminate` and `certificateRefs` pointing to the Secret.",
           "The route has `sectionName: http`, so it only attaches to the HTTP listener. Add a second parentRef with `sectionName: https`, or remove sectionName."],
    solution="""```bash
k create secret tls secure-tls -n secure-shop --cert=~/ckaquest-work/74/tls.crt --key=~/ckaquest-work/74/tls.key
k edit gateway web-gw -n secure-shop
```

```yaml
  listeners:
  - name: http
    protocol: HTTP
    port: 80
  - name: https
    protocol: HTTPS
    port: 443
    hostname: secure.example.com
    tls:
      mode: Terminate
      certificateRefs:
      - name: secure-tls
```

```bash
k edit httproute secure-route -n secure-shop
#   parentRefs:
#   - name: web-gw
#     sectionName: http
#   - name: web-gw
#     sectionName: https
```""",
    debrief="""# HTTPS on the Gateway

## What happened
TLS belongs to the Gateway listener, not to the route. The listener terminates TLS with the Secret, then routes plain HTTP to the backend.

`sectionName` pins a route to one listener by name. The route was pinned to `http`, so the new HTTPS listener had no routes.

## Facts to remember
- `k create secret tls` gives type `kubernetes.io/tls` with keys `tls.crt` and `tls.key`.
- The Secret must be in the Gateway's namespace, or you need a ReferenceGrant.
- `mode: Passthrough` sends TLS through untouched (TLSRoute, not HTTPRoute).

## Exam angle
- Expect "add HTTPS" or "the HTTPS listener is not ready": check the Secret name, namespace and the listener status in `k describe gateway`.

Bookmark: https://gateway-api.sigs.k8s.io/guides/tls/

Your notes: Gateway API, TLS Basics""")

level(W, "level-75-ingress-class", dict(
    name="Ingress Without a Class",
    description="The Ingress has no address and the controller ignores it",
    objective="Make the ingress-nginx controller serve the Ingress",
    xp=250, difficulty="intermediate", expected_time="6m", domain="networking", course_section=9,
    namespace="ingress-lab", requires=["ingress"], concepts=["IngressClass", "ingressClassName", "ingress-nginx"],
    task="""Ingress **docs-ingress** in namespace **ingress-lab** routes `docs.example.com` to Service **docs** on port 80. It never gets an address and requests return 404 from the controller.

Fix the Ingress so the ingress-nginx controller serves it.""",
    docs=["https://kubernetes.io/docs/concepts/services-networking/ingress/#ingress-class"]),
    setup=echo_app("ingress-lab", "docs", "docs site") + """
kubectl create ingress docs-ingress -n ingress-lab --rule="docs.example.com/*=docs:80" >/dev/null""",
    validate="""via_controller() { in_cluster_out ingress-lab """ + CURL + """ curl -s -m 5 -H "Host: docs.example.com" http://ingress-nginx-controller.ingress-nginx/; }
check 2 "ingressClassName is nginx" field_eq ingress-lab ing/docs-ingress '{.spec.ingressClassName}' nginx
check 3 "docs.example.com through the controller answers 'docs site'" out_match "docs site" via_controller""",
    solve="""kubectl patch ingress docs-ingress -n ingress-lab -p '{"spec":{"ingressClassName":"nginx"}}'
sleep 15""",
    hints=["`k get ingressclass`. How many are there, and is one marked default?", "An Ingress without a class is only served if an IngressClass has the default annotation.",
           "`k patch ingress docs-ingress -n ingress-lab -p '{\"spec\":{\"ingressClassName\":\"nginx\"}}'`, or `k create ingress ... --class=nginx`."],
    solution="""```bash
k get ingressclass
k edit ingress docs-ingress -n ingress-lab     # spec.ingressClassName: nginx
k get ingress -n ingress-lab                   # ADDRESS appears after a few seconds
```""",
    debrief="""# Ingress Without a Class

## What happened
A cluster can run several Ingress controllers. Each one only serves Ingresses of its class. Without `ingressClassName`, the Ingress is only picked up if one IngressClass carries `ingressclass.kubernetes.io/is-default-class: "true"`. This cluster has none.

## Exam angle
- `k create ingress NAME --class=nginx --rule="host/path*=svc:port"` writes the class for you.
- `k get ingressclass` first. Use the name from there.
- The old annotation `kubernetes.io/ingress.class` is deprecated. Use the field.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/ingress/

Your notes: Networking, Service Networking""")

level(W, "level-76-ingress-to-gateway", dict(
    name="Migrate to Gateway API",
    description="The team moves from Ingress to Gateway API",
    objective="Replace an Ingress with an equivalent HTTPRoute",
    xp=300, difficulty="advanced", expected_time="10m", domain="networking", course_section=9,
    namespace="migrate-lab", requires=["gateway"], concepts=["Ingress", "HTTPRoute", "path matches", "migration"],
    task="""Ingress **legacy** in namespace **migrate-lab** has two rules for host `app.example.com`:
- path prefix `/api` to Service **api** port 80
- path prefix `/` to Service **web** port 80

Create HTTPRoute **app-route** on Gateway **web-gw** with the same behaviour. Then delete the Ingress.""",
    docs=["https://gateway-api.sigs.k8s.io/guides/migrating-from-ingress/", GW_DOCS]),
    setup=echo_app("migrate-lab", "api", "api backend") + "\n" + echo_app("migrate-lab", "web", "web frontend") + "\n" + gateway("migrate-lab") + """
kubectl create ingress legacy -n migrate-lab --rule="app.example.com/api*=api:80" --rule="app.example.com/*=web:80" >/dev/null""",
    validate=GET + "\n" + ACCEPTED + """
check "Ingress legacy is gone" not_exists migrate-lab ing/legacy
check "app-route is Accepted and resolves" route_ok migrate-lab app-route
check 2 "/api/users goes to api" out_match "api backend" curl_host migrate-lab app.example.com web-gw /api/users
check 2 "/ goes to web" out_match "web frontend" curl_host migrate-lab app.example.com web-gw /""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-route
  namespace: migrate-lab
spec:
  parentRefs:
  - name: web-gw
  hostnames: ["app.example.com"]
  rules:
  - matches:
    - path: {type: PathPrefix, value: /api}
    backendRefs:
    - name: api
      port: 80
  - matches:
    - path: {type: PathPrefix, value: /}
    backendRefs:
    - name: web
      port: 80
EOF
kubectl delete ingress legacy -n migrate-lab""",
    hints=["`k get ingress legacy -n migrate-lab -o yaml`. Note each path and backend.", "Each Ingress path becomes one HTTPRoute rule with `matches: - path: {type: PathPrefix, value: ...}`.",
           "The longest match wins in Gateway API, so the order of the rules does not matter."],
    solution="""```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-route
  namespace: migrate-lab
spec:
  parentRefs:
  - name: web-gw
  hostnames: ["app.example.com"]
  rules:
  - matches:
    - path: {type: PathPrefix, value: /api}
    backendRefs:
    - name: api
      port: 80
  - matches:
    - path: {type: PathPrefix, value: /}
    backendRefs:
    - name: web
      port: 80
```

```bash
k apply -f route.yaml
k delete ingress legacy -n migrate-lab
```""",
    debrief="""# Migrate to Gateway API

## Mapping
| Ingress | HTTPRoute |
|---|---|
| `ingressClassName` | Gateway `gatewayClassName`, route `parentRefs` |
| `rules[].host` | `hostnames` |
| `paths[].path` + `pathType: Prefix` | `matches[].path` with `type: PathPrefix` |
| `backend.service.name/port.number` | `backendRefs[].name/port` |
| `tls` | Gateway listener with `tls` |

## Exam angle
- The tool `ingress2gateway` exists, but in the exam you write it by hand.
- Delete the old Ingress only after the route works.

Bookmark: https://gateway-api.sigs.k8s.io/guides/migrating-from-ingress/

Your notes: Gateway API""")

level(W, "level-77-netpol-namespaces", dict(
    name="Only the Frontend Team",
    description="The database must only accept traffic from the frontend namespace",
    objective="Write a NetworkPolicy with a namespaceSelector",
    xp=300, difficulty="advanced", expected_time="10m", domain="networking", course_section=7,
    namespace="db-ns", concepts=["NetworkPolicy", "namespaceSelector", "kubernetes.io/metadata.name"],
    task="""Namespace **db-ns** runs pod **postgres** (label `app=postgres`, port 5432, Service **postgres**).

Create NetworkPolicy **allow-frontend** in **db-ns** so that the postgres pods accept ingress on TCP 5432 **only** from pods in namespace **frontend-ns**. Pods in any other namespace, and other pods in db-ns, must be blocked.""",
    docs=["https://kubernetes.io/docs/concepts/services-networking/network-policies/#behavior-of-to-and-from-selectors"]),
    setup="""kubectl create namespace frontend-ns --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl create namespace other-ns --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl run postgres -n db-ns --image=postgres:16-alpine --labels=app=postgres --env=POSTGRES_PASSWORD=cq --port=5432 >/dev/null
kubectl expose pod postgres -n db-ns --port=5432 >/dev/null
kubectl wait --for=condition=Ready pod/postgres -n db-ns --timeout=120s >/dev/null""",
    validate="""T="nc -z -w 3 postgres.db-ns.svc.cluster.local 5432"
check "allow-frontend selects app=postgres" field_eq db-ns netpol/allow-frontend '{.spec.podSelector.matchLabels.app}' postgres
check 2 "a pod in frontend-ns can connect" in_cluster_ok frontend-ns busybox:1.36 $T
check 2 "a pod in other-ns is blocked" in_cluster_fails other-ns busybox:1.36 $T
check "a pod in db-ns itself is blocked" in_cluster_fails db-ns busybox:1.36 $T""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
  namespace: db-ns
spec:
  podSelector:
    matchLabels: {app: postgres}
  policyTypes: [Ingress]
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: frontend-ns
    ports:
    - protocol: TCP
      port: 5432
EOF""",
    cleanup="kubectl delete namespace frontend-ns other-ns --ignore-not-found --wait=false >/dev/null 2>&1",
    hints=["Every namespace has the label `kubernetes.io/metadata.name=<name>`. Check with `k get ns --show-labels`.",
           "`from: - namespaceSelector: ...` allows all pods in matching namespaces. Do not add a podSelector in the same item unless you want AND.",
           "Once a policy selects the postgres pod for Ingress, everything not allowed is denied. You do not need a separate deny-all."],
    solution="""```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
  namespace: db-ns
spec:
  podSelector:
    matchLabels: {app: postgres}
  policyTypes: [Ingress]
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: frontend-ns
    ports:
    - protocol: TCP
      port: 5432
```""",
    debrief="""# Only the Frontend Team

## What happened
`namespaceSelector` matches namespaces by label. Kubernetes adds `kubernetes.io/metadata.name` to every namespace, so you can select one by name without labelling it.

## AND versus OR
```yaml
from:
- namespaceSelector: {...}     # item 1
  podSelector: {...}           # same item: namespace AND pod must match
- podSelector: {...}           # item 2: OR this
```
One dash too many or too few changes the meaning. This is the most common NetworkPolicy mistake.

## Exam angle
- A policy only isolates the pods it selects, and only in the directions in `policyTypes`.
- Test with `k run t -n <ns> --rm -it --image=busybox:1.36 -- nc -zv -w2 <svc>.<ns> <port>`.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/network-policies/

Your notes: Network Policy""")

level(W, "level-78-coredns-hosts", dict(
    name="A Name CoreDNS Does Not Know",
    description="Pods must resolve legacy.internal, which is not in any DNS zone",
    objective="Add a static entry to CoreDNS",
    xp=350, difficulty="advanced", expected_time="10m", domain="networking", course_section=9,
    namespace="dns-custom", concepts=["CoreDNS", "Corefile", "hosts plugin"],
    task="""Pods must resolve `legacy.internal` to `10.10.10.10`.

Add this to the cluster DNS (the CoreDNS ConfigMap in kube-system) with the `hosts` plugin. All other names, including `kubernetes.default`, must keep resolving.""",
    docs=["https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/",
          "https://coredns.io/plugins/hosts/"]),
    setup="""mkdir -p "$CQ_HOME/backup"
[ -f "$CQ_HOME/backup/coredns-78.yaml" ] || kubectl get cm coredns -n kube-system -o yaml > "$CQ_HOME/backup/coredns-78.yaml\"""",
    validate="""check 3 "legacy.internal resolves to 10.10.10.10" out_match "10\\.10\\.10\\.10" in_cluster_out dns-custom busybox:1.36 nslookup legacy.internal
check 2 "kubernetes.default still resolves" in_cluster_ok dns-custom busybox:1.36 nslookup kubernetes.default.svc.cluster.local
check "CoreDNS pods are Ready" pods_ready kube-system k8s-app=kube-dns""",
    solve="""kubectl get cm coredns -n kube-system -o jsonpath='{.data.Corefile}' > /tmp/cq-corefile
python3 - <<'EOF'
p = "/tmp/cq-corefile"
s = open(p).read()
s = s.replace("    kubernetes cluster.local", "    hosts {\\n       10.10.10.10 legacy.internal\\n       fallthrough\\n    }\\n    kubernetes cluster.local", 1)
open(p, "w").write(s)
EOF
kubectl create cm coredns -n kube-system --from-file=Corefile=/tmp/cq-corefile --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deploy coredns -n kube-system
kubectl rollout status deploy coredns -n kube-system --timeout=90s""",
    cleanup="""if [ -f "$CQ_HOME/backup/coredns-78.yaml" ]; then
  kubectl get cm coredns -n kube-system -o yaml | grep -q legacy.internal && {
    kubectl replace -f "$CQ_HOME/backup/coredns-78.yaml" >/dev/null 2>&1
    kubectl rollout restart deploy coredns -n kube-system >/dev/null 2>&1
  }
  mv -f "$CQ_HOME/backup/coredns-78.yaml" "$CQ_HOME/backup/coredns-78.yaml.done"
fi""",
    hints=["`k edit cm coredns -n kube-system`. The Corefile is a list of plugins inside `.:53 { ... }`.",
           "The hosts plugin takes lines like in /etc/hosts. Add `fallthrough` so other names go on to the next plugins.",
           "Put the `hosts { ... }` block before `kubernetes cluster.local`. CoreDNS reloads on its own after a minute, or `k rollout restart deploy coredns -n kube-system`."],
    solution="""```bash
k edit cm coredns -n kube-system
```

```
.:53 {
    errors
    health
    ready
    hosts {
       10.10.10.10 legacy.internal
       fallthrough
    }
    kubernetes cluster.local in-addr.arpa ip6.arpa {
    ...
```

```bash
k rollout restart deploy coredns -n kube-system
k run t --rm -it --image=busybox:1.36 -- nslookup legacy.internal
```""",
    debrief="""# A Name CoreDNS Does Not Know

## What happened
CoreDNS runs plugins in a fixed order for every query. `hosts` answers from a static list. Without `fallthrough` it would answer NXDOMAIN for every other name it does not know, and the cluster would break.

## Other common Corefile edits
- `forward . 8.8.8.8` changes the upstream resolver.
- A stub domain: a new server block `corp.local:53 { forward . 10.0.0.53 }`.
- `rewrite name foo.example.com foo.default.svc.cluster.local` aliases a name.

## Exam angle
- Back up the ConfigMap before you edit: `k get cm coredns -n kube-system -o yaml > coredns-backup.yaml`.
- The `reload` plugin picks up changes in about 30 seconds. A rollout restart is faster.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/

Your notes: DNS in Kubernetes""")
