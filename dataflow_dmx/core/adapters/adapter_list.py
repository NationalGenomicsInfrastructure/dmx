from core.adapters.elembio import AvitiAdapter  # type: ignore
from core.adapters.illumina_models import (  # type: ignore
    MiSeqAdapter,
    NextSeqAdapter,
    NovaSeqXPlusAdapter,
)
from core.adapters.ont import PromethIONAdapter  # type: ignore

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
