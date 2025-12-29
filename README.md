# MolPic — Molecule Image Generator (Name/SMILES → PNG/SVG)

MolPic generates publication-ready 2D molecule images from:
- **SMILES** (direct)
- **Compound names** (resolved via PubChem → canonical SMILES)

## Why this exists
Making clean molecule figures for slides/papers is annoyingly repetitive. MolPic makes it one command.

---

## Installation

### Option A: Install with conda (recommended for RDKit)
```bash
conda create -n molpic python=3.10 -y
conda activate molpic
conda install -c conda-forge rdkit -y
pip install -e .
