coverage:
	pip install pminifier[test]
	python setup.py nosetests --with-coverage --cover-package=mage -a '!needsfix' --cover-html

lint:
	pip install pminifier[lint]
	pyflakes ./pminifier
	pyflakes ./pminifier
	pep8 ./pminifier

test:
	pip install pminifier[test]
	python setup.py nosetests -a '!needsfix'
