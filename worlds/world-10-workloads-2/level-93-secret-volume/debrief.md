# Credentials as Files

## What happened
Each Secret key becomes a file in the mount. Mounted Secrets update when the Secret changes (unless subPath). Env vars do not.

## defaultMode
YAML reads `0400` as octal and the API stores decimal 256. In JSON you must write 256. Both mean read-only for the owner.

## Exam angle
- Shell quoting of special characters is a classic trap. Check with `base64 -d`.
- `envFrom` with a ConfigMap or Secret loads all keys. `env.valueFrom` picks one.

Bookmark: https://kubernetes.io/docs/concepts/configuration/secret/

Your notes: Secrets, Config, Environment Variables
