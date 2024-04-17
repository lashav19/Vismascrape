from setuptools import setup, find_packages

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='python-visma',
    version='1.0.2',
    description='Python API to interact with visma as well as getting credentials to use against the Visma REST API',
    packages=find_packages(),
    install_requires=requirements,
)
