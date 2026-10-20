#!/usr/bin/env bash
# Mock CKA exam. See engine/exam.py for the commands.
cd "$(dirname "$0")" || exit 1
source lib/common.sh
exec venv/bin/python3 engine/exam.py "$@"
