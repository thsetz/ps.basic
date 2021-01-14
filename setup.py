"""Setup."""
import os

from setuptools import setup


version = "1.2.6"

INSTALL_REQUIRES = ["setuptools", "docopt", "pygraphviz"]

setup(
    name="ps.basic",
    version=version,
    description="Basic class used in PS environment",
    long_description=open("README.rst").read()
    + "\n"    # noqa: W503
    + open(os.path.join("CHANGES.txt")).read(),  # noqa: W503
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: DevOps",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.9 :: ",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
    ],
    keywords="PS",
    author="Setz",
    author_email="thomas@setz.de",
    url="https://bitbucket.org/drsetz/ps.basic",
    license="GPL",
    packages=["ps.basic"],
    package_dir={"": "src"},
    # include_package_data=True,
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "ps_shell_log=ps.basic.ps_shell_log:main",
        ],
    },
)
