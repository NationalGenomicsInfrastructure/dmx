import os


class GenericRun:
    def __init__(self, run_id):
        self.run_id = run_id
        self.set_flowcell_id()
        self.path_to_samplesheets = "/Users/sara.sjunnebo/code/scratch/pre_demux_testing/example_sample_sheets"  # TODO: change this to a config file

    def set_flowcell_id(self):
        self.flowcell_id = self.run_id.split("_")[-1]


class IlluminaRun(GenericRun):
    def __init__(self, run_id):
        super().__init__(run_id)
        self.sample_sheet = os.path.join(
            self.path_to_samplesheets, f"{self.flowcell_id}.csv"
        )

    def __repr__(self):
        return f"IlluminaRun(name={self.run_id})"


class MiSeqRun(IlluminaRun):
    def __init__(self, run_id):
        super().__init__(run_id)
        self.sample_sheet = os.path.join(
            self.path_to_samplesheets, "SampleSheet.csv"
        )  # TODO: adapt to look in the right place

    def __repr__(self):
        return f"MiSeqRun(name={self.run_id})"


class NextSeqRun(IlluminaRun):
    def __init__(self, run_id):
        super().__init__(run_id)

    def __repr__(self):
        return f"NextSeqRun(name={self.run_id})"


class NovaSeqXPlusRun(IlluminaRun):
    def __init__(self, run_id):
        super().__init__(run_id)

    def __repr__(self):
        return f"NovaSeqXPlusRun(name={self.run_id})"

    def set_flowcell_id(self):
        self.flowcell_id = self.run_id.split("_")[-1][-9:]


class AvitiRun(GenericRun):
    def __init__(self, run_id):
        super().__init__(run_id)
        self.sample_sheet = os.path.join(
            self.path_to_samplesheets, self.flowcell_id + ".csv"
        )  # TODO: change name here or in lims epp

    def __repr__(self):
        return f"AvitiRun(name={self.run_id})"
