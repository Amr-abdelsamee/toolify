from setuptools import setup, find_packages

setup(
    name="toolify",
    version="0.2.0",
    description="A library that provide helper function and tools.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Amr Abdelsamea",
    author_email="amr.abdelsamee33@gmail.com",
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=[
        "python-bidi==0.6.6",
        "arabic_reshaper==3.0.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["tools", "arabic", "bidi", "plotting", "logging", "cuda"],
    license="MIT",
    include_package_data=True,
    package_data={
        "toolify": ["data/*.txt", "*.json"],
    },
)