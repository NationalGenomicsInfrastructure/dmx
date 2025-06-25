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
        # By run_id I mean the name of the run directory, e.g. "20250101_L00123_0123_ABCDEFGH". Do you call it something else?
        # NOTE: I assume we can use the dir name as run_id
        self.run_id = run_path.name
        self.run_path = run_path

        # Optional sanity check for validation
        if not self.matches(self.run_id):
            raise ValueError(f"{self.name} adapter got unexpected run_id {self.run_id}")
