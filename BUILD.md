## Build and Release Instructions

## TL;DR

Test code:
```
make git-update
make test
```

XXX: version bump + commit

Release:
```
make release
make tag
```

Test uploads:
```
pip install fastprogress
conda install -f fastai fastprogress
```

## Detailed information

The following is needed if the combined release instructions were failing. So that each step can be done separately.

### Bump the version

Edit `setup.py` and change the version number.

### PyPI

To build a PyPI package and release it on [pypi.org/](https://pypi.org/project/fastai/):

1. Build the package (source and wheel)

   ```
   make dist-pypi
   ```

2. Publish:

   ```
   make release-pypi
   ```

   Note: PyPI won't allow re-uploading the same package filename, even if it's a minor fix. If you delete the file from pypi or test.pypi it still won't let you do it. So either a micro-level version needs to be bumped (A.B.C++) or some [post release string added](https://www.python.org/dev/peps/pep-0440/#post-releases) in `setup.py`.

3. Test that the uploaded package is found and gets installed:

   Test the webpage: [https://pypi.org/project/fastai/](https://pypi.org/project/fastai/)

   Test installation:

   ```
   pip install fastprogress
   ```



### Conda

To build a Conda package and release it on [anaconda.org](​https://anaconda.org/​):

1. Build the fastprogress package (include the `pytorch` channel, for `torch/` dependencies, and fastai test channel for `torchvision/fastai`):

   ```
   make dist-conda

   ```

2. Upload

   ```
   make release-conda

   ```

3. Test

   ```
   conda install -f fastai fastprogress
   ```
