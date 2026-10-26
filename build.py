# -*- coding: utf-8 -*-
"""
PyInstaller one-click build script.
Packages the modularized application into a standalone, portable single-file executable.
"""

import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "assets", "app_icon.ico")
if not os.path.exists(ICON_PATH):
    ICON_PATH = os.path.join(BASE_DIR, "app_icon.ico")

from core.config import APP_VERSION


def build():
    version_tag = APP_VERSION
    target_name = f"OpenCodeTokenMonitor_{version_tag}"

    print("=" * 60)
    print(f"  Building {target_name} (Standalone Portable Version)")
    print("=" * 60)

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--icon={ICON_PATH}",
        "--add-data", f"{os.path.join(BASE_DIR, 'assets')};assets",
        "--add-data", f"{os.path.join(BASE_DIR, 'app_icon.ico')};.",
        "--add-data", f"{os.path.join(BASE_DIR, 'app_icon.png')};.",
        "--name", target_name,
        os.path.join(BASE_DIR, "main.py")
    ]

    print("Command:", " ".join(cmd))
    res = subprocess.run(cmd, cwd=BASE_DIR)

    if res.returncode == 0:
        dist_dir = os.path.join(BASE_DIR, "dist")
        exe_versioned = os.path.join(dist_dir, f"{target_name}.exe")
        exe_std = os.path.join(dist_dir, "OpenCodeTokenMonitor.exe")
        exe_v1 = os.path.join(dist_dir, "OpenCodeTokenMonitor_v1.0.exe")
        if os.path.exists(exe_versioned):
            shutil.copy2(exe_versioned, exe_std)
            print("[OK] Synced as OpenCodeTokenMonitor.exe")
            shutil.copy2(exe_versioned, exe_v1)
            print("[OK] Synced as OpenCodeTokenMonitor_v1.0.exe")

        # Generate portable zip package
        import zipfile
        zip_path = os.path.join(dist_dir, f"{target_name}_Portable.zip")
        files_to_zip = [f"{target_name}.exe", "app_icon.ico", "app_icon.png", "stop.bat", "使用说明.txt"]
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in files_to_zip:
                fpath = os.path.join(dist_dir, fname)
                if os.path.exists(fpath):
                    zf.write(fpath, arcname=fname)
                    print(f"  + Added file: {fname}")
        print(f"[OK] Portable zip generated: {zip_path}")
        
        # Also sync general zip names
        zip_std = os.path.join(dist_dir, "OpenCodeTokenMonitor_Portable.zip")
        shutil.copy2(zip_path, zip_std)
        zip_v1 = os.path.join(dist_dir, "OpenCodeTokenMonitor_v1.0_Portable.zip")
        shutil.copy2(zip_path, zip_v1)
        print("\n[SUCCESS] Build completed successfully! Deliverables are in dist/")
    else:
        print("\n[ERROR] Build failed, please check the log above.")


if __name__ == "__main__":
    build()
