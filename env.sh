# Source this in the terminal where you type kubectl commands:
#
#   source ~/projects/ckaquest/env.sh
#
# It only changes the current shell. Your ~/.kube/config and other clusters are untouched.
# The setup matches what you would do in the first minute of the real exam.

_cq_root="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
export CQ_ROOT="$_cq_root"
export KUBECONFIG="${CKAQUEST_KUBECONFIG:-$HOME/.ckaquest/kubeconfig}"
export CQ_WORK="${CQ_WORK:-$HOME/ckaquest-work}"
mkdir -p "$CQ_WORK"

# "ssh node01" goes into the kind node container
case ":$PATH:" in
  *":$_cq_root/bin/shims:"*) ;;
  *) export PATH="$_cq_root/bin/shims:$_cq_root/bin:$PATH" ;;
esac

# Exam habits
alias k=kubectl
export do="--dry-run=client -o yaml"
export now="--force --grace-period 0"
if [ -n "${BASH_VERSION:-}" ]; then
  source <(kubectl completion bash) 2>/dev/null
  complete -o default -F __start_kubectl k 2>/dev/null
elif [ -n "${ZSH_VERSION:-}" ]; then
  source <(kubectl completion zsh) 2>/dev/null
fi

if [ -n "${BASH_VERSION:-}" ]; then
  case "$PS1" in *"(cka)"*) ;; *) PS1="(cka) $PS1" ;; esac
fi

echo "CKAQuest shell ready. Context: $(kubectl config current-context 2>/dev/null || echo 'none, run ./install.sh')"
echo "Nodes: controlplane, node01, node02 (use: ssh node01). Work files: $CQ_WORK"
unset _cq_root
