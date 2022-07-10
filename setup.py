from setuptools import setup

setup(
    name="nisin",
    version="0.1.0",
    install_requires=["pyyaml"],
    entry_points={
        "console_scripts": [
            "nisin = nisin.cli:main",
        ],
    },
)
