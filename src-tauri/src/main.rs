#![cfg_attr(all(not(debug_assertions), target_os = "windows"), windows_subsystem = "windows")]

mod backend;
mod commands;

use std::sync::Mutex;
use tauri::Manager;

pub struct AppState {
    pub backend_child: Mutex<Option<std::process::Child>>,
}

fn main() {
    env_logger::init();

    tauri::Builder::default()
        .manage(AppState { backend_child: Mutex::new(None) })
        .invoke_handler(tauri::generate_handler![
            commands::get_app_version,
            commands::open_path,
            commands::reveal_in_explorer,
            commands::pick_file,
            commands::pick_folder,
            commands::get_backend_status,
            commands::restart_backend,
            commands::get_system_info,
            commands::is_portable_mode,
        ])
        .setup(|app| {
            let handle = app.handle();
            let resource_dir = handle
                .path_resolver()
                .resource_dir()
                .expect("Failed to resolve resource dir");

            // Spawn Python backend
            let child = backend::spawn_backend(&resource_dir)?;
            let state: tauri::State<AppState> = handle.state();
            *state.backend_child.lock().unwrap() = Some(child);

            // Wait for backend readiness (max 30s) in a thread; show splash in UI
            let handle_clone = handle.clone();
            std::thread::spawn(move || {
                if backend::wait_for_ready("http://127.0.0.1:8765/api/health", 30).is_ok() {
                    let _ = handle_clone.emit_all("backend-ready", ());
                } else {
                    let _ = handle_clone.emit_all("backend-failed", ());
                }
            });

            Ok(())
        })
        .on_window_event(|event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event.event() {
                // Gracefully kill backend
                let app = event.window().app_handle();
                let state: tauri::State<AppState> = app.state();
                if let Some(mut child) = state.backend_child.lock().unwrap().take() {
                    let _ = child.kill();
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
