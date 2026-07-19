param(
    [int]$ContextSize = 98304,
    [ValidateSet('q8_0', 'q4_0')]
    [string]$CacheType = 'q4_0',
    [int]$MaxTokens = 4096,
    [int]$FitTargetMiB = 512
)

$llamaDir = 'C:\path\to\llama-cpp'
$arguments = @(
    '--host', '0.0.0.0',
    '--port', '8080',
    '--models-dir', 'C:\path\to\models',
    '--models-max', '1',
    '-c', $ContextSize,
    '--jinja',
    '-ngl', '99',
    '-fa', 'on',
    '-ctk', $CacheType,
    '-ctv', $CacheType,
    '-n', $MaxTokens,
    '--metrics'
)

if ($FitTargetMiB -gt 0) {
    $arguments += @('-fitt', $FitTargetMiB)
}

Push-Location $llamaDir
try {
    & (Join-Path $llamaDir 'llama-server.exe') @arguments
}
finally {
    Pop-Location
}
