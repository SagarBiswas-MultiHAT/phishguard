build:
	python -m build

test:
	pytest --maxfail=1 --disable-warnings -q --cov=todo_app

package:
	python -m build
