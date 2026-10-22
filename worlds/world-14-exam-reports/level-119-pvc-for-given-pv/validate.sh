#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "PVC mariadb is Bound to mariadb-pv" out_eq "Bound mariadb-pv" kubectl get pvc mariadb -n mariadb -o jsonpath='{.status.phase} {.spec.volumeName}'
check "PVC requests 250Mi, ReadWriteOnce" out_eq "250Mi ReadWriteOnce" kubectl get pvc mariadb -n mariadb -o jsonpath='{.spec.resources.requests.storage} {.spec.accessModes[0]}'
check "Deployment mariadb uses claim mariadb" field_eq mariadb deploy/mariadb '{.spec.template.spec.volumes[?(@.name=="data")].persistentVolumeClaim.claimName}' mariadb
check 2 "Deployment mariadb is Ready" deploy_ready mariadb mariadb
check "the pod wrote its data to the PV on node01" node_ok node01 'test -s /mnt/mariadb-data/ready'
finish
