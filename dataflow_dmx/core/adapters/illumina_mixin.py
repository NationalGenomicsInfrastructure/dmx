import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import couchdb  # type: ignore
import pandas as pd  # type: ignore

from core.utils.samplesheet_db_manager import (  # type: ignore
    SampleSheetDBManager,
)
from core.adapters.base import DemuxConfig, InstrumentAdapter  # type: ignore

# NOTE: Perhaps better read from a config file or environment variable
BCL_CONVERT = "/path/to/bcl-convert"


class IlluminaAdapterMixin(InstrumentAdapter):
    """Shared helpers for all Illumina instruments."""

    samplesheet_dm = SampleSheetDBManager()
    logger = logging.getLogger("IlluminaAdapterMixin")

    def extract_flowcell_id(self) -> str:
        """
        Default Illumina behaviour: last underscore-separated token.
        Override if a model deviates (e.g. NovaSeq X Plus).
        """
        return self.run_id.split("_")[-1]

    def read_samplesheet(self, flowcell_id: str) -> pd.DataFrame:
        try:
            return self.samplesheet_dm.get(flowcell_id)
        except couchdb.http.ResourceNotFound:
            self.logger.warning(
                f"SampleSheet for flowcell {flowcell_id} not found in CouchDB"
            )
            return pd.DataFrame()  # return empty DataFrame if not found

    def transform_samplesheet(self, samplesheet: pd.DataFrame) -> pd.DataFrame:
        """Transform the samplesheet to the expected format."""
        return samplesheet

    def write_samplesheet_to_csv(
        self, samplesheet: pd.DataFrame, run_path: Path
    ) -> Optional[Path]:
        """Write the samplesheet to a CSV file in the run directory. Return the path."""
        if not samplesheet.empty:
            csv_path = run_path / "SampleSheet.csv"
            samplesheet.to_csv(csv_path, index=False)
            self.logger.info(f"Samplesheet written to {csv_path}")
            return csv_path
        else:
            self.logger.warning("Empty samplesheet, not writing to CSV.")
            return None

    def _illumina_lanes(self, run_path: Path) -> list[int]:
        # Parse the RunInfo.xml to extract lanes? I thought it's better to automatically get all the lanes rather than parameterize the number
        # Production may have reasons to use only a subset of lanes, in which case we discuss
        try:
            xml = ET.parse(run_path / "RunInfo.xml")
        except (ET.ParseError, FileNotFoundError) as e:
            self.logger.error(f"Failed to parse RunInfo.xml: {e}")
            return []
        return [int(e.text) for e in xml.findall(".//Lane") if e.text is not None]

    def build_demux_config(self) -> DemuxConfig:
        lane_list = self._illumina_lanes(self.run_path)

        # TODO: Do we reuse it elsewhere? Make getter/setter if so
        flowcell_id = self.extract_flowcell_id()

        # SampleSheet operations (may also need to store resulting SampleSheet back to CouchDB?)
        ss = self.read_samplesheet(flowcell_id)
        ss = self.transform_samplesheet(ss)
        ss = self.write_samplesheet_to_csv(ss, self.run_path)

        params = self._bcl_convert_params()
        cmd = [BCL_CONVERT, *params]

        return DemuxConfig(
            run_id=self.run_id,
            flowcell_id=flowcell_id,
            lanes=lane_list,
            samplesheet_path=ss,
            cmd=cmd,
        )

    # ----- overridable knobs -----------------------------------------
    def _bcl_convert_params(self) -> list[str]:
        return ["--barcode-mismatches", "1"]  # set default params
