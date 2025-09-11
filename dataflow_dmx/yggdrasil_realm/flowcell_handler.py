import asyncio
import logging
import pathlib
import uuid

import httpcore
import httpx
from yggdrasil.core_utils.event_types import EventType  # type: ignore
from yggdrasil.handlers.base_handler import BaseHandler  # type: ignore

from dataflow_dmx.core.pipelines.demux import demux_ppl

# from prefect.client import get_client


DEPLOYMENT_SLUG = "production-demux/test2-demux-workflow"  # <flow>/<deployment>


def attach_prefect_file_handler():
    run_id = uuid.uuid4().hex[:8]
    log_file = (
        pathlib.Path(
            "/home/anastasios/Documents/git/Yggdrasil/yggdrasil_workspace/logs/prefect"
        )
        / f"run-{run_id}.log"
    )
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s - %(message)s")
    )
    p_logger = logging.getLogger("prefect")
    p_logger.handlers.clear()
    p_logger.addHandler(handler)
    p_logger.setLevel(logging.INFO)
    p_logger.propagate = False  # stops bubbling to Yggdrasil stdout

    # The two extra chatty packages you still saw
    for noisy in (
        "prefect._internal.concurrency",
        "prefect.events",
        "GlobalEventLoopThread",
        "httpcore",
        "graphviz",
        "aiosqlite",
    ):
        logging.getLogger(noisy).setLevel(logging.CRITICAL)

    return handler, p_logger


class FlowcellHandler(BaseHandler):
    event_type = EventType.FLOWCELL_READY

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("FlowcellHandler")

    # async def queue_demux_run(self, run_path: str, instrument: str) -> None:
    #     async with get_client() as client:
    #         # 1. resolve the deployment record
    #         deployment = await client.read_deployment_by_name(DEPLOYMENT_SLUG)
    #         # 2. enqueue a run
    #         await client.create_flow_run_from_deployment(
    #             deployment.id,
    #             parameters={"run_path": run_path, "instrument": instrument},
    #             tags=["production", "illumina"],
    #         )

    async def handle_task(self, payload):
        run_path = payload["subfolder"]
        instrument = payload["instrument"]
        self.logger.info(
            "Invoking demux flow for %s (%s)", pathlib.Path(run_path).name, instrument
        )

        handler, p_logger = attach_prefect_file_handler()
        result = None
        try:
            # Run the demux flow directly
            result = await demux_ppl(run_path, instrument)

            self.logger.info("Flow run requested for %s", run_path)

        except FileNotFoundError as e:
            self.logger.error("A required file is missing: %s", e)
        # network‐layer errors from httpcore
        except (OSError, httpcore.ConnectError, ConnectionRefusedError) as e:
            self.logger.error(
                "Network error contacting Prefect API: %s; skipping demux for %r",
                e,
                run_path,
            )

        except httpx.HTTPStatusError as e:
            # API is up but returned a 4xx/5xx
            self.logger.error(
                "Prefect API returned HTTP %d when scheduling demux for %r: %s",
                e.response.status_code,
                run_path,
                e,
            )

        except RuntimeError as e:
            # Prefect sometimes wraps these as RuntimeError("Failed to reach API ...")
            msg = str(e)
            if msg.startswith("Failed to reach API"):
                self.logger.error(
                    "Prefect orchestration runtime error: %s; skipping %r",
                    msg,
                    run_path,
                )
            else:
                # if it’s something else, re‐raise so we don’t hide bugs
                raise

        except Exception as e:
            # any other unexpected failure
            self.logger.error(
                "Unexpected error scheduling Prefect flow for %s: %s",
                run_path,
                e,
                exc_info=True,
            )
        finally:
            p_logger.removeHandler(handler)
            self.logger.info("Demux flow run completed for %s: %s", run_path, result)

    def __call__(self, payload):
        """
        Schedule handle_task under asyncio.create_task().
        """
        self.logger.debug("Calling flowcell handler for %s", payload)
        try:
            asyncio.create_task(self.handle_task(payload))
        except RuntimeError:
            # No running loop? fallback to ensure_future if appropriate
            # TODO: might be needed for standalone calls, remove if not
            loop = asyncio.get_event_loop()
            loop.create_task(self.handle_task(payload))
