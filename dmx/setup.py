from setuptools import find_packages, setup

from dmx import __version__

try:
    with open("requirements.txt") as f:
        install_requires = [x.strip() for x in f.readlines()]
except OSError:
    install_requires = []


setup(
    name="dmx",
    version=__version__,
    description="Tool for preparing and managing sequencing data before and after demultiplexing.",
    keywords="bioinformatics",
    author="Sara Sjunnebo",
    author_email="sara.sjunnebo@scilifelab.se",
    python_requires=">=3.11.5",
    url="TBD",
    license="MIT",
    packages=find_packages(exclude=["example_sample_sheets", "tests"]),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": ["dmx = dmx.cli:cli"],
        "dmx.subcommands": [
            "prepare = dmx.prepare.cli:prepare",
            "aggregate = dmx.aggregate.cli:aggregate",
        ],
    },
    install_requires=install_requires,
)
