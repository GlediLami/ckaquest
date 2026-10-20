# Debrief

Values under `data:` must be base64-encoded exactly once. Values under `stringData:` are plain text. A common mistake is to encode a value yourself and then pass it to `--from-literal`, which encodes it again.

Use `echo -n`. Plain `echo` adds a newline, and the newline ends up inside the secret.

base64 is encoding, not encryption. Anyone who can `get secrets` can read them. Protection comes from RBAC and encryption at rest (`--encryption-provider-config` on the API server).

Env vars from a Secret are set when the container starts. Changing the Secret does not change a running container. Mounted Secret files are updated after a short delay, but not when mounted with `subPath`.

Your notes: Secrets, Encrypting Secret Data at Rest
