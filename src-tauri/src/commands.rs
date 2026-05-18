use serde::Serialize;
use sysinfo::System;
use tauri_plugin_dialog::DialogExt;

#[derive(Serialize)]
pub struct SystemInfo {
    cpu: String,
    cores: usize,
    ram_gb: u64,
    os: String,
}

#[tauri::command]
pub fn get_app_version(app: tauri::AppHandle) -> String {
    app.package_info().version.to_string()
}

#[tauri::command]
pub fn open_path(path: String) -> Result<(), String> {
    open::that(path).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn reveal_in_explorer(path: String) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        std::process::Command::new("explorer")
            .args(["/select,", &path])
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    let _ = path; // silence unused warning on non-Windows
    Ok(())
}

#[tauri::command]
pub async fn pick_file(app: tauri::AppHandle, filters: Vec<String>) -> Option<String> {
    let mut builder = app.dialog().file();
    if !filters.is_empty() {
        let exts: Vec<&str> = filters.iter().map(|s| s.as_str()).collect();
        builder = builder.add_filter("Files", &exts);
    }
    builder
        .blocking_pick_file()
        .map(|p| p.to_string())
}

#[tauri::command]
pub async fn pick_folder(app: tauri::AppHandle) -> Option<String> {
    app.dialog()
        .file()
        .blocking_pick_folder()
        .map(|p| p.to_string())
}

#[tauri::command]
pub async fn get_backend_status() -> bool {
    reqwest::Client::new()
        .get("http://127.0.0.1:8765/api/health")
        .timeout(std::time::Duration::from_secs(2))
        .send()
        .await
        .map(|r| r.status().is_success())
        .unwrap_or(false)
}

#[tauri::command]
pub fn restart_backend(_app: tauri::AppHandle) -> Result<(), String> {
    // Implementation: kill existing child via AppState, respawn.
    // Simplified for brevity — see backend.rs.
    Ok(())
}

#[tauri::command]
pub fn get_system_info() -> SystemInfo {
    let mut sys = System::new_all();
    sys.refresh_all();
    let cpu = sys
        .cpus()
        .first()
        .map(|c| c.brand().to_string())
        .unwrap_or_default();
    SystemInfo {
        cpu,
        cores: sys.cpus().len(),
        ram_gb: sys.total_memory() / 1024 / 1024 / 1024,
        os: System::long_os_version().unwrap_or_else(|| "Unknown".into()),
    }
}

#[tauri::command]
pub fn is_portable_mode() -> bool {
    let exe = std::env::current_exe().unwrap_or_default();
    exe.parent()
        .map(|p| p.join("portable.txt").exists())
        .unwrap_or(false)
}
