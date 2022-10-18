from distutils.core import setup

from setuptools import find_packages

all_packages = find_packages()

setup(
    name="brokereg",
    packages=all_packages,
    version="0.0.1",
    license="MIT",
    description="S3 schema registry + temporary Kafka broker",
    author="Vladimir Semenov",
    author_email="subatiq@gmail.com",
    url="https://github.com/subatiq/brokereg",
    download_url="https://github.com/subatiq/brokereg/archive/refs/tags/0.0.1.tar.gz",
    keywords=["schema", "registry", "s3", "broker"],
    install_requires=[
        "requests",
        "boto3",
        "python-dotenv",
        "pydantic",
        "confluent-kafka",
        "jsonschema"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
)
