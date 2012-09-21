from setuptools import setup, find_packages

setup(
    name="PMinifier",
    version=1,
    packages=find_packages(),
    install_requires=['pymongo','pylru','redis'],
    include_package_data=True,
)
