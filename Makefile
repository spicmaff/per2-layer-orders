PYTHON ?= python3

.PHONY: test quick finite export figures site check release-artifacts clean

test quick:
	PYTHONPATH=src $(PYTHON) -m pytest -q
	PYTHONPATH=src $(PYTHON) tools/check_import_boundaries.py

finite:
	PYTHONPATH=src $(PYTHON) -m per2.cli finite-validation --full

export:
	PYTHONPATH=src $(PYTHON) -m per2.cli export-reference --root . --k2-states
	$(PYTHON) tools/make_checksums.py reference

figures:
	PYTHONPATH=src:. $(PYTHON) visualization/static/render_atlas.py
	PYTHONPATH=src:. $(PYTHON) visualization/static/render_row_form.py
	PYTHONPATH=src:. $(PYTHON) visualization/static/render_mmmmvv.py
	PYTHONPATH=src:. $(PYTHON) visualization/static/render_mvmmmm.py
	PYTHONPATH=src:. $(PYTHON) visualization/static/render_map_explorer_mvp.py
	PYTHONPATH=src:. $(PYTHON) visualization/static/render_mmmmvv_explorer_scenes.py

site: figures
	PYTHONPATH=src:. $(PYTHON) tools/build_web_preview.py
	PYTHONPATH=src:. $(PYTHON) tools/check_site_links.py

check: quick figures
	PYTHONPATH=src:. $(PYTHON) tools/check_generated.py

release-artifacts:
	PYTHONPATH=src:. $(PYTHON) tools/build_release_artifacts.py

clean:
	rm -rf build .pytest_cache
