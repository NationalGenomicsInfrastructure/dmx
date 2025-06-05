import logging
from importlib.metadata import entry_points

import click

from dmx import __version__

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx, config_file):
    """Tool for preparing and managing sequencing data before and after demultiplexing."""
    ctx.obj = {}
    logger.debug("starting up CLI")


# Add subcommands dynamically to the CLI
for entry_point in entry_points(group="dmx.subcommands"):
    cli.add_command(entry_point.load())
