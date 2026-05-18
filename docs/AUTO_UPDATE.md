# Auto-Update

LocalForge uses Tauri's built-in updater, which checks a manifest URL on app
launch (if `Settings → auto_update` is on; default ON).

## How it works

1. Tauri polls the endpoint defined in `tauri.conf.json`:
   ```json
   "endpoints": ["https://localforge.ai/updates/{{target}}/{{current_version}}"]
   ```
2. The server responds with a JSON manifest (see `installer/update_manifest.example.json`).
3. If a newer version exists, the user is prompted:
   `LocalForge 1.0.1 is available. Update now?`
4. On accept, Tauri downloads the signed zip, verifies the ed25519 signature against the public key embedded at build time, then relaunches with the new EXE.

## Why ed25519 signing matters

Without signature verification, an attacker who intercepts the update channel could replace your AI app with malware. Tauri's updater **refuses** any update whose signature doesn't validate against the public key compiled into your binary.

## Generating signing keys

```bash
# One-time, on your build machine
npm install -g @tauri-apps/cli
tauri signer generate -w ~/.tauri/localforge.key
# Copy the public key into tauri.conf.json -> tauri.updater.pubkey
# Keep ~/.tauri/localforge.key SECRET — required to sign every release
```

## Signing a release

```bash
tauri signer sign -k ~/.tauri/localforge.key \
                  -p "your-passphrase" \
                  LocalForge-1.0.1-win64.zip > sig.txt
# Paste sig.txt content into update_manifest.json -> platforms.windows-x86_64.signature
```

## Publishing the manifest

Upload to any static host (S3, Cloudflare R2, GitHub Pages). The path must match:

```
<endpoint>/<target>/<current_version>
e.g.   https://localforge.ai/updates/windows-x86_64/1.0.0
```

Return the manifest with HTTP 200 to trigger an update prompt, or HTTP 204 to indicate no update.

## Disabling updates entirely

For end users — **Settings → Privacy → Enable auto-update check: off.**
For air-gapped distribution — set `tauri.conf.json` `tauri.updater.active` to `false` at build time.

## Self-hosted update server

For organizations deploying internally:

```bash
# Static server is enough — pure file hosting
caddy file-server --browse --root ./updates --listen :443
```

Update `tauri.conf.json` endpoints to your internal URL before building.
