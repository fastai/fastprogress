import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fast_progress",
    version="0.0.1",
    author="Sylvain Gugger",
    description="A nested progress with plotting options for fastai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastai/fast_progress",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
)