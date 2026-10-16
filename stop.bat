@echo off
taskkill /f /im OpenCodeTokenMonitor*.exe >nul 2>&1
python -c "import psutil, os; [p.kill() for p in psutil.process_iter(['name', 'cmdline']) if any('main.py' in arg or 'opencode_token_widget.py' in arg for arg in (p.info['cmdline'] or [])) and p.pid != os.getpid()]" >nul 2>&1
echo [OK] OpenCode Token Monitor Closed.
