from setuptools import setup, find_packages

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='vismalib',
    version='1.0',
    description='A library to get the visma API',
    packages=find_packages(),
    install_requires=requirements,
)
