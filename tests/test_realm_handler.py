from unittest.mock import AsyncMock, MagicMock

import pytest

from dataflow_demux.yggdrasil_realm.descriptor import (
    _build_demux_sample_info_scope,
    _build_flowcell_status_scope,
)
from dataflow_demux.yggdrasil_realm.handler import DemuxHandler


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.scope = {"kind": "flowcell", "id": "SC123"}

    ctx.db_mocks = {
        "demux_sample_info_db": AsyncMock(),
        "flowcell_status_db": AsyncMock(),
    }

    def couchdb_mock(db_name):
        return ctx.db_mocks[db_name]

    ctx.data.couchdb.side_effect = couchdb_mock
    return ctx


@pytest.mark.asyncio
async def test_canonical_matching_scope():
    event_sc = MagicMock(doc={"flowcell_id": "SC123"})
    event_asc = MagicMock(doc={"flowcell_id": "ASC123"})

    assert _build_demux_sample_info_scope(event_sc) == {
        "kind": "flowcell",
        "id": "SC123",
    }
    assert _build_demux_sample_info_scope(event_asc) == {
        "kind": "flowcell",
        "id": "SC123",
    }

    assert _build_flowcell_status_scope(event_sc) == {"kind": "flowcell", "id": "SC123"}
    assert _build_flowcell_status_scope(event_asc) == {
        "kind": "flowcell",
        "id": "SC123",
    }


@pytest.mark.asyncio
async def test_identical_plan_reconstruction(mock_ctx):
    handler = DemuxHandler()
    handler.realm_id = "dmx_realm"

    yfc_doc = {
        "_id": "uuid-yfc-sc123",
        "flowcell_id": "SC123",
        "runfolder_id": "230314_A00000_0000_AXXXXX",
        "events": [
            {"event_type": "transferred_to_hpc"},
            {
                "event_type": "final_transfer_started",
                "data": {"destination_path": "/incoming/path"},
            },
        ],
    }
    demux_doc = {
        "_id": "uuid123",
        "flowcell_id": "SC123",
        "samplesheets": [{"Sample_ID": "S1"}],
    }

    # demux_sample_info trigger: fetches demux_doc by _id (get), then yfc_doc by find_one
    mock_ctx.db_mocks["demux_sample_info_db"].get.return_value = demux_doc
    mock_ctx.db_mocks["flowcell_status_db"].find_one.return_value = yfc_doc

    # flowcell_status trigger: yfc_doc comes from payload["doc"], fetches demux_doc by find_one
    mock_ctx.db_mocks["demux_sample_info_db"].find_one.return_value = demux_doc

    payload1 = {"source": "demux_sample_info", "planning_ctx": mock_ctx}
    plan1 = await handler.generate_plan_draft(payload1)

    payload2 = {"source": "flowcell_status", "doc": yfc_doc, "planning_ctx": mock_ctx}
    plan2 = await handler.generate_plan_draft(payload2)

    # Plans should have the same auto_run, exactly 6 steps, same step configs.
    assert plan1.auto_run is True
    assert len(plan1.plan.steps) == 6
    assert plan2.auto_run is True
    assert len(plan2.plan.steps) == 6
    # Same canonical_flowcell_id should be in the scenario payload and destination path derived
    p1_scenario = plan1.preview["scenario"]
    p2_scenario = plan2.preview["scenario"]
    assert p1_scenario["canonical_flowcell_id"] == "SC123"
    assert (
        p1_scenario["hpc_runfolder_path"] == "/incoming/path/230314_A00000_0000_AXXXXX"
    )

    # Only the triggering source should be different
    assert p1_scenario["triggering_source"] == "demux_sample_info"
    assert p2_scenario["triggering_source"] == "flowcell_status"


@pytest.mark.asyncio
async def test_missing_counterpart_defer(mock_ctx):
    handler = DemuxHandler()
    handler.realm_id = "dmx_realm"

    # Only YFC is present, Demux missing.
    # flowcell_status trigger: yfc_doc comes from payload["doc"], demux_doc is None.
    yfc_doc = {"_id": "uuid-yfc-sc123", "flowcell_id": "SC123"}
    mock_ctx.db_mocks["demux_sample_info_db"].find_one.return_value = None

    payload = {"source": "flowcell_status", "doc": yfc_doc, "planning_ctx": mock_ctx}
    plan = await handler.generate_plan_draft(payload)

    assert plan.auto_run is False
    assert "No demux_sample_info document found" in plan.notes


@pytest.mark.asyncio
async def test_transferred_to_hpc_absent_defer(mock_ctx):
    handler = DemuxHandler()
    handler.realm_id = "dmx_realm"

    # Both present, but YFC missing transferred_to_hpc event.
    # demux_sample_info trigger: fetches demux_doc by _id (get), then yfc_doc by find_one.
    yfc_doc = {
        "_id": "uuid-yfc-sc123",
        "flowcell_id": "SC123",
        "runfolder_id": "230314_A00000_0000_AXXXXX",
        "events": [
            {
                "event_type": "final_transfer_started",
                "data": {"destination_path": "/incoming/path"},
            }
        ],  # missing "transferred_to_hpc"
    }
    demux_doc = {
        "_id": "uuid123",
        "flowcell_id": "SC123",
        "samplesheets": [{"Sample_ID": "S1"}],
    }

    mock_ctx.db_mocks["demux_sample_info_db"].get.return_value = demux_doc
    mock_ctx.db_mocks["flowcell_status_db"].find_one.return_value = yfc_doc

    payload = {"source": "demux_sample_info", "planning_ctx": mock_ctx}
    plan = await handler.generate_plan_draft(payload)

    assert plan.auto_run is False
    assert "Deferred: flowcell_status missing 'transferred_to_hpc' event" in plan.notes
    assert plan.auto_run is False
    assert "Deferred: flowcell_status missing 'transferred_to_hpc' event" in plan.notes
