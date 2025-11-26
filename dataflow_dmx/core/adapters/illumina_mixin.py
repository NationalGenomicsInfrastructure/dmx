import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import ClassVar

import pandas as pd  # type: ignore

from dataflow_dmx.core.adapters.base import DemuxConfig  # type: ignore
from dataflow_dmx.core.adapters.base import InstrumentAdapter
from dataflow_dmx.core.utils.samplesheet_db_manager import (
    SampleSheetDBManager,
)  # type: ignore

# NOTE: Perhaps better read from a config file or environment variable
BCL_CONVERT = "/path/to/bcl-convert"


class IlluminaAdapterMixin(InstrumentAdapter):
    """Shared helpers for all Illumina instruments."""

    RUNID_RE: ClassVar[re.Pattern[str] | None] = None

    samplesheet_dm = SampleSheetDBManager()
    logger = logging.getLogger("IlluminaAdapterMixin")

    def extract_flowcell_id(self) -> str:
        """
        Extract the flowcell identifier (`fcid`) from the run ID.

        Each Illumina adapter class must define a `RUNID_RE` regex that includes
        a named capture group `(?P<fcid>...)`. This method uses that group to
        return the flowcell ID.

        Returns
        -------
        str
            The flowcell ID captured by the adapter's `RUNID_RE`.

        Raises
        ------
        ValueError
            If `RUNID_RE` is missing, does not match the run ID, or does not
            define an `fcid` group.
        """
        if getattr(self, "RUNID_RE", None) is None:
            raise ValueError(f"{self.name}: RUNID_RE is not defined")

        m = self.RUNID_RE.match(self.run_id)  # type: ignore[attr-defined]
        if not m or "fcid" not in m.groupdict():
            raise ValueError(
                f"{getattr(self, 'name', self.__class__.__name__)}: "
                f"run_id {self.run_id!r} does not match expected pattern "
                "or missing 'fcid' group"
            )
        return m.group("fcid")

    def read_samplesheet(self, flowcell_id: str) -> pd.DataFrame:
        # return empty DataFrame if not found
        sample_sheet: pd.DataFrame = (
            self.samplesheet_dm.get(flowcell_id) or pd.DataFrame()
        )

        if sample_sheet.empty:
            self.logger.warning(
                f"No SampleSheet found for flowcell {flowcell_id}, returning empty DataFrame"
            )
        return sample_sheet

    def transform_samplesheet(self, samplesheet: pd.DataFrame) -> pd.DataFrame:
        """Transform the samplesheet to the expected format."""
        return samplesheet

    def write_samplesheet_to_csv(
        self, samplesheet: pd.DataFrame, run_path: Path
    ) -> Path | None:
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
        # TODO: Add more params if needed, e.g. "-bcl-input-directory", "--output-dir", etc.
        params += ["--bcl-input-directory", str(self.run_path)]
        params += [
            "--output-directory",
            str(self.run_path / "fastq"),  # Perhaps get from config?
        ]
        if ss:
            params += ["--sample-sheet", str(ss)]
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
        return [
            "--first-tile-only",
            "false",
        ]  # set default params, NOTE: this is only an example!
