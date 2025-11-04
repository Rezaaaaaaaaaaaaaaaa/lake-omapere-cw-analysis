$file = Get-Item "O:\TKIL2602\Working\Lake Omapere Trust\Lake_Omapere_CW_Analysis\Results\LAKE_OMAPERE_RESULTS_NEW\Data\Lake_Omapere_Analysis_Results.csv"
Write-Host "File: $($file.Name)"
Write-Host "Size: $([math]::Round($file.Length/1KB, 1)) KB"
$lines = (Get-Content $file.FullName | Measure-Object -Line).Lines
Write-Host "Lines: $lines"
Write-Host ""
Write-Host "Expected: 51 lines (50 reaches + 1 header)"
if ($lines -eq 51) {
    Write-Host "[OK] Correct number of Lake Omapere reaches"
} else {
    Write-Host "[ERROR] Wrong number of lines!"
}
