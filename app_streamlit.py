import streamlit as st
from molpic.resolve import resolve_name_to_smiles
from molpic.core import render_molecule
import tempfile
from pathlib import Path

st.title("MolPic — Molecule Image Generator")

query = st.text_input("Enter compound name or SMILES", "aspirin")
fmt = st.selectbox("Output format", ["svg", "png"])
w = st.slider("Width", 300, 1200, 800)
h = st.slider("Height", 300, 1200, 600)

if st.button("Generate"):
    q = query.strip()
    if not q:
        st.error("Please enter a name or SMILES.")
    else:
        # Simple heuristic: treat as name unless it contains typical SMILES chars
        is_smiles = any(c in q for c in "#=()[]@+\\/-0123456789")
        smiles = q if is_smiles else None

        if smiles is None:
            rr = resolve_name_to_smiles(q)
            if not rr.smiles:
                st.error(f"Could not resolve: {rr.message}")
                st.stop()
            smiles = rr.smiles
            st.caption(f"Resolved via PubChem (CID {rr.pubchem_cid})")

        with tempfile.TemporaryDirectory() as td:
            out = str(Path(td) / f"molecule.{fmt}")
            rr2 = render_molecule(smiles=smiles, out=out, size=(w, h), legend=q)
            if not rr2.ok:
                st.error(rr2.message)
            else:
                data = Path(out).read_bytes()
                mime = "image/svg+xml" if fmt == "svg" else "image/png"
                st.download_button("Download", data=data, file_name=f"{q.replace(' ','_')}.{fmt}", mime=mime)
                if fmt == "png":
                    st.image(data)
                else:
                    st.markdown(data.decode("utf-8"), unsafe_allow_html=True)
