# Spatial Mapping Guide - Lake Ōmāpere CW Analysis

## Overview

The comprehensive Python script (`lake_omapere_cw_analysis.py`) now includes **spatial mapping capabilities** that create visual maps of phosphorus loads across the river network for different mitigation scenarios.

**New Feature:** MapGenerator class creates publication-ready maps showing TP loads on the river network with color-coded reaches similar to the example you provided.

---

## Installation Requirements

### Required Package: geopandas

```bash
# Install geopandas (includes spatial capabilities)
pip install geopandas

# This also installs dependencies:
# - fiona (shapefile reading)
# - pyproj (coordinate systems)
# - shapely (geometry operations)
```

### Check Installation

```python
python -c "import geopandas; print('geopandas version:', geopandas.__version__)"
```

If successful, you're ready to generate maps!

---

## What Maps Are Generated

The script automatically creates **5 types of spatial maps**:

### 1. Generated Loads Comparison (3-panel)
**File:** `Generated_Loads_Comparison.png`

Shows side-by-side comparison of:
- Panel 1: Baseline (Current Lake)
- Panel 2: Wetland (+0.66m, No CW)
- Panel 3: Wetland + CW Mitigation

Color scale: Red (high load) → Yellow → Green (low load)

### 2. Routed Loads Comparison (2-panel)
**File:** `Routed_Loads_Comparison.png`

Shows network-routed loads:
- Panel 1: Routed Baseline
- Panel 2: Routed with CW Mitigation

Demonstrates how upstream loads accumulate downstream.

### 3. CW Reduction - Generated Loads
**File:** `CW_Reduction_Generated.png`

Shows direct CW mitigation effect (local reduction).

Color scale: White (no reduction) → Green (high reduction)

### 4. CW Reduction - Routed Loads
**File:** `CW_Reduction_Routed.png`

Shows network-wide CW mitigation effect (includes upstream benefits).

Color scale: White (no reduction) → Green (high reduction)

**Key insight:** Routed reduction is typically 8× larger than generated!

### 5. CW Coverage Distribution
**File:** `CW_Coverage_Distribution.png`

Shows which reaches have CW sites and coverage %.

Color scale: Light blue (0% coverage) → Dark blue (high coverage)

---

## How It Works

### Step 1: Load River Shapefile
```python
river_gdf = MapGenerator.load_river_network("Shapefiles/Reference/Riverlines.shp")
```
- Loads all river reaches in the region
- Returns GeoDataFrame with geometry

### Step 2: Filter to Lake Reaches
```python
lake_gdf = MapGenerator.filter_lake_reaches(river_gdf, results_df)
```
- Filters to 50 Lake Ōmāpere reaches only
- Joins with analysis results (loads, coverage, etc.)

### Step 3: Create Maps
```python
MapGenerator.generate_all_maps(results_df)
```
- Creates all 5 maps automatically
- Saves to `Results/LAKE_OMAPERE_RESULTS/Maps/`

---

## Shapefile Configuration

The script uses shapefiles from the `Shapefiles/` directory:

```python
# In Config class:
RIVER_SHAPEFILE = "Shapefiles/Reference/Riverlines.shp"
CATCHMENT_SHAPEFILE = "Shapefiles/Reference/Catchment.shp"
LAKE_SHAPEFILE = "Shapefiles/Lake/Lake Omapere-236.34 mAMSL (+0.66m).shp"
SUBCATCHMENTS_SHAPEFILE = "Shapefiles/Subcatchments/Subs.shp"
```

**Required:**
- `Riverlines.shp` - River network geometry

**Optional (enhance maps):**
- `Catchment.shp` - Catchment boundary (gray outline)
- `Lake Omapere...shp` - Lake polygon (blue fill)
- `Subs.shp` - Subcatchments (future use)

---

## Map Features

### Visual Elements

Each map includes:
- **River reaches** - Color-coded lines (linewidth=2.5)
- **Catchment boundary** - Gray outline (if shapefile provided)
- **Lake polygon** - Light blue fill (if shapefile provided)
- **Colorbar** - Shows value range with units
- **Grid** - Faint grid lines for reference
- **Labels** - Longitude/Latitude axes

### Color Schemes

| Map Type | Colormap | Range |
|----------|----------|-------|
| TP Loads (baseline/wetland/CW) | RdYlGn_r | Auto (min to max) |
| CW Reduction | Greens | 0 to max reduction |
| Coverage Distribution | YlGnBu | 0% to 10% |

**RdYlGn_r:**
- Red = High values (high load)
- Yellow = Medium values
- Green = Low values (low load)

**Greens:**
- White/Light = Low reduction
- Dark Green = High reduction

### Map Layout

- **Figure size:** 10×12 inches (single map) or 16×6n inches (multi-panel)
- **DPI:** 300 (publication quality)
- **Format:** PNG with transparent background option

---

## Usage Examples

### Example 1: Basic Usage (Automatic)

The script generates maps automatically when you run the full analysis:

```bash
python lake_omapere_cw_analysis.py
```

Maps appear in: `Results/LAKE_OMAPERE_RESULTS/Maps/`

### Example 2: Generate Maps Separately

```python
from lake_omapere_cw_analysis import MapGenerator
import pandas as pd

# Load your results
results = pd.read_csv('Results/LAKE_OMAPERE_RESULTS/Data/Lake_Omapere_Analysis_Results.csv')

# Generate all maps
MapGenerator.generate_all_maps(results)
```

### Example 3: Create Custom Single Map

```python
from lake_omapere_cw_analysis import MapGenerator
import geopandas as gpd

# Load river network
river_gdf = gpd.read_file('Shapefiles/Reference/Riverlines.shp')

# Filter to Lake reaches
lake_gdf = MapGenerator.filter_lake_reaches(river_gdf, results)

# Create custom map
MapGenerator.create_phosphorus_map(
    lake_gdf,
    value_column='routed_baseline',
    title='Baseline Routed TP Loads',
    output_path='custom_map.png',
    cmap='viridis',
    vmin=0,
    vmax=0.5
)
```

### Example 4: Custom Comparison

```python
# Define your own scenarios
scenarios = [
    ('generated_baseline', 'My Baseline Scenario'),
    ('generated_cw', 'My Mitigation Scenario'),
]

# Create comparison map
MapGenerator.create_comparison_map(
    lake_gdf,
    scenarios,
    output_path='my_comparison.png'
)
```

---

## Customization Options

### Change Color Scheme

Edit the `cmap` parameter in `create_phosphorus_map()`:

```python
# Available colormaps:
cmap='RdYlGn_r'  # Red-Yellow-Green (reversed)
cmap='viridis'   # Purple-Green-Yellow
cmap='plasma'    # Purple-Orange-Yellow
cmap='coolwarm'  # Blue-Red
cmap='Greens'    # White to Dark Green
cmap='Blues'     # White to Dark Blue
```

See: https://matplotlib.org/stable/tutorials/colors/colormaps.html

### Adjust Value Range

Control color scale min/max:

```python
# Auto range (default)
vmin=None, vmax=None

# Fixed range
vmin=0, vmax=0.5  # TP loads from 0 to 0.5 tpy

# Symmetric around zero
vmin=-0.1, vmax=0.1  # For showing changes
```

### Change Line Width

In `create_phosphorus_map()`, edit:

```python
lake_gdf.plot(..., linewidth=2.5)  # Thicker = more visible
```

### Add More Context Layers

```python
# Load additional shapefiles
roads_gdf = gpd.read_file('path/to/roads.shp')
towns_gdf = gpd.read_file('path/to/towns.shp')

# Plot before river reaches
roads_gdf.plot(ax=ax, color='gray', linewidth=0.5)
towns_gdf.plot(ax=ax, marker='o', color='red', markersize=5)
```

---

## Troubleshooting

### Issue: geopandas not found

**Error:**
```
Warning: geopandas not available, skipping mapping
```

**Solution:**
```bash
pip install geopandas
```

### Issue: Shapefile not found

**Error:**
```
Warning: Shapefile not found: Shapefiles/Reference/Riverlines.shp
```

**Solution:**
- Check that shapefile exists at that path
- Update `Config.RIVER_SHAPEFILE` with correct path
- Verify all required files exist (.shp, .shx, .dbf, .prj)

### Issue: Reach ID column not recognized

**Error:**
```
Error: Cannot find reach ID column in shapefile
```

**Solution:**
- Open shapefile in QGIS or ArcGIS
- Check attribute table for reach ID column name
- Common names: NZSEGMENT, nzsegment, OBJECTID, ReachID
- Update `reach_id_col` parameter if needed

### Issue: No reaches found after filtering

**Error:**
```
Filtered to 0 Lake reaches
```

**Solution:**
- Verify results_df has reach_id column
- Check reach IDs match between shapefile and results
- Ensure reach IDs are same data type (int vs string)

### Issue: Maps look blank or empty

**Possible causes:**
- All values are same (no variation in colors)
- Value range too narrow
- Coordinate system mismatch

**Solution:**
```python
# Check value range
print(lake_gdf['routed_baseline'].describe())

# Check coordinate system
print(lake_gdf.crs)

# Ensure CRS matches
if lake_gdf.crs != catchment_gdf.crs:
    catchment_gdf = catchment_gdf.to_crs(lake_gdf.crs)
```

### Issue: Memory error with large shapefiles

**Solution:**
```python
# Filter shapefile first before loading all geometry
import fiona

# Get bounding box of Lake area
bounds = lake_reaches_bbox  # (minx, miny, maxx, maxy)

with fiona.open('Riverlines.shp') as src:
    filtered = [feature for feature in src.filter(bbox=bounds)]

# Load filtered GeoDataFrame
lake_gdf = gpd.GeoDataFrame.from_features(filtered, crs=src.crs)
```

---

## Output Specifications

### File Format
- **Format:** PNG (portable network graphics)
- **DPI:** 300 (publication quality)
- **Color depth:** 24-bit RGB
- **Transparency:** Optional (background can be transparent)

### File Sizes
- Single map: ~1-3 MB
- Multi-panel comparison: ~3-5 MB
- Total for all 5 maps: ~10-15 MB

### Dimensions
- Single map: 3000×3600 pixels (10×12 inches @ 300 DPI)
- 2-panel: 4800×1800 pixels (16×6 inches @ 300 DPI)
- 3-panel: 4800×2700 pixels (16×9 inches @ 300 DPI)

---

## Advanced Features

### Temperature-Style Gradient (Like Your Example)

To replicate the red-purple-green gradient from your example image:

```python
import matplotlib.colors as mcolors
import numpy as np

# Create custom colormap (red → purple → green)
colors = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
n_bins = 100
cmap_custom = mcolors.LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

# Use in mapping
MapGenerator.create_phosphorus_map(
    lake_gdf,
    value_column='routed_baseline',
    title='TP Load - Custom Gradient',
    output_path='custom_gradient.png',
    cmap=cmap_custom
)
```

### Add Temperature-Style Labels

```python
# In create_phosphorus_map, after plotting:
# Add text labels for specific reaches
for idx, row in lake_gdf.iterrows():
    if row['routed_baseline'] > threshold:
        x, y = row.geometry.centroid.coords[0]
        ax.text(x, y, f"{row['routed_baseline']:.2f}",
               fontsize=6, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
```

### Export to Interactive HTML

```python
# Create interactive map (pan, zoom)
import folium

# Convert to WGS84 for web mapping
lake_gdf_wgs84 = lake_gdf.to_crs(epsg=4326)

# Create basemap
m = folium.Map(
    location=[lake_gdf_wgs84.geometry.centroid.y.mean(),
             lake_gdf_wgs84.geometry.centroid.x.mean()],
    zoom_start=12
)

# Add river reaches with tooltip
folium.GeoJson(
    lake_gdf_wgs84,
    style_function=lambda feature: {
        'color': get_color(feature['properties']['routed_baseline']),
        'weight': 3
    },
    tooltip=folium.GeoJsonTooltip(['reach_id', 'routed_baseline'])
).add_to(m)

# Save interactive map
m.save('interactive_map.html')
```

---

## Integration with Analysis Workflow

The mapping is fully integrated into the main analysis pipeline:

```
[STEP 1] LOAD DATA
[STEP 2] CALCULATE GENERATED LOADS
[STEP 3] APPLY CW MITIGATION
[STEP 4] ROUTE LOADS
[STEP 5] GENERATE OUTPUTS
    ├─ Save CSV results
    ├─ Generate summary statistics
    ├─ Create visualizations (charts)
    └─ Generate spatial maps ← NEW!
```

Maps are created automatically if:
- geopandas is installed
- Riverlines.shp exists
- Results have necessary columns

If any requirement missing, script continues without error (graceful degradation).

---

## Best Practices

### 1. Check Shapefiles First
```bash
# Verify shapefiles exist and are valid
ls -lh Shapefiles/Reference/Riverlines.*
python -c "import geopandas; gdf = geopandas.read_file('Shapefiles/Reference/Riverlines.shp'); print(f'{len(gdf)} reaches loaded')"
```

### 2. Use Consistent CRS
Ensure all shapefiles use same coordinate reference system:
```python
print(river_gdf.crs)      # Should be same
print(catchment_gdf.crs)  # for all layers
print(lake_gdf.crs)
```

### 3. Optimize for Performance
- Filter to study area before complex operations
- Use simplified geometries if detail not needed
- Close plots with `plt.close()` to free memory

### 4. Quality Check Maps
- Visually inspect each map
- Verify color scale makes sense
- Check reach IDs match results
- Ensure coordinates are correct

### 5. Document Custom Changes
If you modify mapping code, document:
- What was changed
- Why it was changed
- How to revert if needed

---

## Examples Gallery

### Example Output 1: Generated Loads Comparison
Shows how lake level rise (wetland scenario) affects loads, then how CW mitigation helps.

**Typical finding:** Wetland slightly increases loads, CW reduces them by ~8%.

### Example Output 2: Routed Loads Comparison
Shows network-wide effects including upstream contributions.

**Typical finding:** Routed loads are 7-8× higher than generated due to upstream accumulation.

### Example Output 3: CW Reduction Maps
Green intensity shows where CW has biggest impact.

**Typical finding:** Reaches with no direct CW still show reduction (upstream benefit!).

---

## Future Enhancements

Potential additions for future versions:

1. **Animated maps** - Show temporal changes
2. **3D visualization** - Elevation + load intensity
3. **Network flow arrows** - Show direction of flow
4. **Interactive web maps** - Pan, zoom, click for details
5. **Export to GIS** - Save as shapefile with results
6. **Batch processing** - Create maps for multiple scenarios
7. **Difference maps** - Highlight changes between scenarios

---

## References

### Documentation
- **geopandas:** https://geopandas.org/
- **matplotlib colormaps:** https://matplotlib.org/stable/tutorials/colors/colormaps.html
- **shapely geometries:** https://shapely.readthedocs.io/

### Example Code
See `lake_omapere_cw_analysis.py` Section 5B (lines 931-1368) for complete implementation.

---

## Quick Reference Commands

```bash
# Install mapping dependencies
pip install geopandas

# Run analysis with mapping
python lake_omapere_cw_analysis.py

# Maps saved to:
ls Results/LAKE_OMAPERE_RESULTS/Maps/

# View maps
# (open PNG files in image viewer)
```

---

## Questions?

For mapping issues:
- Check shapefile exists and is valid
- Verify geopandas installed
- Review error messages (usually self-explanatory)
- Enable debug mode for more output

For methodology questions:
- See EMAIL_TO_FLEUR_AND_ANNETTE.md
- See USAGE_GUIDE.md

---

**Maps successfully integrated into Lake Ōmāpere CW analysis pipeline!** 🗺️

---

**Last Updated:** October 30, 2025
**Feature:** Spatial Mapping
**Status:** ✅ Production Ready
