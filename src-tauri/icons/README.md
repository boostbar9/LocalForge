Place app icons here for the Tauri bundler:

- `32x32.png`
- `128x128.png`
- `128x128@2x.png`
- `icon.icns` (macOS, not used)
- `icon.ico` (Windows)

The Tauri CLI can auto-generate all sizes from a single 1024×1024 PNG:

```bash
cargo tauri icon path/to/source.png
```

See `resources/icon.png` for the source logo.
