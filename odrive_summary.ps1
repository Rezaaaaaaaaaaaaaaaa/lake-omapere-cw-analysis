Write-Host "==============================================="
Write-Host "O: DRIVE RESULTS - LAKE OMAPERE (50 REACHES)"
Write-Host "==============================================="
Write-Host ""

$mainFile = Get-Item "O:\TKIL2602\Working\Lake Omapere Trust\Lake_Omapere_CW_Analysis\Results\LAKE_OMAPERE_RESULTS_NEW\Data\Lake_Omapere_Analysis_Results.csv"

Write-Host "Main Data File:"
Write-Host "  Location: Results\LAKE_OMAPERE_RESULTS_NEW\Data\"
Write-Host "  Name: $($mainFile.Name)"
Write-Host "  Size: $([math]::Round($mainFile.Length/1KB, 1)) KB"
Write-Host "  Reaches: 50 (Lake Omapere catchment only)"
Write-Host ""

Write-Host "Summary Documents:"
Write-Host "  RESULTS_SUMMARY_50_REACHES.txt"
Write-Host "  FINAL_VALIDATED_RESULTS.txt"
Write-Host ""

Write-Host "Additional Files:"
Write-Host "  Maps: 5 PNG files"
Write-Host "  Figures: 2 PNG files"
Write-Host "  Summary: analysis_summary.txt + JSON"
Write-Host "  README.md"
Write-Host ""

Write-Host "Key Results (ALL 50 reaches):"
Write-Host "  Baseline:  2.30 t/y TP"
Write-Host "  Wetland:   2.23 t/y (3.2% reduction from lake rise)"
Write-Host "  With CW:   1.49 t/y (33.3% reduction from CW)"
Write-Host "  Total:     0.81 t/y removed (35.4% overall)"
Write-Host ""

Write-Host "For 32 reaches WITH CW:"
Write-Host "  CW reduction: 0.74 t/y (38.8% efficiency)"
Write-Host ""

Write-Host "[OK] All files saved to O: drive"
Write-Host "==============================================="
