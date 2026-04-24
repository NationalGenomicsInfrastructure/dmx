import io

# Required fields on every BCLConvert_Data row.
_BCL_DATA_REQUIRED_ROW_FIELDS: tuple[str, ...] = (
    "Lane",
    "Sample_ID",
    "Sample_Name",
    "index",
    "Sample_Project",
)

# Optional fields whose presence is checked for consistency across rows.
_BCL_DATA_CONSISTENCY_CHECKED_FIELDS: tuple[str, ...] = ("index2", "OverrideCycles")


def normalize_flowcell_id(fcid: str) -> str:
    """Canonical matching of SC... vs ASC..."""
    fcid = fcid or ""
    if fcid.startswith("ASC"):
        return fcid[1:]
    return fcid


def validate_lane_payload(lane_payload: dict) -> None:
    """Validate a single lane samplesheet payload before rendering.

    Checks:
    - Top-level required keys are present.
    - BCLConvert_Data is a non-empty list of dicts.
    - Every row contains the required row fields.
    - Optional fields (index2, OverrideCycles) are consistent: present in all
      rows or absent from all rows.

    Raises:
        ValueError: on any structural or content problem.
    """
    for key in ("Header", "raw_samplesheet_settings", "BCLConvert_Data"):
        if key not in lane_payload:
            raise ValueError(f"Lane payload missing required key '{key}'.")

    data = lane_payload["BCLConvert_Data"]
    if not isinstance(data, list):
        raise ValueError(
            f"BCLConvert_Data must be a list, got {type(data).__name__}."
        )
    if not data:
        raise ValueError("BCLConvert_Data is empty.")

    for i, row in enumerate(data):
        if not isinstance(row, dict):
            raise ValueError(f"BCLConvert_Data row {i} is not a dict.")
        missing = [f for f in _BCL_DATA_REQUIRED_ROW_FIELDS if f not in row]
        if missing:
            raise ValueError(
                f"BCLConvert_Data row {i} missing required field(s): {missing}."
            )

    # Consistency check: optional fields must be uniformly present or absent.
    for field in _BCL_DATA_CONSISTENCY_CHECKED_FIELDS:
        presence = [field in row for row in data]
        if any(presence) and not all(presence):
            raise ValueError(
                f"BCLConvert_Data rows are inconsistent: '{field}' is present "
                f"in some rows but not all."
            )


def render_bcl_convert_samplesheet(lane_payload: dict) -> str:
    """Render a bcl-convert SampleSheet.csv text from a lane payload dict.

    Sections emitted (in order):
      [Header]          — key/value pairs
      [BCLConvert_Settings] — key/value pairs (source field: raw_samplesheet_settings)
      [BCLConvert_Data] — CSV table

    Column order in [BCLConvert_Data]: required fields first (in canonical
    order), then any extra fields found in the rows, in their natural dict
    iteration order from the first row.

    Args:
        lane_payload: A validated lane payload dict.  Call validate_lane_payload
            first to get a clear error on bad input.

    Returns:
        The full samplesheet text, ready to be written to SampleSheet.csv.
    """
    buf = io.StringIO()

    def _write_kv_section(section_name: str, mapping: dict) -> None:
        buf.write(f"[{section_name}]\n")
        for k, v in mapping.items():
            buf.write(f"{k},{v}\n")

    _write_kv_section("Header", lane_payload["Header"])
    buf.write("\n")

    # The field is currently named raw_samplesheet_settings; it will likely
    # be renamed to BCLConvert_Settings upstream.
    _write_kv_section("BCLConvert_Settings", lane_payload["raw_samplesheet_settings"])
    buf.write("\n")

    data_rows = lane_payload["BCLConvert_Data"]
    # Build column order: required columns first, then extra columns in
    # first-row dict order (stable across Python 3.7+).
    extra_cols = [
        k for k in data_rows[0] if k not in _BCL_DATA_REQUIRED_ROW_FIELDS
    ]
    columns = list(_BCL_DATA_REQUIRED_ROW_FIELDS) + extra_cols

    buf.write("[BCLConvert_Data]\n")
    buf.write(",".join(columns) + "\n")
    for row in data_rows:
        buf.write(",".join(str(row.get(col, "")) for col in columns) + "\n")

    return buf.getvalue()
