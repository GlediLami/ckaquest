#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
ex() { kubectl exec app -n config-lab -- sh -c "$1" 2>/dev/null; }
check "secret db-creds has password S3cure!" out_eq 'S3cure!' sh -c "kubectl get secret db-creds -n config-lab -o jsonpath='{.data.password}' | base64 -d"
check 2 "/etc/creds/password has the password" out_eq 'S3cure!' ex 'cat /etc/creds/password'
check "the volume is read-only" out_eq "ro" ex 'grep " /etc/creds " /proc/mounts | grep -o "ro," | head -c2'
check "file mode is 0400" field_eq config-lab pod/app '{.spec.volumes[?(@.secret.secretName=="db-creds")].secret.defaultMode}' 256
check 2 "LOG_LEVEL and REGION are env vars" out_eq "debug eu-central" ex 'echo $LOG_LEVEL $REGION'
finish
