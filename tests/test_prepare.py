import unittest

from dmx.dmx import (
    get_run_object,
    # prepare_flow_cell,
)
from dmx.RunClasses import (
    GenericRun,
    IlluminaRun,
    MiSeqRun,
    NextSeqRun,
    AvitiRun,
    NovaSeqXPlusRun,
)


class TestDmx(unittest.TestCase):
    def test_prepare_flow_cell(self):
        # result = prepare_flow_cell("20250528_LH00217_0219_A22TT52LT4")
        pass

    def test_get_run_object(self):
        got_obj_novaseq = get_run_object("20250528_LH00217_0219_A22TT52LT4")
        self.assertIsInstance(got_obj_novaseq, NovaSeqXPlusRun)
        got_obj_nextseq = get_run_object("250522_VH00203_513_AAGMCTHM5")
        self.assertIsInstance(got_obj_nextseq, NextSeqRun)
        got_obj_miseq = get_run_object("250514_M01548_0635_000000000-LWFFY")
        self.assertIsInstance(got_obj_miseq, MiSeqRun)
        got_obj_aviti = get_run_object("20250508_AV242106_A2427687031")
        self.assertIsInstance(got_obj_aviti, AvitiRun)


class TestRunClasses(unittest.TestCase):
    def test_generic_run(self):
        run = GenericRun("20250528_LH00217_0219_A22TT52LT4")
        self.assertEqual(run.flowcell_id, "A22TT52LT4")
        self.assertEqual(
            run.path_to_samplesheets,
            "/Users/sara.sjunnebo/code/scratch/pre_demux_testing/example_sample_sheets",
        )

    def test_illumina_run(self):
        run = IlluminaRun("250522_VH00203_513_AAGMCTHM5")
        self.assertEqual(
            run.sample_sheet,
            "/Users/sara.sjunnebo/code/scratch/pre_demux_testing/example_sample_sheets/AAGMCTHM5.csv",
        )

    def test_miseq_run(self):
        run = MiSeqRun("250514_M01548_0635_000000000-LWFFY")
        self.assertEqual(run.flowcell_id, "000000000-LWFFY")
        self.assertEqual(
            run.sample_sheet,
            "/Users/sara.sjunnebo/code/scratch/pre_demux_testing/example_sample_sheets/SampleSheet.csv",
        )

    def test_nextseq_run(self):
        run = NextSeqRun("250522_VH00203_513_AAGMCTHM5")
        self.assertEqual(run.flowcell_id, "AAGMCTHM5")
        self.assertEqual(
            run.sample_sheet,
            "/Users/sara.sjunnebo/code/scratch/pre_demux_testing/example_sample_sheets/AAGMCTHM5.csv",
        )

    def test_novaseqxplus_run(self):
        run = NovaSeqXPlusRun("20250528_LH00217_0219_A22TT52LT4")
        self.assertEqual(run.flowcell_id, "22TT52LT4")
        self.assertEqual(
            run.sample_sheet,
            "/Users/sara.sjunnebo/code/scratch/pre_demux_testing/example_sample_sheets/22TT52LT4.csv",
        )

    def test_aviti_run(self):
        run = AvitiRun("20250508_AV242106_A2427687031")
        self.assertEqual(run.flowcell_id, "A2427687031")
        self.assertEqual(
            run.sample_sheet,
            "/Users/sara.sjunnebo/code/scratch/pre_demux_testing/example_sample_sheets/A2427687031.csv",
        )


if __name__ == "__main__":
    unittest.main()
