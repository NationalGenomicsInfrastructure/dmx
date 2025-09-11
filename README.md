# DMX
A helper script for preparing sequening data for demultiplexing.

This repo provides:

* **Adapter layer** – instrument-specific helpers that create and return a
  `DemuxConfig` object (flow-cell ID, BCL-Convert command, lanes, …).
* **Pipeline scaffold** – `demux_ppl()` uses those adapters to _pretend_
  to run BCL-Convert (or skip for ONT PromethION), and other supposed demux steps.
* **Yggdrasil handler** – `dataflow_dmx/yggdrasil_realm/flowcell_handler.py`
  auto-registers itself under the `ygg.handler` entry-point group, so
  Yggdrasil can invoke the pipeline as soon as a new flow-cell is detected.


## 0. Create a conda env

```bash
conda create -n ygg python=3.11
conda activate ygg
```

Use the `env` for either of the next steps (running under Yggdrasil or standalone)


## 1.  Standalone quick-start

```bash
# 1. Clone dmx
git clone https://github.com/NationalGenomicsInfrastructure/dmx.git

# 2. Editable install
pip install -e dmx

# 3. Run the demo CLI on a mock folder
mkdir -p /tmp/mock_fc/20250601_LH00001_0001_ABCDEFGH
dataflow-dmx \
  --run-path /tmp/mock_fc/20250601_LH00001_0001_ABCDEFGH \
  --instrument novaseqxplus
```

## 2. Using the module under Yggdrasil

1. **Install Yggdrasil editable**

```bash
git clone https://github.com/NationalGenomicsInfrastructure/Yggdrasil.git
pip install -e Yggdrasil
```

2. **Install dmx editable**

```bash
git clone https://github.com/NationalGenomicsInfrastructure/dmx.git
pip install -e dmx
```

3. **Launch Yggdrasil**

(Check how to run Yggdrasil in its repo, or ask [@glrs](https://github.com/glrs))

On startup Yggdrasil’s `auto_register_external_handlers()` discovers the
entry-point declared in `pyproject.toml`:

```ini
[project.entry-points."ygg.handler"]
flowcell-dmx = "dataflow_dmx.yggdrasil_realm.flowcell_handler:FlowcellHandler"
```

Log line:
```
✓  registered external handler flowcell-dmx for FLOWCELL_READY
```

When the `SeqDataWatcher` emits a `FLOWCELL_READY` event the handler
executes `production_demux_flow()` asynchronously.
As of writing this, you have to trigger an event manually or fake a real
event for Yggdrasil to capture automatically if you want to play with it.


## 3. Repository overview

```
dataflow_dmx/
├── core/
│   ├── adapters/                # Instrument adapters - all related logic goes here
│   │   ├── base.py
│   │   ├── illumina_mixin.py
│   │   ├── illumina_models.py
│   │   ├── elembio.py
│   │   ├── ont.py
│   │   └── adapter_list.py
│   ├── pipelines/              # Theoretically we can have more demux-related pipelines
│   │   └── demux.py            # Well defined demultiplexing steps go here
│   └── utils/
|       ├── samplesheet_db_manager.py   # Undecided about its use - just mocking right now
│       └── step.py              # (no-op) @step decorator - to be replaced or developed
├── yggdrasil_realm/
│   └── flowcell_handler.py      # auto-registered Ygg handler - Yggdrasil realm interfacing
└── cli.py                       # `dataflow-dmx` entry-point
```

* `@step` is currently a **no-op marker**; later we can swap in status tracking, logging,
retries, etc., without touching pipeline code. It may also be replaced with the likes of Prefect. Still exploring...

* All instrument-specific behaviour lives in `core/adapters/*`.

## 4. Supported Instruments

**TODO**: In the future we should mention which instruments are supported.
Right now I just list the examples I have created, that will probably need some work from production to be called "supported".

| Registry key   | Instrument              |
| ------------   | ----------------------- |
| `miseq`        | Illumina MiSeq          |
| `novaseqxplus` | Illumina NovaSeq XPlus  |
| `nextseq`      | Illumina NextSeq 2000   |
| `aviti`        | ElementBio Aviti        |
| `promethion`   | ONT PromethION          |

**Note:** Additions require only a new `Adapter` subclass and an entry in
`adapter_list.py`.
