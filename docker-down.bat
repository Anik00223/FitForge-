@echo off
setlocal

cd /d "%~dp0"
set "DOCKER_CONFIG=%~dp0.docker-config"
if not exist "%DOCKER_CONFIG%" mkdir "%DOCKER_CONFIG%"

docker compose down

pause
