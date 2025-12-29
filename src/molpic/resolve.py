from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import pubchempy as pcp


@dataclass
class ResolveResult:
    query: str
    smiles: Optional[str]
    source: str
    pubchem_cid: Optional[int]
    message: str


def resolve_name_to_smiles(name: str, timeout_s: int = 20) -> ResolveResult:
    """
    Resolve a compound name to canonical SMILES using PubChem.
    Returns a structured result so callers can log provenance.
    """
    q = name.strip()
    if not q:
        return ResolveResult(name, None, "none", None, "Empty name provided.")

    try:
        # PubChem: try by name
        compounds = pcp.get_compounds(q, namespace="name", as_dataframe=False)
        if not compounds:
            # Try as "query" (sometimes helps for synonyms)
            compounds = pcp.get_compounds(q, namespace="query", as_dataframe=False)

        if not compounds:
            return ResolveResult(q, None, "pubchem", None, "No PubChem match found.")

        c = compounds[0]
        smiles = getattr(c, "canonical_smiles", None) or getattr(c, "isomeric_smiles", None)
        cid = getattr(c, "cid", None)
        if not smiles:
            return ResolveResult(q, None, "pubchem", cid, "Matched PubChem entry but no SMILES returned.")
        return ResolveResult(q, smiles, "pubchem", cid, "OK")
    except Exception as e:
        return ResolveResult(q, None, "pubchem", None, f"PubChem resolution error: {e}")
