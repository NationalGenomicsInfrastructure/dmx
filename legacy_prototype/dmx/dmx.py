import logging
import os
import pandas as pd

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
    sequencer_type = determine_sequencer(run)
    flow_cell_id = get_flow_cell_id(run, sequencer_type)
    sample_sheet_path = get_samplesheet_path(flow_cell_id, sequencer_type)

    # Read the samplesheet
    df = pd.read_csv(sample_sheet_path, comment="#", dtype=str)

    # Separate the samples into groups based on lane
    if not lanes:
        lanes = df["Lane"].unique()
    for lane in lanes:
        sub_sample_sheet = df[df["Lane"] == lane]
        
    # Separate samples in each lane into groups based on index type
    # Generate sub-sample sheets for each group
    # Generate demux command for each group


def determine_sequencer(run):
    """
    Determine the sequencer type based on the run identifier.

    Args:
        run (str): The run identifier, e.g., '20250528_LH00217_0219_A22TT52LT4'.

    Returns:
        str: The sequencer type, e.g., 'miseq' or 'aviti'.
    """
    instrument_id = run.split("_")[1]
    if instrument_id.startswith("M") and "-" in run:
        return "miseq"
    elif instrument_id.startswith("AV"):
        return "aviti"
    elif instrument_id.startswith("VH"):
        return "nextseq"
    elif instrument_id.startswith("LH"):
        return "novaseqxplus"


def get_flow_cell_id(run, sequencer_type):
    """
    Extract the flow cell ID from the run string.

    Args:
        run (str): The run identifier, e.g., '20250528_LH00217_0219_A22TT52LT4'.
        sequencer_type (str): The type of sequencer, e.g., 'miseq' or 'aviti'.

    Returns:
        str: The extracted flow cell ID.
    """
    parts = run.split("_")
    if sequencer_type == "novaseqxplus":
        return parts[-1][-9:]
    else:
        return parts[-1]


def get_samplesheet_path(flow_cell_id, sequencer_type):
    """
    Get the path to the samplesheet based on the flow cell ID and sequencer type.

    Args:
        flow_cell_id (str): The flow cell ID.
        sequencer_type (str): The type of sequencer, e.g., 'illumina'.

    Returns:
        str: The path to the samplesheet.
    """
    sample_sheet_path = "/Users/sara.sjunnebo/code/scratch/pre_demux_testing/example_sample_sheets"  # TODO: change this to a config file
    if sequencer_type == "miseq":
        return os.path.join(sample_sheet_path, "SampleSheet.csv")
    elif sequencer_type == "aviti":
        return os.path.join(
            sample_sheet_path, flow_cell_id + ".csv"
        )  # TODO: change name here or in lims epp
    else:
        return os.path.join(sample_sheet_path, flow_cell_id + ".csv")


def prepare_demux(run, lanes=None):
    """Prepare the demultiplexing commands for the given run."""
    logger.debug("Starting up predemux CLI")
    prepare_flow_cell(run, lanes)
