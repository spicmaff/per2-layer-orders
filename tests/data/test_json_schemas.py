import json
from pathlib import Path

from jsonschema import Draft202012Validator

from per2.export import write_k2_exact_states, write_site_classification_json
from per2.export.site_data import write_map_explorer_mvp, write_mmmmvv_explorer_scenes

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "reference" / "schemas"


def _validate(instance_path: Path, schema_name: str) -> None:
    instance = json.loads(instance_path.read_text())
    schema = json.loads((SCHEMAS / schema_name).read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def test_public_json_exports_validate_against_committed_schemas(tmp_path: Path):
    classification = tmp_path / "classification-v1.json"
    exact = tmp_path / "k2-exact-states.json"
    explorer = tmp_path / "map-explorer-mvp.json"
    mmmmvv = tmp_path / "mmmmvv-scenes.json"

    write_site_classification_json(classification)
    write_k2_exact_states(exact)
    write_map_explorer_mvp(explorer)
    write_mmmmvv_explorer_scenes(mmmmvv)

    _validate(classification, "classification-v1.schema.json")
    _validate(exact, "k2-exact-states-v1.schema.json")
    _validate(explorer, "map-explorer-mvp-v1.schema.json")
    _validate(mmmmvv, "mmmmvv-explorer-scenes-v1.schema.json")
