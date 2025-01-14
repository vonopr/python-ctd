release:
	rm -rf dist/
	python setup.py sdist bdist_wheel
	twine upload dist/*

isort:
	isort --remove-import . --apply --use-parentheses --trailing-comma

format:
	black --line-length 79 .

style: isort format

docs:
	cp notebooks/{quick_intro.ipynb,searchfor.ipynb} docs/source/
	pushd docs && make clean html linkcheck && popd

lint:
	pytest --flake8 -m flake8

test:
	pytest -n 2 -rxs --cov=ctd tests

check: style docs lint test
	echo "All checks complete!"
