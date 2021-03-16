import pathlib

import setuptools

HERE = pathlib.Path(__file__).parent
AUTHORS = (HERE / "AUTHORS").read_text()
README = (HERE / "README.md").read_text()


setuptools.setup(
    name="respir-os",
    version="1.0.0",
    author=", ".join(AUTHORS.splitlines()),
    license="LGPL-3",
    description="""
    Open design and implementation of a low-cost ventilator for COVID-19
    patients.
    """,
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Intended Audience :: Healthcare Industry",
        "Natural Language :: Spanish",
        "Operating System :: Unix",
    ],
    packages=["controls", "gui", "api"],
    python_requires=">=3.8.6",
    install_requires=[
        "flask",
        "flask-socketio",
        "pigpio",
        "pysimplegui",
        "matplotlib",
        "numpy",
        "gevent",
        "pyzmq",
    ],
    scripts=["scripts/run", "scripts/run-dev", "scripts/run-test"],
)
