# Release policy

The first public candidate is `v1.0.0-rc1`. A stable `v1.0.0` should be tagged only after the real GitHub/Pages deployment has been checked and the rights holder has approved the required license scopes.

Before any tag:

- quick tests pass;
- full bounded finite validation passes from a clean checkout;
- reference exports and static figures regenerate without unexplained drift;
- manuscript and supplements build from clean paths;
- public/private boundaries are reviewed;
- `CITATION.cff` contains only real metadata;
- the public Pages routes have been checked in a normal browser;
- release assets are hashed after final bytes are fixed.

Build deterministic candidate assets with:

```bash
make release-artifacts
```

This writes two deterministic ZIP files plus `SHA256SUMS.txt` under `build/release/`:

- a clean public source snapshot;
- a compact research-artifact bundle containing the paper, supplements, reference data, provenance/reproducibility documentation, and the validation record for the separately scoped physical example.

Do not silently replace published release assets. Scientific-data changes require a new version and explicit release notes. DOI metadata must be added only after an archive actually mints it.
