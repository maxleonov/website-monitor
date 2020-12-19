import os

import setuptools


readme_path = os.path.join(os.path.dirname(__file__), "README.rst")
with open(readme_path, "r") as fp:
    long_description = fp.read()

setuptools.setup(
    name="website-monitor",
    version="0.0.1",
    author="Maksym Leonov",
    author_email="maks.leonov@gmail.com",
    description="A simple website monitor that saves website availability metrics to Postgres.",
    long_description=long_description,
    url="https://github.com/maxleonov/website-monitor",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
    ],
    python_requires='>=3.7',
)
