import cftime
import numpy as np
import pandas as pd
import xarray as xr

mom6like = xr.Dataset(
    data_vars=dict(tos=(["time", "yh", "xh"], np.random.rand(2, 180, 360)),),
    coords=dict(
        xq=xr.DataArray(
            np.arange(-300, 60 + 1),
            dims=["xq"],
            attrs={
                "long_name": "q point nominal longitude",
                "units": "degrees_east",
                "cartesian_axis": "X",
            },
        ),
        yq=xr.DataArray(
            np.arange(-90, 90 + 1),
            dims=["yq"],
            attrs={
                "long_name": "q point nominal latitude",
                "units": "degrees_north",
                "cartesian_axis": "Y",
            },
        ),
        xh=xr.DataArray(
            0.5 + np.arange(-300, 60),
            dims=["xh"],
            attrs={
                "long_name": "h point nominal longitude",
                "units": "degrees_east",
                "cartesian_axis": "X",
            },
        ),
        yh=xr.DataArray(
            0.5 + np.arange(-90, 90),
            dims=["yh"],
            attrs={
                "long_name": "h point nominal latitude",
                "units": "degrees_north",
                "cartesian_axis": "Y",
            },
        ),
        time=xr.DataArray(
            [
                cftime.DatetimeNoLeap(2007, 1, 16, 12, 0, 0, 0),
                cftime.DatetimeNoLeap(2007, 2, 15, 0, 0, 0, 0),
            ],
            dims=["time"],
        ),
        reference_time=cftime.DatetimeNoLeap(1901, 1, 1, 0, 0, 0, 0),
    ),
    attrs=dict(description="Synthetic MOM6 data"),
)

ndays = 3652
ds_1d = xr.Dataset(
    {"data": xr.DataArray(np.arange(ndays), dims=("time"))},
    coords={"time": pd.date_range("1900-01-01", freq="1d", periods=ndays)},
)

nmonths = 10 * 12
ds_1m = xr.Dataset(
    {"data": xr.DataArray(np.arange(nmonths), dims=("time"))},
    coords={"time": pd.date_range("1900-01-01", freq="1m", periods=nmonths)},
)

nyears = 10
ds_1y = xr.Dataset(
    {"data": xr.DataArray(np.arange(nyears), dims=("time"))},
    coords={"time": pd.date_range("1900-01-01", freq="1y", periods=nyears)},
)


def test_extract_timeserie():
    from freedompp.libcompute import extract_timeserie

    ds = extract_timeserie(mom6like, "tos")
    assert isinstance(ds, xr.core.dataset.Dataset)
    assert "tos" in ds.variables


def test_simple_average():
    from freedompp.libcompute import simple_average

    ave_1y = simple_average(ds_1y)
    expected = np.arange(nyears).sum() / nyears
    assert np.allclose(ave_1y["data"], expected)

    ave_1d = simple_average(ds_1d)
    expected = np.arange(ndays).sum() / ndays
    assert np.allclose(ave_1d["data"], expected)


def test_weighted_by_month_length_average():
    from freedompp.libcompute import weighted_by_month_length_average

    ave = weighted_by_month_length_average(ds_1m)
    expected = (ds_1m["data"] * ds_1m["time"].dt.days_in_month).sum() / (
        ds_1m["time"].dt.days_in_month
    ).sum()
    assert np.allclose(ave["data"].values, expected.values)


def test_month_by_month_average():
    from freedompp.libcompute import month_by_month_average

    ave = month_by_month_average(ds_1m)
    assert len(ave["data"]) == 12
    ave = month_by_month_average(ds_1d)
    assert len(ave["data"]) == 12
