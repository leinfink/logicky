import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logicky",  # Replace with your own username
    version="0.0.1",
    author="Henrik Hörmann",
    author_email="henrikhoermann@googlemail.com",
    description=("A small tool to evaluate"
                 "and prove arguments in formal logic."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tranfunzel/logicky",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
