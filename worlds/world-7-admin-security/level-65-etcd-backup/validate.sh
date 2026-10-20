#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "etcd-snapshot.db exists" node_ok controlplane 'test -s /opt/course/65/etcd-snapshot.db'
check 2 "the snapshot is valid" node_ok controlplane 'etcdutl snapshot status /opt/course/65/etcd-snapshot.db'
check "status.txt has the status table" node_ok controlplane 'grep -q HASH /opt/course/65/status.txt'
finish
