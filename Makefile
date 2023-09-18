style:
	@python -m pip install pre-commit
	@pre-commit run --all-files --show-diff-on-failure

install:
	@pip install -r requirements/requirements_build.txt
	@python -m build
	@pip install dist/*.whl --force-reinstall

version-info:
	@bash -c "date -u +'Build date: %B %d, %Y %H:%M UTC ShaID: <id>' | xargs -I date sed -i 's/_VERSION_INFO = .*/_VERSION_INFO = \"date\"/g' src/ansys/fluent/parametric/__init__.py"
	@bash -c "git --no-pager log -n 1 --format='%h' | xargs -I hash sed -i 's/<id>/hash/g' src/ansys/fluent/parametric/__init__.py"


docker-pull:
	@pip install docker
	@bash .ci/pull_fluent_image.sh

unittest-222:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_tests.txt
	@pytest --fluent-version=22.2

unittest-231:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_tests.txt
	@pytest --fluent-version=23.1

unittest-232:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_tests.txt
	@pytest --fluent-version=23.2

unittest-241:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_tests.txt
	@pytest --fluent-version=24.1

unittest-self-hosted-222:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_tests.txt
	@pytest --fluent-version=22.2 --self-hosted

unittest-self-hosted-231:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_tests.txt
	@pytest --fluent-version=23.1 --self-hosted

unittest-self-hosted-232:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_tests.txt
	@pytest --fluent-version=23.2 --self-hosted

unittest-self-hosted-241:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_tests.txt
	@pytest --fluent-version=24.1 --self-hosted

build-doc:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_doc.txt
	@xvfb-run make -C doc html
	@touch doc/_build/html/.nojekyll
	@echo "$(DOCS_CNAME)" >> doc/_build/html/CNAME
