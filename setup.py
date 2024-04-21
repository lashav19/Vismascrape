from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='python-visma',
    version='1.0.3',
    description='Python API to interact with visma as well as getting credentials to use against the Visma REST API',
    long_description= long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
)
