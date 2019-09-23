#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import fastprogress

def test_basic():
    assert fastprogress.__version__

def test_empty():
    with pytest.warns(UserWarning, match='Your generator is empty.'):
        assert list(fastprogress.progress_bar([])) == []
