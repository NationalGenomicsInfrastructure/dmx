import re
from typing import ClassVar

from dataflow_dmx.core.adapters.illumina_mixin import (
    IlluminaAdapterMixin,
)  # type: ignore


class MiSeqAdapter(IlluminaAdapterMixin):
    """Adapter for MiSeq instruments.
    This class handles the specifics of MiSeq parameters and behavior
    """

    name = "miseq"

    # Example: 250819_M01543_0642_000000000-M5BLC
    # YYMMDD _ M<5 digits> _ <4 digits> _ <9 digits>-<5 alnum>
    RUNID_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<date>\d{6})_(?P<inst>M\d{5})_(?P<run>\d{4})_(?P<fcid>\d{9}-[A-Z0-9]{5})$"
    )

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        return bool(cls.RUNID_RE.match(run_id))

    def _bcl_convert_params(self):
        # NOTE: Example parameter, adjust as needed
        return super()._bcl_convert_params() + ["--tiles-per-lane", "all"]


class NextSeqAdapter(IlluminaAdapterMixin):
    """Adapter for NextSeq instruments.
    This class handles the specifics of NextSeq parameters and behavior
    """

    name = "nextseq"

    # Example: 250820_VH00203_548_AAH7H2MM5
    # YYMMDD _ VH<5 digits> _ <3 digits> _ <9 alnum>
    RUNID_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<date>\d{6})_(?P<inst>VH\d{5})_(?P<run>\d{3})_(?P<fcid>[A-Z0-9]{9})$"
    )

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        return bool(cls.RUNID_RE.match(run_id))


class NovaSeqXPlusAdapter(IlluminaAdapterMixin):
    """Adapter for NovaSeq X Plus instruments.
    This class handles the specifics of NovaSeq X Plus parameters and behavior
    """

    name = "novaseqxplus"

    # Example: 20250903_LH00202_0271_A22VTNFLT4
    # YYYYMMDD _ LH<5 digits> _ <4 digits> _ <10 alnum>
    RUNID_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<date>\d{8})_(?P<inst>LH\d{5})_(?P<run>\d{4})_(?P<fcid>[A-Z0-9]{10})$"
    )

    # Not needed, but may be used for validation
    @classmethod
    def matches(cls, run_id):
        return bool(cls.RUNID_RE.match(run_id))

    def _bcl_convert_params(self):
        # NOTE: Example parameter, adjust as needed
        return [
            "--first-tile-only",
            "true",
        ]
