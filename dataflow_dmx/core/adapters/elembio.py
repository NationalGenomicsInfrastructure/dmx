import re

from dataflow_dmx.core.adapters.base import DemuxConfig  # type: ignore
from dataflow_dmx.core.adapters.base import InstrumentAdapter

# NOTE: Perhaps better read from a config file or environment variable
AVITI_DEMUX = "/opt/element/aviti-demux"

# Aviti run-id pattern:
#   20250822_AV242106_A2247654903
#   {YYYYMMDD}_{instrument}_{side}{flowcell}
# where side is 'A' or 'B'
AVITI_RUNID_RE = re.compile(
    r"""
    ^(?P<date>\d{8})_                # YYYYMMDD
    (?P<instrument>AV\d+)_           # AV instrument id
    (?P<side>[AB])(?P<flowcell>\d+)  # side + numeric flowcell
    $""",
    re.VERBOSE,
)


class ElementAdapterMixin(InstrumentAdapter):
    """Any particular functionality shared by Element instruments in the future must be implemented here."""


class AvitiAdapter(ElementAdapterMixin):
    """Adapter for Element Biosciences Aviti."""

    name = "aviti"

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        """Return True iff run_id matches the Aviti pattern."""
        return bool(AVITI_RUNID_RE.match(run_id))

    def extract_flowcell_id(self) -> str:
        # TODO: Check if this is correct for Aviti
        return self.run_id.split("_")[2]

    def build_demux_config(self) -> DemuxConfig:
        cmd = [
            str(AVITI_DEMUX),
            "--input",
            str(self.run_path),
            "--output",
            "/ngi/fastq",
        ]  # Example command, adjust as needed

        return DemuxConfig(
            run_id=self.run_id,
            flowcell_id=self.extract_flowcell_id(),
            lanes=[],  # Does Aviti have lanes? If so, how to extract them?
            samplesheet_path=None,  # Does Aviti operate with samplesheets? If so, how to retrieve them?
            cmd=cmd,
        )
