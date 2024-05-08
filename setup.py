from setuptools import setup, find_packages
from pathlib import Path


with open("README.md") as f:
    long_description = f.read()

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='python-visma',
    version='2.0.0',
    description='Python API to interact with visma as well as getting credentials to use against the Visma REST API',
    long_description= long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
)
