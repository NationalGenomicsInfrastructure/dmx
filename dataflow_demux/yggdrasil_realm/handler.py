import logging
import os
from typing import Any, ClassVar

from lib.core_utils.event_types import EventType
from yggdrasil.flow.base_handler import BaseHandler
from yggdrasil.flow.model import Plan
from yggdrasil.flow.planner import PlanDraft, PlanningContext

from .recipes import demux_pipeline
from .utils import normalize_flowcell_id

logger = logging.getLogger(__name__)


class DemuxHandler(BaseHandler):
    event_type: ClassVar[EventType] = EventType.COUCHDB_DOC_CHANGED
    handler_id: ClassVar[str] = "demux_handler"

    def derive_scope(self, doc: dict[str, Any]) -> dict[str, Any]:
        """
        Since build_scope already generates the clean dict, but derive_scope is required
        for direct handler triggers or injections, we can parse it from doc.
        """
        fcid = doc.get("flowcell_id", doc.get("_id", "unknown"))
        return {"kind": "flowcell", "id": normalize_flowcell_id(fcid)}

    def _deferred(self, ctx: PlanningContext, note: str) -> PlanDraft:
        """Return an empty deferred PlanDraft with a descriptive note."""
        return PlanDraft(
            plan=Plan(
                plan_id=f"{self.realm_id}:{ctx.scope.get('id', 'unknown')}",
                realm=self.realm_id or "dmx_realm",
                scope=ctx.scope,
                steps=[],
            ),
            auto_run=False,
            approvals_required=[],
            notes=f"Deferred: {note}",
        )

    def _get_last_event(self, events: list, event_type: str) -> dict | None:
        """Helper to find the last occurring event of a certain type"""
        matches = [
            e
            for e in events
            if e.get("event") == event_type
            or e.get("type") == event_type
            or e.get("event_type") == event_type
        ]
        if not matches:
            return None
        return matches[-1]

    async def generate_plan_draft(self, payload: dict[str, Any]) -> PlanDraft:
        ctx: PlanningContext = payload["planning_ctx"]
        source_db = payload.get("source", "unknown")

        logger.info(f"Planning demux triggered by {source_db}")

        demux_db = ctx.data.couchdb("demux_sample_info_db")
        yfc_db = ctx.data.couchdb("flowcell_status_db")

        if source_db == "demux_sample_info":
            # CouchDB 3.x ignores include_docs via POST body (IBM SDK limitation),
            # so doc is not embedded in the change event. Fetch it by _id directly.
            doc_id = payload.get("doc_id") or ctx.scope.get("id", "")
            if not doc_id:
                return self._deferred(ctx, "demux_sample_info trigger missing doc_id.")
            if doc_id.startswith("_"):
                # Design docs and internal CouchDB documents — should be filtered by
                # WatchSpec.filter_expr but guard here as defense-in-depth.
                return self._deferred(
                    ctx, f"Skipping internal CouchDB document '{doc_id}'."
                )

            demux_doc = await demux_db.get(doc_id)
            if not demux_doc:
                return self._deferred(
                    ctx, f"demux_sample_info document '{doc_id}' not found or deleted."
                )

            canonical_fcid = normalize_flowcell_id(demux_doc.get("flowcell_id", ""))
            if not canonical_fcid:
                return self._deferred(
                    ctx, "demux_sample_info document missing flowcell_id."
                )

            yfc_doc = await yfc_db.find_one(
                {"flowcell_id": {"$in": [canonical_fcid, f"A{canonical_fcid}"]}}
            )

        else:
            # flowcell_status: _id is a UUID hash; flowcell_id is a separate field.
            # The watcher performs a separate GET per document, so payload["doc"] is populated.
            canonical_fcid = ctx.scope.get("id", "")
            if not canonical_fcid:
                return self._deferred(
                    ctx,
                    "flowcell_status trigger missing canonical flowcell_id in scope.",
                )

            yfc_doc = payload.get("doc") or None
            if not yfc_doc:
                return self._deferred(
                    ctx, "flowcell_status trigger missing document in payload."
                )

            demux_doc = await demux_db.find_one(
                {"flowcell_id": {"$in": [canonical_fcid, f"A{canonical_fcid}"]}}
            )

        logger.info(f"Planning demux for {canonical_fcid} triggered by {source_db}")

        if not yfc_doc:
            return self._deferred(
                ctx,
                f"No flowcell_status document found for flowcell_id '{canonical_fcid}'.",
            )
        if not demux_doc:
            return self._deferred(
                ctx,
                f"No demux_sample_info document found for flowcell_id '{canonical_fcid}'.",
            )

        # Readiness Checks
        events = yfc_doc.get("events", [])
        transferred_event = self._get_last_event(events, "transferred_to_hpc")
        final_transfer_event = self._get_last_event(events, "final_transfer_started")

        if not transferred_event:
            return self._deferred(
                ctx, "flowcell_status missing 'transferred_to_hpc' event."
            )

        if not final_transfer_event:
            return self._deferred(
                ctx, "flowcell_status missing 'final_transfer_started' event."
            )

        destination_path = final_transfer_event.get("data", {}).get("destination_path")
        if not destination_path:
            return self._deferred(
                ctx, "final_transfer_started event missing destination_path."
            )

        runfolder_id = yfc_doc.get("runfolder_id", yfc_doc.get("runfolder_name"))
        if not runfolder_id:
            return self._deferred(ctx, "flowcell_status missing runfolder_id.")

        samplesheets = demux_doc.get(
            "uploaded_lims_info", demux_doc.get("samplesheets", [])
        )
        if not samplesheets:
            return self._deferred(ctx, "demux_sample_info missing samplesheets.")

        selected_samplesheet = (
            samplesheets[0] if isinstance(samplesheets[0], dict) else samplesheets
        )

        hpc_runfolder_path = os.path.join(destination_path, runfolder_id)

        scenario = {
            "canonical_flowcell_id": canonical_fcid,
            "triggering_source": source_db,
            "hpc_runfolder_path": hpc_runfolder_path,
            "runfolder_id": runfolder_id,
            "samplesheet_payload": selected_samplesheet,
            "flowcell_status_doc": {
                "_id": yfc_doc.get("_id"),
                "_rev": yfc_doc.get("_rev"),
            },
            "demux_sample_info_doc": {
                "_id": demux_doc.get("_id"),
                "_rev": demux_doc.get("_rev"),
                "metadata": demux_doc.get("metadata", {}),
            },
        }

        steps = demux_pipeline(scenario=scenario)

        plan = Plan(
            plan_id=f"{self.realm_id}:{canonical_fcid}",
            realm=self.realm_id or "dmx_realm",
            scope=ctx.scope,
            steps=steps,
        )

        return PlanDraft(
            plan=plan,
            auto_run=True,
            approvals_required=[],
            notes="Ready for demultiplexing",
            preview={"scenario": scenario, "step_count": len(steps)},
        )
