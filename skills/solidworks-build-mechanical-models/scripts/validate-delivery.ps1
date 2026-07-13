[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [string]$Assembly,

    [int]$ExpectedPartCount = -1,

    [string]$Video,

    [double]$ExpectedVideoDuration = -1,

    [double]$DurationTolerance = 1.0,

    [switch]$RequireBuildComplete
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()

$resolvedOutput = Resolve-Path -LiteralPath $OutputDirectory -ErrorAction SilentlyContinue
if (-not $resolvedOutput) {
    Write-Error "Output directory does not exist: $OutputDirectory"
    exit 1
}

$outputPath = $resolvedOutput.Path
$parts = @(Get-ChildItem -LiteralPath $outputPath -Filter '*.SLDPRT' -File)
$assemblies = @(Get-ChildItem -LiteralPath $outputPath -Filter '*.SLDASM' -File)
$emptyCadFiles = @(Get-ChildItem -LiteralPath $outputPath -File | Where-Object {
    $_.Extension -in '.SLDPRT', '.SLDASM' -and $_.Length -eq 0
})

if ($ExpectedPartCount -ge 0 -and $parts.Count -ne $ExpectedPartCount) {
    $failures.Add("Expected $ExpectedPartCount part files; found $($parts.Count).")
}
if ($emptyCadFiles.Count -gt 0) {
    $failures.Add("Zero-byte CAD files: $($emptyCadFiles.Name -join ', ')")
}

if ($Assembly) {
    if (-not (Test-Path -LiteralPath $Assembly -PathType Leaf)) {
        $failures.Add("Assembly does not exist: $Assembly")
    } elseif ((Get-Item -LiteralPath $Assembly).Length -eq 0) {
        $failures.Add("Assembly is empty: $Assembly")
    }
} elseif ($assemblies.Count -eq 0) {
    $failures.Add('No .SLDASM file was found.')
}

$logPath = Join-Path $outputPath 'build_log.txt'
$logComplete = $false
$logErrors = @()
if (Test-Path -LiteralPath $logPath -PathType Leaf) {
    $logLines = @(Get-Content -LiteralPath $logPath)
    $logComplete = [bool]($logLines -match 'BUILD_COMPLETE')
    $logErrors = @($logLines -match 'ERROR:')
} elseif ($RequireBuildComplete) {
    $failures.Add("Missing build log: $logPath")
}

if ($RequireBuildComplete -and -not $logComplete) {
    $failures.Add('build_log.txt does not contain BUILD_COMPLETE.')
}
if ($logErrors.Count -gt 0) {
    $failures.Add("build_log.txt contains $($logErrors.Count) ERROR line(s).")
}

$videoMetadata = $null
if ($Video) {
    if (-not (Test-Path -LiteralPath $Video -PathType Leaf)) {
        $failures.Add("Video does not exist: $Video")
    } else {
        $ffprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
        if (-not $ffprobe) {
            $failures.Add('ffprobe is required to validate video metadata.')
        } else {
            $json = & $ffprobe.Source -v error -show_entries `
                'format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate,pix_fmt' `
                -of json -- $Video
            if ($LASTEXITCODE -ne 0) {
                $failures.Add("ffprobe failed for: $Video")
            } else {
                $videoMetadata = $json | ConvertFrom-Json
                $duration = [double]$videoMetadata.format.duration
                if ($ExpectedVideoDuration -ge 0 -and
                    [math]::Abs($duration - $ExpectedVideoDuration) -gt $DurationTolerance) {
                    $failures.Add("Video duration $duration s is outside expected $ExpectedVideoDuration +/- $DurationTolerance s.")
                }
            }
        }
    }
}

$summary = [ordered]@{
    ok = ($failures.Count -eq 0)
    output_directory = $outputPath
    part_count = $parts.Count
    assembly_count = $assemblies.Count
    build_complete = $logComplete
    log_error_count = $logErrors.Count
    video = $videoMetadata
    failures = @($failures)
}

$summary | ConvertTo-Json -Depth 8
if ($failures.Count -gt 0) { exit 1 }
exit 0
