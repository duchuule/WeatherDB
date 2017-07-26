from setuptools import setup

setup(
    name='gatekeeeper',
    packages=['gatekeeper'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)