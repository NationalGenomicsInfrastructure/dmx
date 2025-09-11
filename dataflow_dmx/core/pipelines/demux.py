import logging
import subprocess
from pathlib import Path

from dataflow_dmx.core.adapters.adapter_list import ADAPTERS  # type: ignore
from dataflow_dmx.core.adapters.base import DemuxConfig  # type: ignore
from dataflow_dmx.core.utils.step import (
    step,  # For demonstration purposes to imitate (a tracking decorator or Prefect, etc. steps, whatever we decide to use)
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@step  # Example of automatically using the function's name as the step name
def build_config(run_path: Path, instrument: str) -> DemuxConfig:
    adapter_cls = ADAPTERS[instrument.lower()]
    adapter = adapter_cls(run_path)
    cfg = adapter.build_demux_config()
    logger.debug("Built DemuxConfig: %s", cfg.model_dump_json())
    return cfg


@step()  # Also an example of auto-naming a step
def run_demux(cfg: DemuxConfig):
    # logger = get_run_logger()
    if not cfg.cmd:  # e.g. PromethION
        logger.info("No demux needed for %s", cfg.run_id)
        return
    logger.info("Running: %s", " ".join(cfg.cmd))
    # subprocess.run(cfg.cmd, check=True)  # Bypassed since bcl-convert is not installed


@step(
    "do_something"
)  # Example of explicitly overriding a step's name (positional argument)
def another_step(cfg: DemuxConfig):
    pass


@step(
    name="do_soomething_else"
)  # Example of explicitly overriding a step's name (keyword argument)
def yet_another_step(cfg: DemuxConfig):
    pass


async def demux_ppl(run_path: str, instrument: str):
    """
    Parameters
    ----------
    run_path   Absolute path to the run folder on Miarka (HPC).
    instrument Registry key: 'miseq', 'nextseq', 'novaseqxplus', 'aviti', 'promethion'.
    """
    config = build_config(Path(run_path), instrument)
    run_demux(config)
    another_step(config)
    yet_another_step(config)
    return True
