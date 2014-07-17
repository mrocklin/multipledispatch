PYTHON ?= python

inplace:
	$(PYTHON) setup.py build_ext --inplace --with-cython

test: inplace
	nosetests -s --with-doctest multipledispatch/
