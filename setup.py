from setuptools import setup, find_packages

setup(
    name='Octopus API',
    version='1.0',
    description='API for Integrating Ministerio de Hacienda DTEs',
    author='Marcelo Cerritos',
    packages=find_packages(exclude=['tests']),
)
