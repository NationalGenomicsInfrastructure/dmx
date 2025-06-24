import re

from .illumina_mixin import IlluminaAdapterMixin


class MiSeqAdapter(IlluminaAdapterMixin):
    """Adapter for MiSeq instruments.
    This class handles the specifics of MiSeq parameters and behavior
    """

    name = "miseq"

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        # TODO: check if this is correct for MiSeq
        # return re.match(r"\d{6}_M\d{5}_\d{4}_\d{9}", run_id)
        return True

    def _bcl_convert_params(self):
        # TODO: check if this is correct for MiSeq
        return super()._bcl_convert_params() + ["--tiles-per-lane", "all"]


class NextSeqAdapter(IlluminaAdapterMixin):
    """Adapter for NextSeq instruments.
    This class handles the specifics of NextSeq parameters and behavior
    """

    name = "nextseq"

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        # TODO: check if this is correct for NextSeq
        return re.match(r"\d{6}_VH\d{5}_\d{4}_[A-Z0-9]{10}", run_id)


class NovaSeqXPlusAdapter(IlluminaAdapterMixin):
    """Adapter for NovaSeq X Plus instruments.
    This class handles the specifics of NovaSeq X Plus parameters and behavior
    """

    name = "novaseqxplus"

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        # TODO: check if this is correct for NovaSeq X Plus
        return "_LH" in run_id

    def extract_flowcell_id(self) -> str:
        # Meet NovaSeq X Plus' needs by overriding the default behavior
        token = self.run_id.split("_")[-1]
        return token[-9:]

    def _bcl_convert_params(self):
        # TODO: check if this is correct for NovaSeq X Plus
        return ["--barcode-mismatches", "0", "--ignore-missing-bcl"]
