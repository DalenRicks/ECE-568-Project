if (Test-Path env:VIRTUAL_ENV) {
   Write-Output "Virtual environment is active: $env:VIRTUAL_ENV"
} else {
   Write-Output "No virtual environment active"
}