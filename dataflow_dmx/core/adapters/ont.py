from .base import DemuxConfig, InstrumentAdapter


class PromethIONAdapter(InstrumentAdapter):
    name = "promethion"

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        # TODO: Check if this is correct for PromethION
        return run_id.startswith("P") or "promethion" in run_id.lower()

    def extract_flowcell_id(self, run_id: str) -> str:
        # TODO: Check if this is correct for PromethION
        return run_id.split("_")[-1]

    def build_demux_config(self) -> DemuxConfig:
        # NOTE: ONT PromethION does not require demultiplexing
        # Nothing to run; just inform downstream tasks
        return DemuxConfig(
            run_id=self.run_id,
            flowcell_id=self.extract_flowcell_id(self.run_id),
            lanes=[1],  # lanes irrelevant for PromethION?
            samplesheet_path=None,  # No samplesheets for PromethION?
            cmd=None,  # No command to run for PromethION (no demux needed)
        )
