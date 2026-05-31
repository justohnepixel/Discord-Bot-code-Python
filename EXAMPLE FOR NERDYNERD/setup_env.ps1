<#
setup_env.ps1

Creates a local virtual environment in `.venv` and installs packages from
`requirements.txt`. Run this from the workspace root in PowerShell.
#>

try {
    $py = (Get-Command py -ErrorAction SilentlyContinue).Source
} catch {
    $py = $null
}
if (-not $py) {
    try {
        $py = (Get-Command python -ErrorAction SilentlyContinue).Source
    } catch {
        $py = $null
    }
}

if (-not $py) {
    Write-Error "Neither 'py' nor 'python' was found on PATH. Install Python and retry."
    exit 1
}

Write-Host "Using Python executable: $py"

Write-Host "Creating virtual environment .venv..."
& $py -3 -m venv .venv
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create virtual environment."; exit $LASTEXITCODE }

Write-Host "Upgrading pip in venv..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip

if (Test-Path requirements.txt) {
    Write-Host "Installing requirements.txt into venv..."
    & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
} else {
    Write-Host "No requirements.txt found, skipping install."
}

Write-Host "Setup complete. Activate with: .\.venv\Scripts\Activate.ps1"
