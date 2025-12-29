from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from rdkit import Chem
from rdkit.Chem import AllChem, Draw


@dataclass
class RenderResult:
    smiles: Optional[str]
    out_path: Optional[str]
    ok: bool
    message: str


def _mol_from_smiles(smiles: str, no_h: bool = False):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    AllChem.Compute2DCoords(mol)
    if no_h:
        try:
            mol = Chem.RemoveHs(mol, sanitize=True)
        except Exception:
            pass
    return mol


def render_molecule(
    smiles: str,
    out: str,
    size: Tuple[int, int] = (900, 700),
    legend: str = "",
    transparent: bool = True,
    no_h: bool = False,
    png_dpi: int = 300,
) -> RenderResult:
    s = (smiles or "").strip()
    if not s:
        return RenderResult(None, None, False, "Empty SMILES provided.")

    mol = _mol_from_smiles(s, no_h=no_h)
    if mol is None:
        return RenderResult(s, None, False, "RDKit could not parse the SMILES.")

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = out_path.suffix.lower()
    if suffix not in [".png", ".svg"]:
        return RenderResult(s, None, False, "Output must end with .png or .svg")

    try:
        if suffix == ".png":
            img = Draw.MolToImage(mol, size=size, legend=legend)
            try:
                img.save(str(out_path), dpi=(png_dpi, png_dpi))
            except Exception:
                img.save(str(out_path))
        else:
            drawer = Draw.MolDraw2DSVG(size[0], size[1])
            opts = drawer.drawOptions()
            opts.clearBackground = transparent
            opts.baseFontSize = 18
            opts.bondLineWidth = 2
            opts.addStereoAnnotation = True
            opts.padding = 0.05

            drawer.DrawMolecule(mol, legend=legend)
            drawer.FinishDrawing()
            svg = drawer.GetDrawingText()
            out_path.write_text(svg, encoding="utf-8")

        return RenderResult(s, str(out_path), True, "OK")
    except Exception as e:
        return RenderResult(s, None, False, f"Render error: {e}")


def _inject_svg_title(svg: str, title: str, extra_top_px: int = 70) -> str:
    """
    Wrap the RDKit SVG in a new SVG with extra top margin and a title text.
    Keeps it simple and robust.
    """
    if not title.strip():
        return svg

    # Ensure RDKit SVG starts with <svg ...>
    start = svg.find("<svg")
    if start == -1:
        return svg

    # Extract width/height if present (common in RDKit SVG)
    # We'll default to 1500x1000 if not found.
    import re
    w = 1500
    h = 1000
    m_w = re.search(r'width="(\d+)(px)?"', svg)
    m_h = re.search(r'height="(\d+)(px)?"', svg)
    if m_w:
        w = int(m_w.group(1))
    if m_h:
        h = int(m_h.group(1))

    new_h = h + extra_top_px

    # Remove outer XML headers if present, keep inner SVG content
    inner = svg
    # strip optional xml declaration
    inner = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", inner)
    # strip optional doctype
    inner = re.sub(r"^\s*<!DOCTYPE[^>]*>\s*", "", inner)

    # Move original content down by extra_top_px via a group transform
    wrapped = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{new_h}" viewBox="0 0 {w} {new_h}">
  <text x="{w/2}" y="{extra_top_px*0.65}" text-anchor="middle" font-size="28" font-family="Arial">{title}</text>
  <g transform="translate(0,{extra_top_px})">
    {inner}
  </g>
</svg>
"""
    return wrapped


def render_grid(
    smiles_list: List[str],
    out: str,
    legends: Optional[List[str]] = None,
    grid: Tuple[int, int] = (2, 3),
    sub_img_size: Tuple[int, int] = (550, 450),
    transparent: bool = True,
    no_h: bool = False,
    png_dpi: int = 300,
    title: str = "",
) -> RenderResult:
    if not smiles_list:
        return RenderResult(None, None, False, "No molecules provided for grid rendering.")

    mols = []
    used_legends = legends or [""] * len(smiles_list)

    for s in smiles_list:
        ss = (s or "").strip()
        if not ss:
            mols.append(None)
            continue
        mols.append(_mol_from_smiles(ss, no_h=no_h))

    rows, cols = grid
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = out_path.suffix.lower()
    if suffix not in [".png", ".svg"]:
        return RenderResult(None, None, False, "Grid output must end with .png or .svg")

    try:
        if suffix == ".png":
            # RDKit produces PIL image for grids
            img = Draw.MolsToGridImage(
                mols,
                molsPerRow=cols,
                subImgSize=sub_img_size,
                legends=used_legends,
                useSVG=False,
            )
            try:
                img.save(str(out_path), dpi=(png_dpi, png_dpi))
            except Exception:
                img.save(str(out_path))
            return RenderResult("GRID", str(out_path), True, "OK")

        # SVG grid (best for papers)
        svg = Draw.MolsToGridImage(
            mols,
            molsPerRow=cols,
            subImgSize=sub_img_size,
            legends=used_legends,
            useSVG=True,
        )
        if not transparent:
            # RDKit SVG usually transparent; you can postprocess if needed later.
            pass

        svg = _inject_svg_title(svg, title=title.strip())
        out_path.write_text(svg, encoding="utf-8")
        return RenderResult("GRID", str(out_path), True, "OK")

    except Exception as e:
        return RenderResult("GRID", None, False, f"Grid render error: {e}")
