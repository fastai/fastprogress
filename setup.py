import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastprogress",
    version="0.1.5",
    author="Sylvain Gugger",
	license = "Apache License 2.0",
    description="A nested progress with plotting options for fastai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastai/fast_progress",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6"
    ],
)