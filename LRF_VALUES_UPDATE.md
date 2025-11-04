# LRF Values Update - CW Practitioner Guide

**Date:** October 31, 2025
**Updated By:** Analysis update based on CW Practitioner Guide and MSCMM design report 1.0

---

## Summary of Changes

The Load Reduction Factor (LRF) values in the Lake Omapere CW analysis script have been updated to reflect the values from the **CW Practitioner Guide** and **MSCMM design report 1.0**.

### Previous Values (Incorrect)

The script previously used per-percentage-coverage factors that were multiplied by the actual coverage percentage:

| Category | Coverage Range | Previous LRF | Formula Used |
|----------|---------------|--------------|--------------|
| Low | <2% | 0.15 (15%) | `Load × (Coverage% / 100) × 0.15` |
| Medium | 2-4% | 0.18 (18%) | `Load × (Coverage% / 100) × 0.18` |
| High | >4% | 0.20 (20%) | `Load × (Coverage% / 100) × 0.20` |

**Problem:** This formula resulted in very small reductions. For example, a reach with 3% coverage would only get:
- `Load × (3/100) × 0.18 = Load × 0.54%` reduction (far too small)

### Updated Values (Correct)

Based on the **CW Practitioner Guide**:

| Category | Coverage Range | Updated LRF | Source |
|----------|---------------|-------------|---------|
| Low | <2% | **26%** (0.26) | CW Practitioner Guide |
| Medium | 2-4% | **42%** (0.42) | CW Practitioner Guide |
| High | >4% | **48%** (0.48) | CW Practitioner Guide |

**Note:** The MSCMM design report 1.0 used **23%** instead of 26% for the low category. We've adopted the CW Practitioner Guide value of 26%.

### New Formula

The reduction is now calculated as a **flat percentage** based on the category:

```python
CW_Reduction = Generated_Wetland_Load × LRF
```

Where LRF is simply 0.26, 0.42, or 0.48 depending on the coverage category.

**Example:** A reach with 3% coverage (medium category) now gets:
- `Load × 0.42 = 42% reduction` (correct)

---

## Technical Changes in Script

### File: `lake_omapere_cw_analysis.py`

**Change 1: LRF Factor Values (Lines 108-114)**

```python
# OLD:
LRF_FACTORS = {
    'low': 0.15,      # <2% coverage: 15% reduction per % coverage
    'medium': 0.18,   # 2-4% coverage: 18% reduction per % coverage
    'high': 0.20      # >4% coverage: 20% reduction per % coverage
}

# NEW:
LRF_FACTORS = {
    'low': 0.26,      # <2% coverage: 26% reduction
    'medium': 0.42,   # 2-4% coverage: 42% reduction
    'high': 0.48      # >4% coverage: 48% reduction
}
```

**Change 2: Reduction Formula (Lines 455-459)**

```python
# OLD:
results['cw_reduction'] = (results['generated_wetland'] *
                           (results['CW_Coverage_Percent'] / 100) *
                           results['lrf_factor'])

# NEW:
results['cw_reduction'] = (results['generated_wetland'] *
                           results['lrf_factor'])
```

**Change 3: Updated Documentation (Lines 389-408)**

The function docstring now clearly states:
- Formula: `CW_Reduction = Generated_Wetland × LRF`
- Specifies the source: CW Practitioner Guide
- Lists the explicit percentage values for each category

---

## Impact on Results

### Expected Changes:

1. **Much larger CW mitigation effects**
   - Previous: Reductions of ~0.5-2% per reach
   - Updated: Reductions of 26-48% per reach (depending on category)

2. **More realistic network amplification**
   - Total catchment-wide TP reduction will increase significantly
   - Network routing amplification will still apply (cascade effect)

3. **Better alignment with literature**
   - Values now match published CW effectiveness data
   - Consistent with CW Practitioner Guide recommendations
   - Matches MSCMM design report methodology

### Re-run Required:

The analysis **must be re-run** with the updated values to generate corrected results. Previous results are no longer valid.

---

## Coverage Categories (Unchanged)

The category thresholds remain the same:

| Category | Coverage Range | Definition |
|----------|---------------|------------|
| None | 0% | No CW coverage |
| Low | >0% to <2% | Minimal CW coverage |
| Medium | 2% to <4% | Moderate CW coverage |
| High | ≥4% | High CW coverage |

---

## References

1. **CW Practitioner Guide** - Source for LRF values (26%, 42%, 48%)
2. **MSCMM Design Report 1.0** - Alternative source (23%, 42%, 48%)

---

## Next Steps

1. ✓ **Update script values** - Completed
2. ⚠ **Re-run analysis** - Required with corrected LRF values
3. ⚠ **Regenerate all outputs** - Results, maps, and summaries
4. ⚠ **Update email to Fleur/Annette** - Reflect corrected methodology
5. ⚠ **Quality check results** - Verify reductions are realistic

---

## Version Control

- **Previous version:** LRF = 15-20% (per % coverage)
- **Current version:** LRF = 26-48% (flat percentage)
- **Script location:**
  - O:\TKIL2602\Working\Lake Omapere Trust\Lake_Omapere_CW_Analysis\Analysis_Scripts\
  - C:\Users\moghaddamr\Reza_CW_Analysis\Analysis_Scripts\

Both locations have been updated with the corrected values.

---

**Status:** ✓ Script updated and ready for re-analysis
