from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
import typer
from rich.console import Console

from .core import render_grid, render_molecule
from .resolve import resolve_name_to_smiles

app = typer.Typer(add_completion=False)
console = Console()


def _parse_grid(g: str) -> Tuple[int, int]:
    s = g.lower().replace(" ", "")
    if "x" not in s:
        raise typer.BadParameter("Grid must be like 2x3")
    a, b = s.split("x", 1)
    r, c = int(a), int(b)
    if r <= 0 or c <= 0:
        raise typer.BadParameter("Grid rows/cols must be positive.")
    return r, c


def _is_probably_smiles(text: str) -> bool:
    smiles_chars = set("#=()[]@+\\/-0123456789")
    return any(c in smiles_chars for c in text)


def _to_smiles(query: str) -> tuple[str, str, Optional[int]]:
    q = query.strip()
    if _is_probably_smiles(q):
        return q, "input", None
    rr = resolve_name_to_smiles(q)
    if not rr.smiles:
        raise ValueError(rr.message)
    return rr.smiles, rr.source, rr.pubchem_cid


def _write_caption(path: str, title: str, legends: List[str]):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    items = "; ".join([f"{i+1}) {name}" for i, name in enumerate(legends)])
    caption = f"{title.strip()}\nCompounds: {items}\n" if title.strip() else f"Compounds: {items}\n"
    p.write_text(caption, encoding="utf-8")


@app.command()
def generate(
    query: str = typer.Argument(..., help="Compound name or SMILES."),
    out: str = typer.Option("molecule.svg", "-o", "--out", help="Output (.png or .svg)."),
    width: int = typer.Option(900, "--width"),
    height: int = typer.Option(700, "--height"),
    name: str = typer.Option("", "--name", help="Legend label under structure."),
    no_h: bool = typer.Option(False, "--no-h", help="Remove explicit hydrogens."),
    transparent: bool = typer.Option(True, "--transparent/--no-transparent"),
    png_dpi: int = typer.Option(300, "--png-dpi"),
):
    q = query.strip()
    try:
        smiles, source, cid = _to_smiles(q)
    except ValueError as e:
        console.print(f"[red]Could not resolve:[/red] {e}")
        raise typer.Exit(code=1)

    legend = name.strip() or q
    rr2 = render_molecule(
        smiles=smiles,
        out=out,
        size=(width, height),
        legend=legend,
        transparent=transparent,
        no_h=no_h,
        png_dpi=png_dpi,
    )
    if not rr2.ok:
        console.print(f"[red]Failed:[/red] {rr2.message}")
        raise typer.Exit(code=1)

    console.print(f"[green]Saved:[/green] {rr2.out_path}")
    console.print(f"[cyan]Label:[/cyan] {legend}")
    console.print(f"[cyan]SMILES:[/cyan] {smiles}")
    console.print(f"[cyan]Source:[/cyan] {source}" + (f" (CID {cid})" if cid else ""))


@app.command()
def grid(
    queries: List[str] = typer.Argument(..., help="Multiple names/SMILES."),
    out: str = typer.Option("panel.svg", "-o", "--out"),
    grid: str = typer.Option("2x3", "--grid"),
    sub_w: int = typer.Option(550, "--sub-width"),
    sub_h: int = typer.Option(450, "--sub-height"),
    names: Optional[List[str]] = typer.Option(None, "--name", help="Optional labels; repeatable."),
    no_h: bool = typer.Option(False, "--no-h"),
    png_dpi: int = typer.Option(300, "--png-dpi"),
    title: str = typer.Option("", "--title", help="Figure title (SVG panels)."),
    caption_file: str = typer.Option("", "--caption-file", help="Write a caption text file."),
    order_by: str = typer.Option("input", "--order-by", help="input or name"),
):
    rows, cols = _parse_grid(grid)

    items = []
    for i, q in enumerate(queries):
        q = q.strip()
        try:
            smiles, _, _ = _to_smiles(q)
        except ValueError as e:
            console.print(f"[yellow]Skip:[/yellow] {q} ({e})")
            continue

        label = q
        if names and i < len(names) and names[i].strip():
            label = names[i].strip()

        items.append((label, smiles))

    if not items:
        console.print("[red]No valid molecules to render.[/red]")
        raise typer.Exit(code=2)

    if order_by.lower() == "name":
        items.sort(key=lambda x: x[0].lower())

    legends = [x[0] for x in items]
    smiles_list = [x[1] for x in items]

    rr = render_grid(
        smiles_list=smiles_list,
        out=out,
        legends=legends,
        grid=(rows, cols),
        sub_img_size=(sub_w, sub_h),
        no_h=no_h,
        png_dpi=png_dpi,
        title=title,
    )
    if not rr.ok:
        console.print(f"[red]Failed:[/red] {rr.message}")
        raise typer.Exit(code=1)

    if caption_file.strip():
        _write_caption(caption_file, title=title, legends=legends)

    console.print(f"[green]Saved panel:[/green] {rr.out_path}")
    console.print(f"[cyan]Grid:[/cyan] {rows}x{cols}")
    console.print(f"[cyan]Count:[/cyan] {len(smiles_list)}")


@app.command()
def batch(
    input_file: str = typer.Argument(..., help="CSV with columns for name and/or smiles."),
    smiles_col: str = typer.Option("smiles", "--smiles-col"),
    name_col: str = typer.Option("name", "--name-col"),
    out_dir: str = typer.Option("molpic_out", "--out-dir"),
    fmt: str = typer.Option("svg", "--fmt"),
    no_h: bool = typer.Option(False, "--no-h"),
    make_panels: bool = typer.Option(False, "--make-panels"),
    panel_grid: str = typer.Option("2x3", "--panel-grid"),
    panel_title_prefix: str = typer.Option("Panel", "--panel-title-prefix"),
    captions: bool = typer.Option(False, "--captions", help="Write caption per panel."),
    order_by: str = typer.Option("input", "--order-by", help="input or name"),
):
    df = pd.read_csv(input_file)
    outp = Path(out_dir)
    outp.mkdir(parents=True, exist_ok=True)

    has_smiles = smiles_col in df.columns
    has_name = name_col in df.columns
    if not has_smiles and not has_name:
        console.print(f"[red]Need '{smiles_col}' or '{name_col}' column.[/red]")
        console.print(f"Columns: {list(df.columns)}")
        raise typer.Exit(code=2)

    rows, cols = _parse_grid(panel_grid)
    capacity = rows * cols

    rendered_items = []  # (legend, smiles, out_file)

    report_rows = []
    for i, row in df.iterrows():
        raw_smiles = str(row.get(smiles_col, "")).strip() if has_smiles else ""
        raw_name = str(row.get(name_col, "")).strip() if has_name else ""

        query = raw_smiles if raw_smiles else raw_name
        if not query:
            report_rows.append({"row": i, "ok": False, "message": "empty"})
            continue

        if raw_smiles:
            smiles = raw_smiles
            source = "input_smiles"
            cid = None
        else:
            rr = resolve_name_to_smiles(raw_name)
            if not rr.smiles:
                report_rows.append({"row": i, "ok": False, "message": rr.message})
                continue
            smiles = rr.smiles
            source = rr.source
            cid = rr.pubchem_cid

        legend = raw_name if raw_name else query
        safe_label = (legend.replace(" ", "_").replace("/", "_"))[:80]
        out_file = outp / f"{i:04d}_{safe_label}.{fmt}"

        rr2 = render_molecule(smiles=smiles, out=str(out_file), legend=legend, no_h=no_h)
        report_rows.append({
            "row": i, "query": query, "legend": legend, "ok": rr2.ok,
            "out": rr2.out_path, "source": source, "cid": cid, "message": rr2.message
        })

        if rr2.ok:
            rendered_items.append((legend, smiles, str(out_file)))

    # Save report
    pd.DataFrame(report_rows).to_csv(outp / "molpic_report.csv", index=False)

    # Panels
    if make_panels and rendered_items:
        items = rendered_items[:]
        if order_by.lower() == "name":
            items.sort(key=lambda x: x[0].lower())

        panel_index = 1
        for start in range(0, len(items), capacity):
            chunk = items[start:start + capacity]
            legends = [x[0] for x in chunk]
            smiles_list = [x[1] for x in chunk]

            panel_out = outp / f"panel_{panel_index:03d}.{fmt}"
            title = f"{panel_title_prefix} {panel_index:03d}"
            render_grid(
                smiles_list=smiles_list,
                legends=legends,
                out=str(panel_out),
                grid=(rows, cols),
                sub_img_size=(550, 450),
                no_h=no_h,
                title=title,
            )
            if captions:
                _write_caption(str(outp / f"panel_{panel_index:03d}_caption.txt"), title=title, legends=legends)

            panel_index += 1

    console.print(f"[green]Done.[/green] Output dir: {out_dir}")
    console.print(f"[cyan]Report:[/cyan] {outp / 'molpic_report.csv'}")


def main():
    app()
