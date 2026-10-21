@echo off
taskkill /f /im OpenCodeTokenMonitor*.exe >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -like '*python*') -and ($_.CommandLine -like '*main.py*' -or $_.CommandLine -like '*opencode_token_widget.py*') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >nul 2>&1
python -c "import psutil, os; [p.kill() for p in psutil.process_iter(['name', 'cmdline']) if any('main.py' in arg or 'opencode_token_widget.py' in arg for arg in (p.info['cmdline'] or [])) and p.pid != os.getpid()]" >nul 2>&1
echo [OK] OpenCode Token Monitor Closed.
