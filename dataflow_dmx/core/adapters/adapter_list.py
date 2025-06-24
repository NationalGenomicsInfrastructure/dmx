from .elembio import AvitiAdapter
from .illumina_models import MiSeqAdapter, NextSeqAdapter, NovaSeqXPlusAdapter
from .ont import PromethIONAdapter

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
