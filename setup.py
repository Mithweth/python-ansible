#!/usr/bin/env python
from setuptools import setup

setup(
    name="python-ansible",
    version="0.0.4",
    description="Ansible executor module for Python",
    author="Jean-Baptiste LANGLOIS",
    author_email="JLANGLOI@bouyguestelecom.fr",
    long_description="Module to easily execute Ansible Task and Playbooks",
    license="GPL",
    test_suite="tests",
    packages=['pyansible'],
)
