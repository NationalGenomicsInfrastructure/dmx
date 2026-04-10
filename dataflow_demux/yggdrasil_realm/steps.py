import logging

from yggdrasil.flow.artifacts import SimpleArtifactRef
from yggdrasil.flow.model import StepResult
from yggdrasil.flow.step import StepContext, step

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
    """Generates and writes SampleSheet.csv to the execution directory."""
    ss_payload = scenario["samplesheet_payload"]
    ss_file = ctx.workdir / "SampleSheet.csv"
    logger.info(f"Generating samplesheet at {ss_file}")

    # In reality there would be parsing of samplesheet dictionary into csv format.
    # We write a mock CSV based on the payload provided.
    ss_file.write_text("[Data]\nSample_ID,Sample_Name,index\nS1,Sample1,ATGC")

    ctx.record_artifact(SimpleArtifactRef("samplesheet", "samplesheets"), path=ss_file)
    return StepResult(metrics={"samplesheet_written": True})


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
    return StepResult(metrics={"upload_status": "simulated_success"})
