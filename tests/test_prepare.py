import unittest

from dmx.prepare.prepare import (
    prepare_flow_cell,
    determine_sequencer,
    get_flow_cell_id,
    get_samplesheet_path,
)


class TestPredemuxMockup(unittest.TestCase):
    def test_prepare_flow_cell(self):
        # result = prepare_flow_cell("20250528_LH00217_0219_A22TT52LT4")
        pass

    def test_determine_sequencer(self):
        got_sequencer = determine_sequencer("20250528_LH00217_0219_A22TT52LT4")
        self.assertEqual(got_sequencer, "novaseqxplus")
        got_sequencer = determine_sequencer("250522_VH00203_513_AAGMCTHM5")
        self.assertEqual(got_sequencer, "nextseq")
        got_sequencer = determine_sequencer("250514_M01548_0635_000000000-LWFFY")
        self.assertEqual(got_sequencer, "miseq")
        got_sequencer = determine_sequencer("20250508_AV242106_A2427687031")
        self.assert_Equal(got_sequencer, "aviti")

    def test_get_flow_cell_id(self):
        got_id = get_flow_cell_id("20250528_LH00217_0219_A22TT52LT4")
        self.assertEqual(got_id, "22TT52LT4")
        got_id = get_flow_cell_id("250522_VH00203_513_AAGMCTHM5")
        self.assertEqual(got_id, "AAGMCTHM5")
        got_sequencer = get_flow_cell_id("250514_M01548_0635_000000000-LWFFY")
        self.assertEqual(got_id, "000000000-LWFFY")
        got_sequencer = determine_sequencer("20250508_AV242106_A2427687031")
        self.assert_Equal(got_sequencer, "A2427687031")

    def test_get_samplesheet_path(self):
        # This function is not implemented in the mockup, so we skip this test
        pass


if __name__ == "__main__":
    unittest.main()
