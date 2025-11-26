"""
FOR DEMO PURPOSES ONLY
Undecided how to go with this, up to discussion.
"""

import io
import logging
import os

import pandas as pd  # type: ignore

try:
    from lib.couchdb.couchdb_connection import CouchDBHandler  # type: ignore
except ImportError:  # unit-test / demo env with no CouchDB lib
    CouchDBHandler = object  # type: ignore

_log = logging.getLogger("SampleSheetDBManager")


class SampleSheetDBManager(CouchDBHandler):  # type: ignore # inherits when lib exists
    """
    Retrieve a SampleSheet as a DataFrame.

    * demo / unit-test  --> returns a hard-coded 1-lane sheet
    * prod with CouchDB --> pulls the attachment
    """

    def __init__(self, use_mock: bool = False):
        # decide up-front whether we’re in mock mode
        self._mock = (
            use_mock or os.getenv("SAMPLESHEET_STORE", "couchdb").lower() == "mock"
        )

        if not self._mock:
            try:
                super().__init__("samplesheets")  # real DB
            except Exception as exc:
                _log.warning(
                    "CouchDB unreachable (%s) - switching to mock SampleSheet", exc
                )
                self._mock = True

        # one tiny DataFrame for the demo
        self._dummy_df = pd.DataFrame(
            {
                "Lane": ["1"],
                "Sample_ID": ["DEMO_SAMPLE"],
                "index": ["ACGTACGT"],
                "index2": [""],
            }
        )

    # ---- public API -------------------------------------------------
    def get(self, flowcell_id: str) -> pd.DataFrame:
        """
        Always returns *something*.
        Raises only if we're in DB mode and the document truly does not exist.
        """
        if self._mock:
            return self._dummy_df.copy()

        # --- real CouchDB path --------------------------------------
        # TODO: Check the id used again when the Samplesheets database is finalised
        doc = self.fetch_document_by_id(flowcell_id)
        csv_bytes = doc["_attachments"]["samplesheet.csv"]["data"]
        return pd.read_csv(io.BytesIO(csv_bytes), dtype=str)


# ---------- HOW TO USE ----------------------------------------------
#
# Option A – let the class auto-detect CouchDB
#   samplesheet_dm = SampleSheetDBManager()
#
# Option B – force mock in dev or CI:
#   samplesheet_dm = SampleSheetDBManager(use_mock=True)
#   # or export SAMPLESHEET_STORE=mock
#
# The rest of the Illumina mix-in stays unchanged:
#   ss_df = self.samplesheet_dm.get(flowcell_id)
