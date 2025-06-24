import subprocess
from pathlib import Path

from prefect import flow, get_run_logger, task

from .adapters.adapter_list import ADAPTERS
from .adapters.base import DemuxConfig


@task(retries=2)
def build_config(run_path: Path, instrument: str) -> DemuxConfig:
    logger = get_run_logger()
    adapter_cls = ADAPTERS[instrument.lower()]
    adapter = adapter_cls(run_path)
    cfg = adapter.build_demux_config()
    logger.debug("Built DemuxConfig: %s", cfg.model_dump_json())
    return cfg


@task
def run_demux(cfg: DemuxConfig):
    logger = get_run_logger()
    if not cfg.cmd:  # e.g. PromethION
        logger.info("No demux needed for %s", cfg.run_id)
        return
    logger.info("Running: %s", " ".join(cfg.cmd))
    subprocess.run(cfg.cmd, check=True)


@task
def another_step(cfg: DemuxConfig):
    pass


@flow(name="production_demux_flow")
async def production_demux_flow(run_path: str, instrument: str):
    """
    Parameters
    ----------
    run_path   Absolute path to the run folder on Miarka (HPC).
    instrument Registry key: 'miseq', 'nextseq', 'novaseqxplus', 'aviti', 'promethion'.
    """
    config = build_config(Path(run_path), instrument)
    run_demux(config)
    another_step(config)
    return True
