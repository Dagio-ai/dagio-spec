param()

$archDir = if ($env:ARCHITECTURE_DIR) { $env:ARCHITECTURE_DIR } else { 'specs/architecture' }
$readmePath = Join-Path $archDir 'README.md'
$overviewPath = Join-Path $archDir 'architecture_overview.md'
$architectureJsonPath = Join-Path $archDir 'architecture.json'
$architectureLogPath = Join-Path $archDir 'architecture_logs.md'

$defaultViews = @(
    'architecture_overview.md',
    'architecture_logs.md',
    'c1_context/system_context.md',
    'c2_containers/containers_overview.md',
    'c5_dynamic_view/view_diagram.md',
    'c6_deployment/deployment_diagram.md',
    'c7_tests/tests_overview.md'
)

if (-not (Test-Path $archDir)) {
    New-Item -ItemType Directory -Path $archDir | Out-Null
}

function Get-ExpectedViews {
    param($JsonPath, $Fallback)
    if (-not $JsonPath) { return $Fallback }
    if (-not (Test-Path $JsonPath)) { return $Fallback }
    try {
        $data = Get-Content $JsonPath -Raw | ConvertFrom-Json -Depth 8
        $views = @()
        if ($data.views -and $data.views.PSObject.Properties.Count -gt 0) {
            foreach ($entry in $data.views.PSObject.Properties.Value) {
                if ($entry -and $entry.path) {
                    $path = $entry.path.ToString().Replace('\', '/')
                    $prefix = 'specs/architecture/'
                    if ($path.StartsWith($prefix)) {
                        $path = $path.Substring($prefix.Length)
                    }
                    if ($path.Trim() -ne '') {
                        $views += $path
                    }
                }
            }
        }
        if ($views.Count -eq 0) { $views = $Fallback }
        return $views
    }
    catch {
        return $Fallback
    }
}

$expectedViews = Get-ExpectedViews -JsonPath $architectureJsonPath -Fallback $defaultViews

$existingViews = @()
$missingViews = @()
foreach ($view in $expectedViews) {
    $candidate = Join-Path $archDir $view
    if (Test-Path $candidate) {
        $existingViews += $view
    }
    else {
        $missingViews += $view
    }
}

$modelVersion = $null
if (Test-Path $architectureJsonPath) {
    try {
        $jsonData = Get-Content $architectureJsonPath -Raw | ConvertFrom-Json -Depth 8
        $modelVersion = $jsonData.model_version
    }
    catch {
        $modelVersion = $null
    }
}

$result = [ordered]@{
    architecture_dir = $archDir
    readme = $readmePath
    overview = $overviewPath
    architecture_json = $architectureJsonPath
    architecture_log = $architectureLogPath
    model_version = $modelVersion
    expected_views = $expectedViews
    existing_views = $existingViews
    missing_views = $missingViews
}

$result | ConvertTo-Json -Depth 8
