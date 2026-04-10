def normalize_flowcell_id(fcid: str) -> str:
    """Canonical matching of SC... vs ASC..."""
    fcid = fcid or ""
    if fcid.startswith("ASC"):
        return fcid[1:]
    return fcid
