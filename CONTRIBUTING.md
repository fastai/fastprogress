# How to contribute to fastai

First, thanks a lot for wanting to help!

## Did you find a bug?

* Ensure the bug was not already reported by searching on GitHub under [Issues](https://github.com/fastai/fastai_v1/issues).

* If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/fastai/fastai_v1/issues/new). Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.

* Be sure to add the complete error messages.

#### Did you write a patch that fixes a bug?

* Open a new GitHub pull request with the patch.

* Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.

* Before submitting, please read the [doc on code style](https://github.com/fastai/fastai_v1/blob/master/docs/style.md) and [the one on abbreviations](https://github.com/fastai/fastai_v1/blob/master/docs/abbr.md) and clean-up your code accordingly.

## Do you intend to add a new feature or change an existing one?

* You can suggest your change on the [fastai forum](http://forums.fast.ai/) to see if others are interested or want to help.

* PRs are welcome with a complete description of the new feature and an example of how it's use. Be sure to document your code and read the [doc on code style](https://github.com/fastai/fastai_v1/blob/master/docs/style.md) and [the one on abbreviations](https://github.com/fastai/fastai_v1/blob/master/docs/abbr.md).

## Do you have questions about the source code?

* Please ask it on the [fastai forum](http://forums.fast.ai/) (after searching someone didn't ask the same one before with a quick search).

## Do you want to contribute to the documentation?

* Please read [Contributing to the documentation]() *link to be added*

## Git: a mandatory notebook strip out

Currently we only store `source` code cells under git. If you would like to commit or submit a PR, you need to confirm to that standard.

This is done automatically during `diff`/`commit` git operations, but you need to configure your local repository once to activate that instrumentation.

Therefore, your developing process will always start with:

    git clone https://github.com/fastai/fastai_v1
    cd fastai_v1
    git config --local include.path '../.gitconfig'

The last command tells git to invoke configuration stored in `fastai_v1/.gitconfig`, so your `git diff` and `git commit` invocations for this particular repository will now go via 'tools/fastai-nbstripout' which will do all the work for you.

If you skip this configuration your commit/PR involving notebooks will not be accepted, since it'll carry in it many JSON bits which we don't want in the git repository. Those unwanted bits create collisions and lead to unnecessarily complicated and time wasting merge activities. So please do not skip this step.

Note: we can't make this happen automatically, since git will ignore a repository-stored `.gitconfig` for security reasons, unless a user will tell git to use it (and thus trust it).

If you'd like to check whether you already trusted git with using `fastai_v1/.gitconfig` please look inside `fastai_v1/.git/config`, which should have this entry:


```
[include]
        path = ../.gitconfig

```

