import re
from pathlib import Path
from typing import ClassVar

from dataflow_dmx.core.adapters.base import DemuxConfig  # type: ignore
from dataflow_dmx.core.adapters.base import InstrumentAdapter


class PromethIONAdapter(InstrumentAdapter):
    """
    ONT PromethION runs are already demultiplexed on-instrument.

    Example run-id: 20250823_1607_3C_PBG38503_bece6143
                    <YYYYMMDD>_<HHMM>_<token>_<FLOWCELL>_<runhash>
    """

    name = "promethion"

    RUNID_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"""
        ^(?P<date>\d{8})_            # YYYYMMDD
        (?P<hhmm>\d{4})_             # HHMM
        (?P<token>[A-Za-z0-9]+)_     # e.g. "3C" (varies)
        (?P<flowcell>[A-Za-z0-9]+)_  # e.g. "PBG38503"
        (?P<hash>[a-f0-9]+)$         # run hash
        """,
        re.VERBOSE | re.IGNORECASE,
    )

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        return bool(cls.RUNID_RE.match(run_id))

    def extract_flowcell_id(self) -> str:
        """
        Return the flowcell ID (e.g. "PBG38503").
        Fail fast if run_id is malformed.
        """
        m = self.RUNID_RE.match(self.run_id)
        if not m:
            raise ValueError(
                f"{self.name}: run_id {self.run_id!r} does not match "
                r"'YYYYMMDD_HHMM_token_FLOWCELL_hash'"
            )

        return m.group("flowcell")

    def _samplesheet_path(self) -> Path | None:
        """
        A samplesheet may exist for ONT but might not get used post-demux.
        Keep None for now; we can revisit later if needed.
        """
        return None

    def build_demux_config(self) -> DemuxConfig:
        # NOTE: ONT PromethION does not require demultiplexing
        # Nothing to run; just inform downstream tasks
        return DemuxConfig(
            run_id=self.run_id,
            flowcell_id=self.extract_flowcell_id(),
            lanes=[],  # No lanes for PromethION
            samplesheet_path=None,  # No samplesheets for PromethION?
            cmd=None,  # No demux step (already done on-instrument)
        )
