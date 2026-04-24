import logging

from yggdrasil.flow.artifacts import SimpleArtifactRef
from yggdrasil.flow.model import StepResult
from yggdrasil.flow.step import StepContext, step

from .utils import render_bcl_convert_samplesheet, validate_lane_payload

logger = logging.getLogger(__name__)


@step
def validate_runfolder(ctx: StepContext, scenario: dict) -> StepResult:
    """Validates that the runfolder exists in the HPC."""
    hpc_path = scenario["hpc_runfolder_path"]
    logger.info(f"Validating expected HPC runfolder path: {hpc_path}")

    # Normally we would os.path.isdir(hpc_path) or ssh verify it
    # We will pretend it exists successfully
    return StepResult(metrics={"path_validated": hpc_path})


@step
def materialize_extra_config(ctx: StepContext, scenario: dict) -> StepResult:
    """Materializes the extra demultiplex config file."""
    config_file = ctx.workdir / "extra_config_demultiplex.config"
    logger.info(f"Materializing config to {config_file}")

    # Writing a mock standard config
    config_file.write_text("process {\n  executor = 'local'\n  cpus = 4\n}")

    ctx.record_artifact(SimpleArtifactRef("demux_config", "config"), path=config_file)
    return StepResult(metrics={"config_bytes": config_file.stat().st_size})


@step
def generate_samplesheet(ctx: StepContext, scenario: dict) -> StepResult:
    """Generates and writes SampleSheet.csv from the lane-specific samplesheet payload."""
    ss_payload = scenario["samplesheet_payload"]

    validate_lane_payload(ss_payload)
    ss_text = render_bcl_convert_samplesheet(ss_payload)

    ss_file = ctx.workdir / "SampleSheet.csv"
    ss_file.write_text(ss_text)

    logger.info("Wrote SampleSheet.csv (%d bytes) to %s", ss_file.stat().st_size, ss_file)
    ctx.record_artifact(SimpleArtifactRef("samplesheet", "samplesheets"), path=ss_file)
    return StepResult(metrics={"samplesheet_bytes": ss_file.stat().st_size})


@step
def execute_demux(ctx: StepContext, scenario: dict) -> StepResult:
    """Simulates Nextflow pipeline execution."""
    logger.info("Executing demux pipeline (Nextflow)...")
    logger.info(f"Using runfolder: {scenario['hpc_runfolder_path']}")
    logger.info("Simulation mode: Pipeline executed successfully.")

    return StepResult(metrics={"execution_status": "simulated_success"})


@step
def collect_results(ctx: StepContext, scenario: dict) -> StepResult:
    """Collects demultiplexing metrics, artifacts and logs."""
    logger.info("Collecting metrics from demux result directory...")

    return StepResult(metrics={"yield": 120000000, "q30_percentage": 98.4})


@step
def upload_results(ctx: StepContext, scenario: dict) -> StepResult:
    """Uploads metrics and artifacts to appropriate endpoints (simulated)."""
    logger.info("Uploading metrics to remote API...")
    scenario_metadata = scenario.get("demux_sample_info_doc", {}).get("metadata", {})
    logger.info(
        f"Simulating upload for run {scenario['runfolder_id']} with metadata {scenario_metadata}"
    )

    return StepResult(metrics={"upload_status": "simulated_success"})
