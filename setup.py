from setuptools import find_packages, setup

with open("README.md", encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(name='MEDprofiles',
      version='0.1.0',
      description='Python module for treatment and visualization of medical data.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Sarah Denis',
      author_email='dens1704@usherbrooke.ca',
      url='https://github.com/MEDomics-UdeS/MEDprofiles',
      packages=find_packages(exclude=['docs']),
      install_requires=requirements
      )
