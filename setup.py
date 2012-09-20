from setuptools import setup, find_packages

setup(
    name="PMinifier",
    version=1,
    packages=find_packages(),
    install_requires=[l.split('#')[0].strip()
                      for l in open('requirements.txt').readlines()
                      if not l.startswith('#')],
    include_package_data=True,
)
