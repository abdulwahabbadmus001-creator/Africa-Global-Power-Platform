Write-Host "Starting AGP PostgreSQL and API..." -ForegroundColor Cyan
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Running database migrations..." -ForegroundColor Cyan
docker compose exec api alembic upgrade head
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "AGP API: http://localhost:8000" -ForegroundColor Green
Write-Host "Swagger: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Next: cd frontend; npm install; npm run dev" -ForegroundColor Yellow
