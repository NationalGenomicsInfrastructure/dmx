import logging
import pandas as pd
from dmx.RunClasses import MiSeqRun, NextSeqRun, NovaSeqXPlusRun, AvitiRun

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def prepare_flow_cell(run, lanes=None):
    """
    Prepare the flow cell for demultiplexing by locating the samplesheet,
    reading it, separating samples into groups, and generating sub-sample sheets.

    Args:
        flow_cell_id (str): The ID of the flow cell to prepare.
        lanes (int, optional): The lane number to process. If None, all lanes are processed.

    Returns:
        None
    """
    logger.info(f"Preparing flow cell {run} for demultiplexing.")

    # Locate the samplesheet based on the given flow cell
    SeqRun = get_run_object(run)

    # Read the samplesheet
    df = pd.read_csv(SeqRun.sample_sheet, comment="#", dtype=str)

    # Separate the samples into groups based on lane
    if not lanes:
        lanes = df["Lane"].unique()
    for lane in lanes:
        sub_sample_sheet = df[df["Lane"] == lane]
        for sample in sub_sample_sheet["Sample_ID"]:
            sample_group = sub_sample_sheet[sub_sample_sheet["Sample_ID"] == sample]
            # Here you would generate a sub-sample sheet for each group
            # For now, we just log the sample group
            logger.debug(f"Processing sample {sample} in lane {lane}.")
            logger.debug(sample_group)
        # TODO: use get_mask from element_runs in TACA?
    # Separate samples in each lane into groups based on index type
    # Generate sub-sample sheets for each group
    # Generate demux command for each group


def get_run_object(run):
    """
    Initiate the appropriate run object based on the run identifier.

    Args:
        run (str): The run identifier, e.g., '20250528_LH00217_0219_A22TT52LT4'.

    Returns:
        object: An instance of the appropriate run class.
    """
    instrument_id = run.split("_")[1]
    if instrument_id.startswith("M") and "-" in run:
        return MiSeqRun(run)
    elif instrument_id.startswith("AV"):
        return AvitiRun(run)
    elif instrument_id.startswith("VH"):
        return NextSeqRun(run)
    elif instrument_id.startswith("LH"):
        return NovaSeqXPlusRun(run)


def prepare_demux(run, lanes=None):
    """Prepare the demultiplexing commands for the given run."""
    logger.debug("Starting up predemux CLI")
    prepare_flow_cell(run, lanes)
