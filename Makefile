# NetBox IPAM Grouping — install helpers
#
# Usage:
#   make install          Install into the active venv (use as netbox user)
#   make install-fix-perms  Install as root then fix permissions
#   make uninstall        Remove the plugin (run migrate zero first)
#   make permissions      Fix permissions on an already-installed plugin
#   make build            Build sdist + wheel for PyPI upload
#   make upload           Upload to PyPI (requires twine)

PYTHON      ?= /opt/netbox/venv/bin/python
PIP         ?= /opt/netbox/venv/bin/pip
MANAGE      ?= /opt/netbox/netbox/manage.py
PLUGIN_DIR  ?= $(shell $(PYTHON) -c "import site; print(site.getsitepackages()[0])")/netbox_ipam_grouping

.PHONY: install install-fix-perms uninstall permissions build upload migrate

install:
	$(PIP) install .

# Run as root — installs then corrects file ownership/permissions so the
# netbox service user can read the installed files.
install-fix-perms:
	$(PIP) install .
	@$(MAKE) permissions

permissions:
	@echo "Fixing permissions on $(PLUGIN_DIR) ..."
	chmod -R a+rX $(PLUGIN_DIR)
	@echo "Done."

migrate:
	$(PYTHON) $(MANAGE) migrate netbox_ipam_grouping

uninstall:
	@echo "Run 'make migrate-zero' first to drop database tables."
	$(PIP) uninstall netbox-ipam-grouping -y

migrate-zero:
	$(PYTHON) $(MANAGE) migrate netbox_ipam_grouping zero

build:
	$(PYTHON) -m build

upload: build
	twine upload dist/*
