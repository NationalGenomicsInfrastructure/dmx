from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel


class DemuxConfig(BaseModel):
    run_id: str
    flowcell_id: str
    lanes: list[int]
    samplesheet_path: Path | None = None
    cmd: list[str] | None = None  # empty for PromethION


class InstrumentAdapter(ABC):
    """Contract every sequencer must implement."""

    name: str  # class attribute used as registry key

    @classmethod
    @abstractmethod
    # Every adapter states its own rules (even if they’re "always true")
    def matches(cls, run_id: str) -> bool: ...

    @abstractmethod
    def extract_flowcell_id(self) -> str: ...

    @abstractmethod
    def build_demux_config(self) -> DemuxConfig: ...

    def __init__(self, run_path: Path):
        """Initialize the adapter with the run directory path.
        Parameters
        ----------
        run_path : Path
            Path to the run directory, e.g. /data/illumina/miseq/250819_M01543_0642_000000000-M5BLC
        """
        self.run_id = run_path.name
        self.run_path = run_path

        # Optional sanity check for validation
        if not self.matches(self.run_id):
            raise ValueError(f"{self.name} adapter got unexpected run_id {self.run_id}")
