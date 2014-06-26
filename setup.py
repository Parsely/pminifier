import sys

from setuptools import setup, find_packages

install_requires = ['pymongo','pylru','redis']
tests_require = ['mock', 'coverage', 'testinstances', 'mock']
lint_requires = ['pep8', 'pyflakes']
setup_requires = []

if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')
    setup_requires.append('nose-testconfig')

setup(
    name="PMinifier",
    version=1,
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    include_package_data=True,
    extras_require={
        'test': tests_require,
        'all': install_requires + tests_require,
        'lint': lint_requires,
    },
)
