# MolPic
# Name/SMILES → Publication-Ready Molecular Figures

MolPic is an open-source cheminformatics tool that generates high-quality 2D molecular figures directly from compound names or SMILES, with support for multi-panel (grid) figures, batch processing, and automatic figure captions.
It is designed for computational drug discovery, chemoinformatics, and scientific publishing, where fast and reproducible generation of clean molecular figures is essential.

## Key Features
-Generate SVG or PNG molecule images from:
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
!pip -q install git+https://github.com/akinwumiishola5000/MolPic.git
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
!molpic grid Aspirin Caffeine Ibuprofen Warfarin Naproxen Acetaminophen \
  --grid 2x3 \
  -o panel.svg \
  --no-h \
  --title "Figure 1. Example panel of drug molecules" \
  --caption-file figure1_caption.txt \
  --order-by name
 ```

**Display**
```bash
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
**Teaching cheminformatics and drug design**
**Standardizing molecule depiction across projects**
**Generating consistent graphics for presentations**



