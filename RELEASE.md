## Build and Release Instructions

## TL;DR


1. Test code:
   ```
   make git-pull
   make test
   make git-not-dirty || echo "Commit changes before proceeding"
   ```

   The next stage requires a clean tree to start with, so commit any uncommitted code. If you `git stash` make sure to rerun `make test`.

2. Bump and Tag and Commit:

   ```
   make git-not-dirty && make bump && make commit-tag
   ```

   This will do patch-level bump, for major/minor bump targets see below.

3. Release:

   ```
   make release
   ```

4. Test uploads by installing them:

   ```
   make test-install
   ```

5. Update fastai repo

   If this was a bug fix, update `fastai` dependency files: `conda/meta.yaml` and `setup.py` with this release's `fastprogress` version number.



## Detailed information

The following is needed if the combined release instructions were failing. So that each step can be done separately.


### Bump the version

You can either edit `fastprogress/version.py` and change the version number by hand.

Or run one of these `make` targets:

   Target             | Function
   -------------------| --------------------------------------------
   bump-major         | bump major-level unless has .devX, then don't bump, but remove .devX
   bump-minor         | bump minor-level unless has .devX, then don't bump, but remove .devX
   bump-patch         | bump patch-level unless has .devX, then don't bump, but remove .devX
   bump               | alias to bump-patch (as it's used often)
   bump-major-dev     | bump major-level and add .dev0
   bump-minor-dev     | bump minor-level and add .dev0
   bump-patch-dev     | bump patch-level and add .dev0
   bump-dev           | alias to bump-patch-dev (as it's used often)


We use the semver version convention w/ python adjustment to `.devX`, instead of `-devX`:

* release: `major.minor.patch`, 0.1.10
* dev or rc: `major.minor.patch.devX`, 0.1.10.dev0

For fastprogress, due to its simplicity and usage, there is probably no need for intermediary `.devX` stage. So just normal `bump` will do when a new version is released.



### PyPI details

To build a PyPI package and release it on [pypi.org/](https://pypi.org/project/fastprogress/):

1. Build the pip packages (source and wheel)

   ```
   make dist-pypi
   ```

2. Publish:

   ```
   make release-pypi
   ```

   Note: PyPI won't allow re-uploading the same package filename, even if it's a minor fix. If you delete the file from pypi or test.pypi it still won't let you do it. So either a patch-level version needs to be bumped (A.B.C++) or some [post release string added](https://www.python.org/dev/peps/pep-0440/#post-releases) in `version.py`.

3. Test that the uploaded package is found and gets installed:

   Test the webpage so that the description looks correct: [https://pypi.org/project/fastprogress/](https://pypi.org/project/fastprogress/)

   Test installation:

   ```
   pip install fastprogress
   ```



### Conda details

To build a Conda package and release it on [anaconda.org](https://anaconda.org/fastai/fastprogress):

1. Build the fastprogress conda package:

   ```
   make dist-conda

   ```

2. Upload

   ```
   make release-conda

   ```

3. Test that the uploaded package is found and gets installed:

   Test the webpage so that the description looks correct: [https://pypi.org/project/fastprogress/](https://pypi.org/project/fastprogress/)

   Test installation:

   ```
   conda install -c fastai fastprogress
   ```

### Others

`make clean` removes any intermediary build artifacts.

`make` will show all possible targets with a short description of what they do.
