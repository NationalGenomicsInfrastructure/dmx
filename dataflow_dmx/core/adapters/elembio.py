from core.adapters.base import DemuxConfig, InstrumentAdapter  # type: ignore

# NOTE: Perhaps better read from a config file or environment variable
AVITI_DEMUX = "/opt/element/aviti-demux"


class ElementAdapterMixin(InstrumentAdapter):
    """Any particular functionality shared by Element instruments in the future must be implemented here."""


class AvitiAdapter(ElementAdapterMixin):
    name = "aviti"

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        # TODO: Check if this is correct for Aviti
        return run_id.startswith("AV")

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
