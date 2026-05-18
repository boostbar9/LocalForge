use anyhow::Result;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};

/// Returns the directory where LocalForge stores writable data.
/// Portable mode: `./localforge_data` next to the executable.
/// Normal mode: %APPDATA%/LocalForge.
pub fn data_dir() -> PathBuf {
    let exe = std::env::current_exe().unwrap_or_default();
    let exe_dir = exe.parent().unwrap_or(Path::new("."));
    let portable_marker = exe_dir.join("portable.txt");

    if portable_marker.exists() {
        return exe_dir.join("localforge_data");
    }
    dirs::data_dir()
        .map(|p| p.join("LocalForge"))
        .unwrap_or_else(|| exe_dir.join("localforge_data"))
}

/// Spawn the bundled Python backend (`pythonw.exe backend/main.py`).
pub fn spawn_backend(resource_dir: &Path) -> Result<Child> {
    let backend_dir = resource_dir.join("backend");
    let python = resource_dir.join("backend/python/pythonw.exe");
    let main_py = backend_dir.join("main.py");
    let data = data_dir();
    std::fs::create_dir_all(&data)?;

    log::info!("Spawning backend: {:?} {:?}", python, main_py);

    let child = Command::new(python)
        .arg(main_py)
        .env("LOCALFORGE_DATA_DIR", &data)
        .env("LOCALFORGE_RESOURCE_DIR", resource_dir)
        .env("PYTHONUNBUFFERED", "1")
        .current_dir(&backend_dir)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()?;

    Ok(child)
}

/// Poll the backend health endpoint until it responds 200 OK or timeout elapses.
pub fn wait_for_ready(url: &str, timeout_secs: u64) -> Result<()> {
    let deadline = Instant::now() + Duration::from_secs(timeout_secs);
    let client = reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(1))
        .build()?;
    while Instant::now() < deadline {
        if let Ok(resp) = client.get(url).send() {
            if resp.status().is_success() {
                return Ok(());
            }
        }
        std::thread::sleep(Duration::from_millis(500));
    }
    anyhow::bail!("Backend did not become ready in {}s", timeout_secs)
}
