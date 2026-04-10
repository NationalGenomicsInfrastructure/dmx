from yggdrasil.flow.model import StepSpec

_PREFIX = "dataflow_demux.yggdrasil_realm.steps"


def demux_pipeline(scenario: dict) -> list[StepSpec]:
    """
    Recipe that carries harvested doc metadata as a structured dict to the steps.
    """
    return [
        StepSpec(
            step_id="validate_runfolder",
            name="Validate Runfolder in HPC",
            fn_ref=f"{_PREFIX}.validate_runfolder",
            params={"scenario": scenario},
        ),
        StepSpec(
            step_id="materialize_config",
            name="Materialize Demux Config",
            fn_ref=f"{_PREFIX}.materialize_extra_config",
            params={"scenario": scenario},
            deps=["validate_runfolder"],
        ),
        StepSpec(
            step_id="generate_samplesheet",
            name="Generate SampleSheet.csv",
            fn_ref=f"{_PREFIX}.generate_samplesheet",
            params={"scenario": scenario},
            deps=["validate_runfolder"],
        ),
        StepSpec(
            step_id="execute_demux",
            name="Simulate Execute Demux (Nextflow)",
            fn_ref=f"{_PREFIX}.execute_demux",
            params={"scenario": scenario},
            deps=["materialize_config", "generate_samplesheet"],
        ),
        StepSpec(
            step_id="collect_results",
            name="Collect Results and Artifacts",
            fn_ref=f"{_PREFIX}.collect_results",
            params={"scenario": scenario},
            deps=["execute_demux"],
        ),
        StepSpec(
            step_id="upload_results",
            name="Upload/Simulate Upload Results",
            fn_ref=f"{_PREFIX}.upload_results",
            params={"scenario": scenario},
            deps=["collect_results"],
        ),
    ]
