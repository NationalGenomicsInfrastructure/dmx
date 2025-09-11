import click
from dmx.dmx import prepare_demux


@click.command()
@click.option(
    "-r",
    "--run",
    required=True,
    help="The run identifier, e.g., 20250528_LH00217_0219_A22TT52LT4.",
)
@click.option(
    "-l",
    "--lanes",
    default=None,
    type=int,
    help="Optional lane numbers to specify specific lanes for demuxing (e.g. 1,2,5).",
)
def cli(run, lanes):
    """
    Command line interface for the dmx module.

    This CLI allows users to specify a run identifier and processes it accordingly.

    Args:
        run (str): The run identifier, e.g., '20250528_LH00217_0219_A22TT52LT4'.
        lanes (int, optional): Specific lane numbers for demultiplexing. If not provided, all lanes are processed.
    """
    prepare_demux(run=run, lanes=None)
