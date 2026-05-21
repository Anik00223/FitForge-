@echo off
setlocal

cd /d "%~dp0"
set "DOCKER_CONFIG=%~dp0.docker-config"
if not exist "%DOCKER_CONFIG%" mkdir "%DOCKER_CONFIG%"

echo Starting FitForge with Docker Compose...
echo.
docker compose up -d --build

pause
