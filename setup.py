from setuptools import setup, find_packages

setup(
    name="language-mentor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.4.3",
        "loguru>=0.7.2",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.14.0",
        "pytest-asyncio>=0.21.0",
    ],
) 