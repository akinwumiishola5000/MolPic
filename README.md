# MolPic
# Name/SMILES → Publication-Ready Molecular Figures

MolPic is an open-source cheminformatics tool that generates high-quality 2D molecular figures directly from compound names or SMILES, with support for multi-panel (grid) figures, batch processing, and automatic figure captions.
It is designed for computational drug discovery, chemoinformatics, and scientific publishing, where fast and reproducible generation of clean molecular figures is essential.

## Key Features
-Generate SVG molecule images from:
-**SMILES strings**

-**Compound names** (resolved automatically via PubChem)

-Multi-panel figures for papers and slides (--grid 2x3)

-Batch processing from CSV files

-Automatic compound labels under each structure

-Optional figure titles and caption text files

-Remove explicit hydrogens for clean publication figures (--no-h)

-Designed for Google Colab, Linux, and macOS

-Fully open-source and citable

## Quick Start (Google Colab – Recommended)
**MolPic is Colab-first. No local setup is required.**

---
## Installation

**Step 1: Install MolPic directly from GitHub**
```bash
!pip -q install rdkit pubchempy typer rich pandas
!pip -q install --upgrade git+https://github.com/akinwumiishola5000/MolPic.git
 ```

**Step 2: Generate a single molecule figure**
```bash
!molpic generate "aspirin" -o aspirin.svg --no-h --name "Aspirin"
 ```

**Display inside Colab:**
```bash
from IPython.display import SVG, display
display(SVG("aspirin.svg"))
 ```

**Step 3: Create a publication-ready multi-panel figure**
```bash
!molpic grid acetaminophen aspirin caffeine ibuprofen warfarin naproxen \
  --grid 2x3 -o panel.svg --no-h
 ```

**Display**
```bash
from IPython.display import SVG, display
display(SVG("panel.svg"))
 ```

## Create a publication-ready multi-panel figure for 20 compounds**
```bash
!molpic grid Aspirin Caffeine Ibuprofen Acetaminophen Warfarin Naproxen Diclofenac\
 Ketoprofen Celecoxib Indomethacin Lidocaine Procaine Metformin Atorvastatin Simvastatin\
 Rosuvastatin Amoxicillin Ciprofloxacin Fluoxetine Diazepam  \
  --grid 2x3 -o panel.svg --no-h
 ```

**Display**
```bash
from IPython.display import SVG, display
display(SVG("panel.svg"))
 ```
## Create a publication-ready multi-panel SMILES with compound names

**Step 1: Define your compounds (Name + SMILES)**
```bash
pairs_text = """
Aspirin|CC(=O)OC1=CC=CC=C1C(=O)O
Caffeine|CN1C=NC2=C1C(=O)N(C(=O)N2C)C
Ibuprofen|CC(C)CC1=CC=C(C=C1)C(C)C(=O)O
Acetaminophen|CC(=O)NC1=CC=C(O)C=C1
Warfarin|CC(=O)CC(C1=CC=CC=C1)C(O)C2=CC=CC=C2
Naproxen|COC1=CC=CC2=C1C(C)C(C(=O)O)=CC2
Nicotinamide|C1=CC(=CN=C1)C(=O)N
Pyridoxine|CC1=NC=C(C(=C1O)CO)CO
Luteolin|C1=CC(=C(C=C1C2=CC(=O)C3=C(C=C(C=C3O2)O)O)O)O
Vernomygdin|CC(C)C(=O)OC1CC23C(O2)CCC(=CC4C1C(=C)C(=O)O4)COC3O
Vernomenin|C=CC12CC3C(C(C1C(=C)C(=O)OC2)O)C(=C)C(=O)O3
"""
 ```
**Step 2: Generate the compounds**
```bash
import shlex, subprocess

names = []
smiles = []

for line in pairs_text.strip().splitlines():
    line = line.strip()
    if not line:
        continue
    name, smi = line.split("|", 1)
    names.append(name.strip())
    smiles.append(smi.strip())

# Build molpic CLI call using SMILES (works reliably; no PubChem needed)
cmd = ["molpic", "grid"] + smiles + [
    "--grid", "2x3",
    "-o", "panel.svg",
    "--no-h",
]

# If your MolPic grid supports repeated --name labels (it does in our CLI design)
for n in names:
    cmd += ["--name", n]

print("Running:\n", " ".join(shlex.quote(x) for x in cmd))
subprocess.run(cmd, check=True)
 ```
**Step 3: Display the compounds panel**
```bash
from IPython.display import SVG, display
display(SVG("panel.svg"))
 ```

## Local Installation (Linux / macOS)
**Recommended (conda)**
```bash
conda create -n molpic python=3.10 -y
conda activate molpic
conda install -c conda-forge rdkit -y
pip install git+https://github.com/akinwumiishola5000/MolPic.git
 ```

**Test**
```bash
molpic generate "ibuprofen" -o ibuprofen.svg --no-h
 ```

## Typical Use Cases
**Preparing figure panels for manuscripts and theses**

**Rapid visualization during virtual screening**

**Teaching chemoinformatics and drug design**

**Standardizing molecule depiction across projects**

**Generating consistent graphics for presentations**



