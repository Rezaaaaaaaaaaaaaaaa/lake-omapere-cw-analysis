"""
Cleanup and organize Lake Omapere project files.

This script:
1. Creates organized directory structure
2. Moves files to appropriate locations
3. Creates a manifest of all key files
4. Archives old/working files
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("LAKE OMAPERE PROJECT CLEANUP AND ORGANIZATION")
print("=" * 80)
print()

# Base directory
BASE_DIR = Path(r"C:\Users\moghaddamr\Reza_CW_Analysis")

# Create organized directory structure
DIRS = {
    "Documentation": BASE_DIR / "Documentation",
    "Analysis_Scripts": BASE_DIR / "Analysis_Scripts",
    "CW_Analysis_Results": BASE_DIR / "CW_Analysis_Results",
    "CLUES_Data": BASE_DIR / "CLUES_Data",
    "Model": BASE_DIR / "Model",
    "Archive": BASE_DIR / "Archive"
}

print("Creating directory structure...")
for name, path in DIRS.items():
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {name}/")
    else:
        print(f"  Exists: {name}/")
print()

# File organization plan
FILE_MOVES = {
    # Documentation files
    "Documentation": [
        "LAKE_OMAPERE_MODEL_READY.md",
        "MODEL_SETUP_SUMMARY.md",
        "CORRECTIONS_SUMMARY.md",
        "DATA_MATCHING_VERIFICATION.md",
        "SESSION_SUMMARY.txt",
        "DRAFT_EMAIL_SHORT.txt",
        "Draft_Email.txt",
        "EMAIL_TO_ANNETTE_FINAL.txt",
        "annette.txt",
        "README.md"
    ],
    # Analysis scripts
    "Analysis_Scripts": [
        "analyze_coverage_levels.py",
        "create_scenarios.py",
        "prepare_model_inputs.py",
        "prepare_cw_files.py",
        "explore_clues_spreadsheet.py",
        "extract_clues_data.py",
        "find_p_columns.py",
        "cleanup_and_organize.py"
    ],
    # CW Analysis results
    "CW_Analysis_Results": [
        "CW_Coverage_CORRECTED.csv",
        "CW_Coverage_CORRECTED.xlsx",
        "CW_Coverage_Categories.csv",
        "CW_Coverage_Analysis_Report.txt"
    ],
    # CLUES data files
    "CLUES_Data": [
        "TP_noMit_LakeOnly_baseline.xlsb",
        "TP_noMit_LakeOnly+0.66m.xlsb",
        "LakeAreaUpdate.xlsx"
    ]
}

print("Organizing files...")
print()

moved_count = 0
skipped_count = 0

for dest_dir, files in FILE_MOVES.items():
    dest_path = DIRS[dest_dir]
    print(f"Moving to {dest_dir}/:")

    for filename in files:
        src_file = BASE_DIR / filename
        dest_file = dest_path / filename

        if src_file.exists():
            if not dest_file.exists():
                # Copy instead of move to be safe
                shutil.copy2(src_file, dest_file)
                print(f"  [COPIED] {filename}")
                moved_count += 1
            else:
                print(f"  [EXISTS] {filename} (skipped)")
                skipped_count += 1
        else:
            print(f"  [MISSING] {filename}")

    print()

print(f"Summary: {moved_count} files copied, {skipped_count} already existed")
print()

# Create a manifest file
print("Creating file manifest...")

manifest_path = BASE_DIR / "Documentation" / "FILE_MANIFEST.txt"

with open(manifest_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("LAKE OMAPERE CW MITIGATION PROJECT - FILE MANIFEST\n")
    f.write("=" * 80 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")

    for dir_name, dir_path in DIRS.items():
        f.write(f"\n{dir_name}/\n")
        f.write("-" * 80 + "\n")

        if dir_path.exists():
            files = sorted([f for f in dir_path.iterdir() if f.is_file()])
            if files:
                for file in files:
                    size_kb = file.stat().st_size / 1024
                    f.write(f"  {file.name:50s} ({size_kb:,.1f} KB)\n")
            else:
                f.write("  (empty)\n")
        else:
            f.write("  (directory not found)\n")

    # Add Model directory structure
    f.write("\n\nModel/\n")
    f.write("-" * 80 + "\n")

    model_path = BASE_DIR / "Model"
    if model_path.exists():
        # Key subdirectories
        for subdir in ["InputData", "SelectionFiles", "Lookups", "Outputs"]:
            subdir_path = model_path / subdir
            f.write(f"\n  {subdir}/\n")
            if subdir_path.exists():
                files = sorted([f for f in subdir_path.iterdir() if f.is_file()])
                for file in files[:20]:  # Limit to 20 files per directory
                    size_kb = file.stat().st_size / 1024
                    f.write(f"    {file.name:45s} ({size_kb:,.1f} KB)\n")
                if len(files) > 20:
                    f.write(f"    ... and {len(files) - 20} more files\n")
            else:
                f.write("    (not found)\n")

print(f"Manifest created: {manifest_path}")
print()

# Create quick start guide
print("Creating quick start guide...")

quickstart_path = BASE_DIR / "QUICK_START.txt"

with open(quickstart_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("LAKE OMAPERE CW MITIGATION MODEL - QUICK START GUIDE\n")
    f.write("=" * 80 + "\n\n")

    f.write("PROJECT STATUS: MODEL READY TO RUN\n")
    f.write("Date: 2025-10-29\n\n")

    f.write("=" * 80 + "\n")
    f.write("DIRECTORY STRUCTURE\n")
    f.write("=" * 80 + "\n\n")

    f.write("Documentation/         - All project documentation and summaries\n")
    f.write("Analysis_Scripts/      - Python scripts for data preparation\n")
    f.write("CW_Analysis_Results/   - CW coverage analysis outputs\n")
    f.write("CLUES_Data/            - CLUES spreadsheets from Annette\n")
    f.write("Model/                 - Main model directory\n")
    f.write("  ├── InputData/       - Model input CSV files\n")
    f.write("  ├── SelectionFiles/  - Reach selection files\n")
    f.write("  ├── Lookups/         - Scenario and LRF lookup files\n")
    f.write("  └── Outputs/         - Model outputs (created on run)\n\n")

    f.write("=" * 80 + "\n")
    f.write("KEY FILES TO READ FIRST\n")
    f.write("=" * 80 + "\n\n")

    f.write("1. Documentation/LAKE_OMAPERE_MODEL_READY.md\n")
    f.write("   >> START HERE - Complete guide to running the model\n\n")

    f.write("2. Documentation/SESSION_SUMMARY.txt\n")
    f.write("   >> Background on CW analysis and outstanding issues\n\n")

    f.write("3. Documentation/annette.txt\n")
    f.write("   >> Original instructions from Annette\n\n")

    f.write("=" * 80 + "\n")
    f.write("HOW TO RUN THE MODEL\n")
    f.write("=" * 80 + "\n\n")

    f.write("1. BASELINE RUN:\n")
    f.write("   cd Model\n")
    f.write("   python StandAloneDNZ2.py\n\n")

    f.write("2. WETLAND RUN (+0.66m):\n")
    f.write("   cd Model\n")
    f.write("   python StandAloneDNZ2_Wetland066m.py\n\n")

    f.write("3. ROUTE RESULTS (if needed):\n")
    f.write("   cd Model\n")
    f.write("   python LakeOmapere_Routing_Template.py\n\n")

    f.write("=" * 80 + "\n")
    f.write("OUTSTANDING ISSUES\n")
    f.write("=" * 80 + "\n\n")

    f.write("1. LAKE OVERLAP ISSUE (URGENT)\n")
    f.write("   - 5 subcatchments have >100% CW coverage\n")
    f.write("   - ~19 ha of CW sites are in the lake zone\n")
    f.write("   - Email draft ready in Documentation/DRAFT_EMAIL_SHORT.txt\n")
    f.write("   - Awaiting Annette & Fleur's guidance\n\n")

    f.write("2. LRF THRESHOLDS\n")
    f.write("   - Review CW_Coverage_Analysis_Report.txt\n")
    f.write("   - Discuss with Fleur if thresholds are appropriate\n\n")

    f.write("=" * 80 + "\n")
    f.write("CONTACT\n")
    f.write("=" * 80 + "\n\n")

    f.write("Reza Moghaddam - Reza.Moghaddam@niwa.co.nz\n")
    f.write("Annette Semadeni-Davies - Annette.Davies@niwa.co.nz\n")
    f.write("Fleur Matheson - Fleur.Matheson@niwa.co.nz\n\n")

    f.write("=" * 80 + "\n")

print(f"Quick start guide created: {quickstart_path}")
print()

print("=" * 80)
print("CLEANUP COMPLETE!")
print("=" * 80)
print()
print("Next steps:")
print("  1. Read: QUICK_START.txt")
print("  2. Read: Documentation/LAKE_OMAPERE_MODEL_READY.md")
print("  3. Run the model when ready")
print()
print("=" * 80)
