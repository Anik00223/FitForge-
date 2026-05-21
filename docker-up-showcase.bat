@echo off
setlocal

cd /d "%~dp0"
set "DOCKER_CONFIG=%~dp0.docker-config"
if not exist "%DOCKER_CONFIG%" mkdir "%DOCKER_CONFIG%"

echo Starting separate FitForge Showcase Docker server...
echo Django direct: http://127.0.0.1:8011/
echo Nginx proxy:   http://127.0.0.1:8081/
echo.
docker compose -p fitforge-showcase -f docker-compose.showcase.yml up --build

pause
