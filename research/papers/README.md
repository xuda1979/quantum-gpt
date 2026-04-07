# Research Papers

This subtree stores self-contained research tracks.

Each paper lives in its own subfolder:

- `paper.md`: the research note / draft paper
- `code/`: the code, configs, or launch artifacts tied to that paper

Plugin-capable methods expose:

- `code/plugin.py`

Those plugins can be enabled from training entrypoints with:

- `--research-methods <paper_id> [<paper_id> ...]`

Current goals for this subtree:

- keep research code removable
- keep papers close to implementation
- make leadership-facing innovation claims traceable to concrete code
