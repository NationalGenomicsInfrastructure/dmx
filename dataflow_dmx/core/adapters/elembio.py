import re
from pathlib import Path

from dataflow_dmx.core.adapters.base import DemuxConfig  # type: ignore
from dataflow_dmx.core.adapters.base import InstrumentAdapter

# NOTE: Perhaps better read from a config file or environment variable
AVITI_DEMUX = "/opt/element/aviti-demux"


class ElementAdapterMixin(InstrumentAdapter):
    """Any particular functionality shared by Element instruments in the future must be implemented here."""


class AvitiAdapter(ElementAdapterMixin):
    """Adapter for Element Biosciences Aviti."""

    name = "aviti"

    # Aviti run-id pattern:
    #   20250822_AV242106_A2247654903
    #   {YYYYMMDD}_{instrument}_{side}{flowcell}
    # where side is 'A' or 'B'
    RUNID_RE = re.compile(
        r"""
        ^(?P<date>\d{8})_               # YYYYMMDD
        (?P<instrument>AV\d+)_          # AV instrument id
        (?P<side>[AB])(?P<fcid>\d+)$    # side + numeric flowcell
        """,
        re.VERBOSE,
    )

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        """Return True iff run_id matches the Aviti pattern."""
        return bool(cls.RUNID_RE.match(run_id))

    def extract_flowcell_id(self) -> str:
        """
        Return side+flowcell (e.g. 'A2247654903').
        Fail fast if run_id is malformed.
        """
        m = self.RUNID_RE.match(self.run_id)
        if not m:
            # Raise early with context;
            raise ValueError(
                f"{self.name}: run_id {self.run_id!r} does not match Aviti pattern "
                r"'YYYYMMDD_AV<digits>_<side><flowcell>'"
            )
        return f"{m.group('side')}{m.group('flowcell')}"

    def _aviti_lanes(self) -> list[int]:
        """
        Placeholder: read 'AnalysisLanes' from RunParameters.json to get the number of lanes used (1-2).
        "Production-team" can implement the exact JSON parsing; default conservatively to returning [1].
        """
        return [1]

    def _samplesheet_path(self) -> Path | None:
        """
        Placeholder: LIMS provides SampleSheet; transport TBD (StatusDB, bundled w/ run, etc.).
        Return None until the decision is implemented. Could be Path or the whole samplesheet content.
        """
        return None

    def build_demux_config(self) -> DemuxConfig:
        flowcell = self.extract_flowcell_id()
        lanes = self._aviti_lanes()
        samplesheet = self._samplesheet_path()

        cmd = [
            str(AVITI_DEMUX),
            "--input",
            str(self.run_path),
            "--output",
            "/ngi/fastq",
        ]  # Example command, adjust as needed

        if samplesheet:
            cmd += ["--sample-sheet", str(samplesheet)]

        return DemuxConfig(
            run_id=self.run_id,
            flowcell_id=flowcell,
            lanes=lanes,
            samplesheet_path=samplesheet,
            cmd=cmd,
        )
