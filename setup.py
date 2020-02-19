"""Karel the Robot (now in Python)

See the README in linked GitHub repository for more details.
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="karel_robot",
    version="0.0.1",
    author="Ondřej Šebek",
    author_email="xsebek@fi.muni.cz",
    description="Karel the Robot simple library and interactive executable",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xsebek/karel",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['karel=karel_robot.run.karel_run:interactive']
    }
)
