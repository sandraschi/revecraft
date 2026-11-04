@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\revecraft-cli.exe" (
    ".venv\Scripts\revecraft-cli.exe" %*
) else (
    uv run revecraft-cli %*
)
