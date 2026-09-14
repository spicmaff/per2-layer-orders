from __future__ import annotations

import argparse
import json
from pathlib import Path

from per2.model import PeriodWord, face_label, parse_face_label
from per2.period import expand_period
from per2.semantics import trace_state, validate_state
from per2.theory import classify_period, mmmmvv_compatibility, mvmmmm_compatibility, mvmmmm_lifo_trace, row_order
from per2.validation import run_full_finite_validation
from per2.export import write_all64_csv, write_k2_exact_states, write_site_classification_json


def _cmd_classify(args: argparse.Namespace) -> int:
    word = PeriodWord.from_code(args.word)
    out = classify_period(word).as_dict()
    out["k"] = args.k
    print(json.dumps(out, indent=2))
    return 0


def _cmd_validate_state(args: argparse.Namespace) -> int:
    word = PeriodWord.from_code(args.word)
    m = expand_period(word, args.k)
    labels = [x.strip() for x in args.order.split(",") if x.strip()]
    state = tuple(parse_face_label(m.n, x) for x in labels)
    trace = trace_state(m, state)
    trace["order_labels"] = [face_label(m.n, fid) for fid in state]
    print(json.dumps(trace, indent=2))
    return 0 if trace["accepted"] else 2


def _cmd_compat(args: argparse.Namespace) -> int:
    if args.family == "MMMMVV":
        out = mmmmvv_compatibility(args.k, args.a, args.b).as_dict()
    else:
        out = mvmmmm_compatibility(args.k, args.a, args.b).as_dict()
        out["trace"] = mvmmmm_lifo_trace(args.k, args.a, args.b).as_dict()
    print(json.dumps(out, indent=2))
    return 0 if out["compatible"] else 3


def _cmd_row(args: argparse.Namespace) -> int:
    cols = row_order(args.k, args.pivot, args.sign)
    row = args.row
    print(json.dumps({"k": args.k, "pivot": args.pivot, "sign": args.sign, "columns": list(cols), "labels": [f"{row}{c}" for c in cols]}, indent=2))
    return 0


def _cmd_finite(args: argparse.Namespace) -> int:
    if not args.full:
        raise SystemExit("use --full: the retained public validation command is intentionally explicit")
    result = run_full_finite_validation()
    print(json.dumps(result, indent=2))
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    root = Path(args.root)
    write_all64_csv(root / "reference/classification/all64.generated.csv")
    write_site_classification_json(root / "web/data/classification-v1.json")
    if args.k2_states:
        write_k2_exact_states(root / "reference/validation/k2_exact_states.json")
    print(json.dumps({"status": "PASS", "root": str(root), "k2_states": bool(args.k2_states)}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="per2", description="PER2 layer-order research artifact CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("classify", help="theorem-derived classification of a six-bit period word")
    c.add_argument("word")
    c.add_argument("--k", type=int, default=2)
    c.set_defaults(func=_cmd_classify)

    v = sub.add_parser("validate-state", help="validate one literal labelled state from theorem-blind semantics")
    v.add_argument("--word", required=True)
    v.add_argument("--k", type=int, required=True)
    v.add_argument("--order", required=True, help="comma-separated labels such as A1,B1,B2,A2")
    v.set_defaults(func=_cmd_validate_state)

    cp = sub.add_parser("compatibility", help="canonical theorem-side pivot compatibility")
    cp.add_argument("family", choices=["MMMMVV", "MVMMMM"])
    cp.add_argument("--k", type=int, required=True)
    cp.add_argument("--a", type=int, required=True)
    cp.add_argument("--b", type=int, required=True)
    cp.set_defaults(func=_cmd_compat)

    r = sub.add_parser("row-order", help="row normal form by physical pivot")
    r.add_argument("--k", type=int, required=True)
    r.add_argument("--pivot", type=int, required=True)
    r.add_argument("--sign", choices=["+", "-"], default="+")
    r.add_argument("--row", choices=["A", "B"], default="A")
    r.set_defaults(func=_cmd_row)

    f = sub.add_parser("finite-validation", help="bounded exact validation; not an all-k proof")
    f.add_argument("--full", action="store_true")
    f.set_defaults(func=_cmd_finite)

    e = sub.add_parser("export-reference", help="generate normalized public exports")
    e.add_argument("--root", default=".")
    e.add_argument("--k2-states", action="store_true")
    e.set_defaults(func=_cmd_export)
    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
