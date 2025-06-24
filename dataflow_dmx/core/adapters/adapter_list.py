from dataflow_dmx.core.adapters.elembio import AvitiAdapter
from dataflow_dmx.core.adapters.illumina_models import (
    MiSeqAdapter,
    NextSeqAdapter,
    NovaSeqXPlusAdapter,
)
from dataflow_dmx.core.adapters.ont import PromethIONAdapter

ADAPTERS = {
    adapter.name: adapter
    for adapter in (
        MiSeqAdapter,
        NextSeqAdapter,
        NovaSeqXPlusAdapter,
        AvitiAdapter,
        PromethIONAdapter,
    )
}
