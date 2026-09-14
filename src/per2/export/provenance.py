from __future__ import annotations


def provenance(role: str, generation_path: str, **scope) -> dict:
    return {
        "epistemic_role": role,
        "generation_path": generation_path,
        **scope,
    }
