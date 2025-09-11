import asyncio
from pathlib import Path

import click

from dataflow_dmx.core.pipelines.demux import demux_ppl


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "-p",
    "--run-path",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Absolute path to the run directory on the HPC "
    "(e.g. /miarka/seq-data/illumina/novaseqxplus/20250601_LH...)",
)
@click.option(
    "-i",
    "--instrument",
    required=True,
    metavar="KEY",
    help="Instrument key understood by the adapters "
    "(miseq | nextseq | novaseqxplus | aviti | promethion)",
)
def cli(run_path: Path, instrument: str) -> None:
    """
    Launch the production demux Prefect flow for a single run folder.

    Example
    -------
    \b
    $ dataflow-dmx -p /miarka/seq-data/.../A22TT52LT4 -i novaseqxplus
    """
    asyncio.run(demux_ppl(run_path=str(run_path), instrument=instrument))


if __name__ == "__main__":
    cli()  # pragma: no cover
