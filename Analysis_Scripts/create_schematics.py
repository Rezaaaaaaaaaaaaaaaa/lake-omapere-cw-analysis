"""
Create comprehensive schematics for Lake Ōmāpere CW mitigation project
Exports to PDF with diagrams showing model structure, inputs, and data flows
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import os
import pandas as pd
from datetime import datetime

# Set up the style
plt.style.use('default')
colors = {
    'input': '#E8F4F8',
    'process': '#B8E6F0',
    'output': '#FFE8CC',
    'scenario': '#E8F8E8',
    'data': '#F0E8F8',
    'header': '#2C3E50'
}

def create_page_title(fig, title, subtitle=""):
    """Add a professional title to a figure"""
    fig.suptitle(title, fontsize=20, fontweight='bold', y=0.98)
    if subtitle:
        fig.text(0.5, 0.94, subtitle, ha='center', fontsize=12, style='italic', color='#555555')

def draw_box(ax, x, y, width, height, text, color='lightblue', fontsize=10):
    """Draw a rounded rectangle box"""
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.1",
                         edgecolor='#333333', facecolor=color,
                         linewidth=2)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            weight='bold', wrap=True, multialignment='center')

def draw_arrow(ax, x1, y1, x2, y2, label=""):
    """Draw an arrow between two points"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=30,
                           color='#333333', linewidth=2.5)
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, fontsize=9, style='italic',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# ============================================================================
# PAGE 1: Overall Project Architecture
# ============================================================================
fig1 = plt.figure(figsize=(11, 14))
ax1 = fig1.add_subplot(111)
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 14)
ax1.axis('off')

create_page_title(fig1, "Lake Ōmāpere CW Mitigation Project",
                  "Overall Architecture & Data Flow")

# CLUES Data Sources
draw_box(ax1, 2, 12.5, 3, 0.8, "CLUES Spreadsheets\n(Baseline & +0.66m)",
         colors['input'], 10)
draw_box(ax1, 8, 12.5, 3, 0.8, "GIS Shapefiles\n(CW Sites, Lake)",
         colors['input'], 10)

# Intermediate Processing
draw_box(ax1, 2, 10.5, 3, 0.8, "Extract TP Loads\nCLUESloads.csv",
         colors['process'], 10)
draw_box(ax1, 8, 10.5, 3, 0.8, "Calculate CW Coverage\nby Subcatchment",
         colors['process'], 10)

# Arrows down
draw_arrow(ax1, 2, 12.1, 2, 10.9)
draw_arrow(ax1, 8, 12.1, 8, 10.9)

# Attenuation Data
draw_box(ax1, 5, 9, 3, 0.8, "Update Attenuation\nAttenCarry.csv",
         colors['process'], 10)
draw_arrow(ax1, 2, 10.1, 4.5, 9.4)
draw_arrow(ax1, 8, 10.1, 5.5, 9.4)

# Selection & Placement Rules
draw_box(ax1, 2, 7.2, 3, 0.8, "Selection CSV\n(50 reaches)",
         colors['data'], 10)
draw_box(ax1, 8, 7.2, 3, 0.8, "Placement Rules\n(CW from GIS)",
         colors['data'], 10)

draw_arrow(ax1, 5, 8.6, 2.5, 7.6)
draw_arrow(ax1, 5, 8.6, 7.5, 7.6)

# Scenario Configuration
draw_box(ax1, 5, 5.5, 3.5, 0.8, "Scenario Lookups\n(LRF thresholds)",
         colors['scenario'], 10)
draw_arrow(ax1, 2, 6.8, 4.2, 5.9)
draw_arrow(ax1, 8, 6.8, 5.8, 5.9)

# Models (Side by Side)
draw_box(ax1, 1.5, 3.5, 2.5, 1.2, "StandAloneDNZ2.py\nBaseline Model\nNo CW Mitigation",
         colors['process'], 9)
draw_box(ax1, 5, 3.5, 2.5, 1.2, "StandAloneDNZ2_\nWetland066m.py\n+0.66m Lake Level",
         colors['process'], 9)
draw_box(ax1, 8.5, 3.5, 2.5, 1.2, "LakeOmapere_\nRouting_Template.py\nRouting & Reduction",
         colors['process'], 9)

# Arrows from scenarios to models
draw_arrow(ax1, 3.5, 5.1, 1.8, 4.1)
draw_arrow(ax1, 5, 5.1, 5, 4.1)
draw_arrow(ax1, 6.5, 5.1, 8.2, 4.1)

# Outputs
draw_box(ax1, 1.5, 1.5, 2.5, 1, "Baseline\nResults\nTP Loads\nConcentrations",
         colors['output'], 9)
draw_box(ax1, 5, 1.5, 2.5, 1, "Wetland\nScenario\nResults\nTP Loads",
         colors['output'], 9)
draw_box(ax1, 8.5, 1.5, 2.5, 1, "Analysis\nResults\nLoad\nReductions",
         colors['output'], 9)

# Arrows to outputs
draw_arrow(ax1, 1.5, 2.9, 1.5, 2.0)
draw_arrow(ax1, 5, 2.9, 5, 2.0)
draw_arrow(ax1, 8.5, 2.9, 8.5, 2.0)

plt.tight_layout()

# ============================================================================
# PAGE 2: Model Inputs Detail
# ============================================================================
fig2 = plt.figure(figsize=(11, 14))
ax2 = fig2.add_subplot(111)
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 14)
ax2.axis('off')

create_page_title(fig2, "Model Input Files & Data Structure",
                  "InputData/, SelectionFiles/, and Lookups/ Directories")

# CLUES Loads
draw_box(ax2, 2.5, 12.5, 2.5, 0.8, "CLUESloads\n_baseline.csv", colors['input'], 9)
draw_box(ax2, 2.5, 11.3, 2.5, 1, "Columns:\n- TPAgGen\n- soilP\n- TPGen\n- TPps", colors['data'], 8)

draw_box(ax2, 7.5, 12.5, 2.5, 0.8, "CLUESloads\n_wetland_066m.csv", colors['input'], 9)
draw_box(ax2, 7.5, 11.3, 2.5, 1, "Same structure\nUpdated TP loads\nfor 0.66m scenario", colors['data'], 8)

# Attenuation Files
draw_box(ax2, 2.5, 9.3, 2.5, 0.8, "AttenCarry\n_baseline.csv", colors['input'], 9)
draw_box(ax2, 2.5, 8.3, 2.5, 1, "Columns:\n- PstreamCarry\n- PresCarry\n- By reach", colors['data'], 8)

draw_box(ax2, 7.5, 9.3, 2.5, 0.8, "AttenCarry\n_wetland_066m.csv", colors['input'], 9)
draw_box(ax2, 7.5, 8.3, 2.5, 1, "Same structure\nUpdated for\nlake rise impact", colors['data'], 8)

# Selection & CW Data
draw_box(ax2, 2.5, 6.3, 2.5, 0.8, "LakeOmapere\n_Selection.csv", colors['input'], 9)
draw_box(ax2, 2.5, 5.3, 2.5, 1, "Columns:\n- Reach ID\n- Selection (0/1)\nFor 50 reaches", colors['data'], 8)

draw_box(ax2, 7.5, 6.3, 2.5, 0.8, "CW_\nSubcatchments.csv", colors['input'], 9)
draw_box(ax2, 7.5, 5.3, 2.5, 1, "Columns:\n- Subcatchment ID\n- CW coverage %\n34 subcatchments", colors['data'], 8)

# Scenario & LRF Lookups
draw_box(ax2, 2.5, 3.3, 2.5, 0.8, "Scenarios_\nLakeOmapere.xlsx", colors['scenario'], 9)
draw_box(ax2, 2.5, 2.3, 2.5, 1, "3 LRF scenarios:\n<2% coverage\n2-4% coverage\n>4% coverage", colors['data'], 8)

draw_box(ax2, 7.5, 3.3, 2.5, 0.8, "LRFs_\nyears.xlsx", colors['scenario'], 9)
draw_box(ax2, 7.5, 2.3, 2.5, 1, "LRF values by:\n- Coverage level\n- Time period\nFor P reduction", colors['data'], 8)

plt.tight_layout()

# ============================================================================
# PAGE 3: Model Configuration & Processing
# ============================================================================
fig3 = plt.figure(figsize=(11, 14))
ax3 = fig3.add_subplot(111)
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 14)
ax3.axis('off')

create_page_title(fig3, "Model Configuration & Processing Logic",
                  "StandAloneDNZ2.py & StandAloneDNZ2_Wetland066m.py")

# Left side - Baseline Model
ax3.text(2.5, 13.2, "BASELINE MODEL", fontsize=12, weight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor=colors['process'], edgecolor='black', linewidth=2))

draw_box(ax3, 2.5, 12.3, 3, 0.7, "Lake Area: Current\nNo CW Mitigation", colors['input'], 9)
draw_box(ax3, 2.5, 11, 3, 1.2, "Configuration:\n- Load all input CSVs\n- Set reach selection\n- Initialize GIS", colors['process'], 9)
draw_box(ax3, 2.5, 9.3, 3, 1.2, "Placement Rules:\n- Read CW shapefile\n- Identify eligible\n  subcatchments\n- Set mitigation = 0", colors['process'], 9)
draw_box(ax3, 2.5, 7.3, 3, 1.2, "Calculate TP:\n- Baseline loads\n- Reach routing\n- Attenuation\n- No reduction", colors['process'], 9)
draw_box(ax3, 2.5, 5.3, 3, 1.2, "Output Generation:\n- GenSS TP by reach\n- Load increments\n- Concentration (mg/L)", colors['output'], 9)

# Arrows down left side
for y_start, y_end in [(12, 11.6), (11, 9.9), (9.3, 7.9), (7.3, 5.9)]:
    draw_arrow(ax3, 2.5, y_start, 2.5, y_end)

# Right side - Wetland Model
ax3.text(7.5, 13.2, "WETLAND SCENARIO", fontsize=12, weight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor=colors['scenario'], edgecolor='black', linewidth=2))

draw_box(ax3, 7.5, 12.3, 3, 0.7, "Lake Area: +0.66m\nWith CW Mitigation", colors['input'], 9)
draw_box(ax3, 7.5, 11, 3, 1.2, "Configuration:\n- Load wetland CSVs\n- Updated attenuation\n- GIS with new lake", colors['process'], 9)
draw_box(ax3, 7.5, 9.3, 3, 1.2, "Placement Rules:\n- Read CW shapefile\n- Override rule:\n  if CW in GIS → mitigation=1\n  else → 0", colors['process'], 9)
draw_box(ax3, 7.5, 7.3, 3, 1.2, "Calculate TP:\n- With CW removal\n- Apply LRF values\n- Based on coverage %\n- Attenuation", colors['process'], 9)
draw_box(ax3, 7.5, 5.3, 3, 1.2, "Output Generation:\n- GenSS TP (reduced)\n- Removal efficiency\n- Concentration (mg/L)", colors['output'], 9)

# Arrows down right side
for y_start, y_end in [(12, 11.6), (11, 9.9), (9.3, 7.9), (7.3, 5.9)]:
    draw_arrow(ax3, 7.5, y_start, 7.5, y_end)

# Comparison box
draw_box(ax3, 5, 3.3, 4, 1.2, "COMPARISON & ANALYSIS\nBaseline vs Wetland Scenario\nCalculate: Load reduction, % reduction, concentration change",
         colors['scenario'], 10)

draw_arrow(ax3, 2.5, 4.7, 4, 3.9)
draw_arrow(ax3, 7.5, 4.7, 6, 3.9)

# Final output
draw_box(ax3, 5, 1.5, 4, 1.2, "RESULTS EXPORT\nGenerated loads CSV\nTP reduction by reach\nScenario comparison",
         colors['output'], 10)

draw_arrow(ax3, 5, 2.7, 5, 2.1)

plt.tight_layout()

# ============================================================================
# PAGE 4: Data Flow Diagram
# ============================================================================
fig4 = plt.figure(figsize=(11, 14))
ax4 = fig4.add_subplot(111)
ax4.set_xlim(0, 10)
ax4.set_ylim(0, 14)
ax4.axis('off')

create_page_title(fig4, "Complete Data Flow & Processing Pipeline",
                  "From CLUES to Final Analysis")

# Top - Source Data
y_pos = 13
ax4.text(5, y_pos, "SOURCE DATA", fontsize=11, weight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor='#FFD700', alpha=0.7, edgecolor='black', linewidth=2))

# Sources
draw_box(ax4, 1.5, y_pos - 1.2, 2, 0.8, "CLUES\nSpreadsheets", colors['input'], 9)
draw_box(ax4, 5, y_pos - 1.2, 2, 0.8, "GIS\nShapefiles", colors['input'], 9)
draw_box(ax4, 8.5, y_pos - 1.2, 2, 0.8, "Field\nSurveys", colors['input'], 9)

# Processing tier 1
y_pos = 10.5
ax4.text(5, y_pos, "DATA PREPARATION", fontsize=11, weight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor='#87CEEB', alpha=0.7, edgecolor='black', linewidth=2))

draw_box(ax4, 2, y_pos - 1.3, 2.2, 1, "Extract\nTP Loads\nby Reach", colors['process'], 8)
draw_box(ax4, 5, y_pos - 1.3, 2.2, 1, "Calculate\nCW Coverage\nby Subcatch", colors['process'], 8)
draw_box(ax4, 8, y_pos - 1.3, 2.2, 1, "Update\nAttenuation\nFactors", colors['process'], 8)

# Processing tier 2
y_pos = 8
ax4.text(5, y_pos, "MODEL CONFIGURATION", fontsize=11, weight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor='#90EE90', alpha=0.7, edgecolor='black', linewidth=2))

draw_box(ax4, 3, y_pos - 1.3, 2.2, 1, "Create\nSelection\nCSV", colors['scenario'], 8)
draw_box(ax4, 7, y_pos - 1.3, 2.2, 1, "Setup\nPlacement\nRules", colors['scenario'], 8)

# Core Models
y_pos = 5.5
ax4.text(5, y_pos, "MODEL EXECUTION", fontsize=11, weight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor='#FFB6C1', alpha=0.7, edgecolor='black', linewidth=2))

draw_box(ax4, 2.5, y_pos - 1.4, 2.5, 1.2, "StandAloneDNZ2\n.py\n\nBASELINE\nModel Run", colors['process'], 8)
draw_box(ax4, 7.5, y_pos - 1.4, 2.5, 1.2, "StandAloneDNZ2\n_Wetland066m.py\n\nWETLAND\nModel Run", colors['process'], 8)

# Analysis & Comparison
y_pos = 2.5
ax4.text(5, y_pos, "ANALYSIS & OUTPUTS", fontsize=11, weight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor='#DDA0DD', alpha=0.7, edgecolor='black', linewidth=2))

draw_box(ax4, 2.5, y_pos - 1.3, 2.2, 1, "Baseline\nResults\nTP Loads", colors['output'], 8)
draw_box(ax4, 5, y_pos - 1.3, 2.2, 1, "Comparison\n& Analysis\nReductions", colors['output'], 8)
draw_box(ax4, 7.5, y_pos - 1.3, 2.2, 1, "Routing &\nReporting\nMaps/Tables", colors['output'], 8)

# Draw connecting lines
draw_arrow(ax4, 1.5, 11.8, 2, 10.2)
draw_arrow(ax4, 5, 11.8, 5, 10.2)
draw_arrow(ax4, 8.5, 11.8, 8, 10.2)

draw_arrow(ax4, 2.5, 8.7, 3, 7.4)
draw_arrow(ax4, 8, 8.7, 7, 7.4)

draw_arrow(ax4, 3.5, 6.2, 2.5, 5.4)
draw_arrow(ax4, 6.5, 6.2, 7.5, 5.4)

draw_arrow(ax4, 2.5, 4.1, 2.5, 3.6)
draw_arrow(ax4, 7.5, 4.1, 5, 3.6)
draw_arrow(ax4, 7.5, 4.1, 7.5, 3.6)

plt.tight_layout()

# ============================================================================
# PAGE 5: Scenario Comparison
# ============================================================================
fig5 = plt.figure(figsize=(11, 14))
ax5 = fig5.add_subplot(111)
ax5.set_xlim(0, 10)
ax5.set_ylim(0, 14)
ax5.axis('off')

create_page_title(fig5, "Scenario Comparison & Analysis Strategy",
                  "Baseline vs Wetland CW Mitigation")

# Baseline Scenario
ax5.text(2.5, 12.8, "SCENARIO 1: BASELINE", fontsize=11, weight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor=colors['process'], edgecolor='black', linewidth=2))

draw_box(ax5, 2.5, 11.8, 3.2, 1.2, "Lake Area: Current\nNo CW Implementation\nNo TP Removal\nBaseline Conditions", colors['input'], 9)

baseline_items = [
    ("10.5", "Model Configuration", "- Current CLUES loads\n- Baseline attenuation\n- Current GIS layer"),
    ("9.5", "Processing", "- Read 50 reaches\n- No mitigation applied\n- Standard routing"),
    ("7.5", "Outputs", "- Baseline TP loads\n- Reach concentrations\n- Loads by reach"),
]

for y, title, content in baseline_items:
    draw_box(ax5, 2.5, float(y), 3.2, 1.3, f"{title}\n{content}", colors['data'], 8)
    if y != baseline_items[-1][0]:
        draw_arrow(ax5, 2.5, float(y) - 0.65, 2.5, float(y) - 0.95)

# Wetland Scenario
ax5.text(7.5, 12.8, "SCENARIO 2: WETLAND (CW MITIGATION)", fontsize=11, weight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor=colors['scenario'], edgecolor='black', linewidth=2))

draw_box(ax5, 7.5, 11.8, 3.2, 1.2, "Lake Area: +0.66m\nCW Implementation\nSurface & GW CW\nRemoval: <2%, 2-4%, >4%", colors['input'], 9)

wetland_items = [
    ("10.5", "Model Configuration", "- Updated CLUES loads\n- Revised attenuation\n- New lake GIS layer"),
    ("9.5", "CW Processing", "- Apply CW placement\n- Determine coverage %\n- Select LRF values"),
    ("7.5", "TP Calculation", "- Apply removal rates\n- Calculate reductions\n- New concentrations"),
]

for y, title, content in wetland_items:
    draw_box(ax5, 7.5, float(y), 3.2, 1.3, f"{title}\n{content}", colors['scenario'], 8)
    if y != wetland_items[-1][0]:
        draw_arrow(ax5, 7.5, float(y) - 0.65, 7.5, float(y) - 0.95)

# Comparison section
draw_box(ax5, 5, 5.3, 4, 1.5, "COMPARISON & ANALYSIS\n\nCalculate for each reach:\n• Load difference = Baseline - Wetland\n• % reduction = (Difference / Baseline) × 100\n• Concentration change (mg/L)\n• Effectiveness by subcatchment",
         colors['output'], 9)

draw_arrow(ax5, 2.5, 6.6, 3.8, 5.8)
draw_arrow(ax5, 7.5, 6.6, 6.2, 5.8)

# Results
draw_box(ax5, 5, 3.3, 4, 1.2, "RESULTS & REPORTING\n\nOutput files:\n• TP_Reduction_by_Reach.csv\n• Scenario_Comparison.xlsx\n• Maps & visualizations",
         colors['output'], 9)

draw_arrow(ax5, 5, 4.8, 5, 3.9)

# Key metrics box
draw_box(ax5, 5, 1.5, 4.5, 1.5, "KEY PERFORMANCE INDICATORS\n\n• Total TP load reduction (tonnes/year)\n• % reduction by subcatchment\n• Reaches with >50% reduction\n• Cost-effectiveness analysis",
         colors['scenario'], 9)

plt.tight_layout()

# ============================================================================
# PAGE 6: Output Structure & File Organization
# ============================================================================
fig6 = plt.figure(figsize=(11, 14))
ax6 = fig6.add_subplot(111)
ax6.set_xlim(0, 10)
ax6.set_ylim(0, 14)
ax6.axis('off')

create_page_title(fig6, "Project Directory Structure & Output Files",
                  "Complete File Organization")

# Root Directory
ax6.text(5, 13.2, "PROJECT ROOT: C:/Users/moghaddamr/Reza_CW_Analysis/",
         fontsize=10, ha='center', family='monospace',
         bbox=dict(boxstyle='round', facecolor='#E0E0E0', edgecolor='black', linewidth=1.5))

# Main directories
draw_box(ax6, 1.8, 11.8, 1.5, 0.7, "[DIR] Model/", colors['process'], 8)
draw_box(ax6, 3.8, 11.8, 1.5, 0.7, "[DIR] CLUES_Data/", colors['input'], 8)
draw_box(ax6, 5.8, 11.8, 1.5, 0.7, "[DIR] Analysis_Scripts/", colors['data'], 8)
draw_box(ax6, 7.8, 11.8, 1.5, 0.7, "[DIR] Documentation/", colors['data'], 8)

# Model subdirectories
ax6.text(1.8, 10.8, "Model/", fontsize=9, ha='center', weight='bold')
model_subs = [
    ("InputData/", "CLUESloads, AttenCarry", 10.1),
    ("SelectionFiles/", "Reach selection CSVs", 9.4),
    ("Lookups/", "Scenarios, LRFs", 8.7),
    ("Outputs/", "Model results", 8.0),
]
for folder, desc, y in model_subs:
    draw_box(ax6, 1.8, y, 1.4, 0.6, f"{folder}\n{desc}", colors['output'], 7)

# Scripts
ax6.text(3.8, 10.8, "Scripts/", fontsize=9, ha='center', weight='bold')
script_items = [
    ("StandAloneDNZ2.py", "Baseline model", 10.1),
    ("StandAloneDNZ2_\nWetland066m.py", "Wetland scenario", 9.3),
    ("LakeOmapere_\nRouting_Template.py", "Routing analysis", 8.5),
    ("PlacementRules.py", "CW placement", 7.7),
]
for script, desc, y in script_items:
    draw_box(ax6, 3.8, y, 1.4, 0.6, f"{script}\n{desc}", colors['process'], 7)

# Input Data
ax6.text(5.8, 10.8, "Input Data/", fontsize=9, ha='center', weight='bold')
data_items = [
    ("CLUES spreadsheets\nbaseline & wetland", 10.1),
    ("GIS shapefiles\nCW sites, lake", 9.4),
    ("Coverage analysis\nCSVs", 8.7),
]
for i, item in enumerate(data_items):
    y = 10.1 - i * 0.7
    draw_box(ax6, 5.8, y, 1.4, 0.6, item, colors['input'], 7)

# Documentation
ax6.text(7.8, 10.8, "Documentation/", fontsize=9, ha='center', weight='bold')
doc_items = [
    ("annette.txt", "Original instructions", 10.1),
    ("PROJECT_STATUS.md", "Status summary", 9.4),
    ("LAKE_OMAPERE_\nMODEL_READY.md", "Complete guide", 8.6),
    ("FILE_MANIFEST.txt", "File inventory", 7.9),
]
for doc, desc, y in doc_items:
    draw_box(ax6, 7.8, y, 1.4, 0.55, f"{doc}\n{desc}", colors['data'], 7)

# Key output files
ax6.text(5, 6.8, "KEY OUTPUT FILES GENERATED BY MODELS", fontsize=10, ha='center', weight='bold',
         bbox=dict(boxstyle='round', facecolor='#FFEB99', edgecolor='black', linewidth=2))

outputs = [
    ("GenSS_Baseline.csv", "Baseline TP loads"),
    ("GenSS_Wetland.csv", "Wetland scenario TP"),
    ("TP_Reduction.csv", "Load reduction values"),
    ("Comparison.xlsx", "Scenario comparison"),
]

for i, (fname, desc) in enumerate(outputs):
    row = i // 2
    col = i % 2
    x = 2.5 + col * 4.5
    y = 5.8 - row * 0.8
    draw_box(ax6, x, y, 2, 0.6, f"{fname}\n{desc}", colors['output'], 8)

# Archive section
ax6.text(5, 3.3, "ARCHIVE/", fontsize=10, ha='center', weight='bold',
         bbox=dict(boxstyle='round', facecolor='#D3D3D3', edgecolor='black', linewidth=2))

draw_box(ax6, 5, 2.3, 4, 0.8, "Model_DNZ_OriginalTemplate/\n(Old DNZ scripts, not used in Lake Ōmāpere)",
         colors['data'], 8)

# File Statistics
stats_text = """PROJECT STATISTICS:
• Total Python scripts: 7 (active)
• Data files: 20+ CSVs & Excel files
• Shapefiles: 15+ (GIS data)
• Documentation: 10+ files
• Total project size: ~500 MB"""

ax6.text(5, 0.8, stats_text, fontsize=8, ha='center', family='monospace',
         bbox=dict(boxstyle='round', facecolor='#F0F0F0', edgecolor='black', linewidth=1))

plt.tight_layout()

# ============================================================================
# Create PDF
# ============================================================================

# Save to PDF
pdf_path = "Lake_Omapere_Project_Schematics.pdf"
print(f"Creating PDF: {pdf_path}")

with PdfPages(pdf_path) as pdf:
    pdf.savefig(fig1, bbox_inches='tight')
    pdf.savefig(fig2, bbox_inches='tight')
    pdf.savefig(fig3, bbox_inches='tight')
    pdf.savefig(fig4, bbox_inches='tight')
    pdf.savefig(fig5, bbox_inches='tight')
    pdf.savefig(fig6, bbox_inches='tight')

    # Add metadata
    d = pdf.infodict()
    d['Title'] = 'Lake Ōmāpere CW Mitigation Project - Architecture & Data Flow Schematics'
    d['Author'] = 'Reza Moghaddam'
    d['Subject'] = 'Project schematics, model architecture, and data flow diagrams'
    d['Keywords'] = 'Lake Ōmāpere, CW, DNZ, CLUES, Model, Phosphorus'
    d['CreationDate'] = datetime.now()

print("[SUCCESS] PDF created successfully: " + pdf_path)
print("   Location: " + os.path.abspath(pdf_path))

# Close all figures
plt.close('all')

print("\nGeneration time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("Total pages: 6")
print("  - Page 1: Overall Architecture")
print("  - Page 2: Model Input Files")
print("  - Page 3: Model Configuration")
print("  - Page 4: Data Flow Diagram")
print("  - Page 5: Scenario Comparison")
print("  - Page 6: Directory Structure")
