from __future__ import absolute_import, division, print_function

import numpy as np
import pytest

from ctd import DataFrame, derive_cnv, lp_filter
from ctd.utilities import Path

data_path = Path(__file__).parent.joinpath("data")


@pytest.fixture
def spiked_ctd():
    yield DataFrame.from_cnv(
        data_path.joinpath("CTD-spiked-unfiltered.cnv.bz2")
    )


@pytest.fixture
def filtered_ctd():
    yield DataFrame.from_cnv(data_path.joinpath("CTD-spiked-filtered.cnv.bz2"))


# Split.
def test_split_return_tuple(spiked_ctd):
    raw = spiked_ctd.split()
    assert isinstance(raw, tuple)


def test_split_cnv(spiked_ctd):
    downcast, upcast = spiked_ctd.split()
    assert downcast.index.size + upcast.index.size == spiked_ctd.index.size


# Despike.
def test_despike(filtered_ctd):
    # Looking at downcast only.
    dirty = filtered_ctd["c0S/m"].split()[0]
    clean = dirty.despike(n1=2, n2=20, block=500)
    spikes = clean.isnull()
    equal = (dirty[~spikes] == clean[~spikes]).all()
    assert spikes.any() and equal


# Filter.
def test_lp_filter(spiked_ctd, filtered_ctd):
    kw = {"sample_rate": 24.0, "time_constant": 0.15}
    expected = filtered_ctd.index.values
    unfiltered = spiked_ctd.index.values
    filtered = lp_filter(unfiltered, **kw)
    # Caveat: Not really a good test...
    np.testing.assert_almost_equal(filtered, expected, decimal=1)


# Pressure check.
def test_press_check(spiked_ctd):
    unchecked = spiked_ctd["t090C"]
    press_checked = unchecked.press_check()
    reversals = press_checked.isnull()
    equal = (unchecked[~reversals] == press_checked[~reversals]).all()
    assert reversals.any() and equal


def test_bindata(filtered_ctd):
    delta = 1.0
    down = filtered_ctd["t090C"].split()[0]
    down = down.bindata(delta=delta)
    assert np.unique(np.diff(down.index.values)) == delta


def test_derive_cnv(spiked_ctd):
    spiked_ctd.lat = spiked_ctd["latitude"].mean()
    spiked_ctd.lon = spiked_ctd["longitude"].mean()
    derived = derive_cnv(spiked_ctd)
    new_cols = set(derived).symmetric_difference(spiked_ctd.columns)
    assert ["CT", "SA", "SP", "SR", "sigma0_CT", "z"] == sorted(new_cols)
