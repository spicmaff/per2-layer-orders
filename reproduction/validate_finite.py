#!/usr/bin/env python3
from __future__ import annotations

import json
from per2.validation import run_full_finite_validation

if __name__ == "__main__":
    print(json.dumps(run_full_finite_validation(), indent=2))
