from .elembio import AvitiAdapter  # type: ignore
from .illumina_models import (  # type: ignore
    MiSeqAdapter,
    NextSeqAdapter,
    NovaSeqXPlusAdapter,
)
from .ont import PromethIONAdapter  # type: ignore

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
