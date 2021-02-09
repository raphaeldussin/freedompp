import cftime
import numpy as np
import pandas as pd
import xarray as xr
from calendar import monthrange


mom6like = xr.Dataset(
    data_vars=dict(
        tos=(["time", "yh", "xh"], np.random.rand(2, 180, 360)),
        time_bnds=(
            ["time", "nv"],
            [
                [cftime.DatetimeNoLeap(2007, 1, 1), cftime.DatetimeNoLeap(2007, 1, 31)],
                [cftime.DatetimeNoLeap(2007, 2, 1), cftime.DatetimeNoLeap(2007, 2, 28)],
            ],
        ),
        average_T1=(
            ["time"],
            [cftime.DatetimeNoLeap(2007, 1, 1), cftime.DatetimeNoLeap(2007, 2, 1)],
        ),
        average_T2=(
            ["time"],
            [cftime.DatetimeNoLeap(2007, 1, 31), cftime.DatetimeNoLeap(2007, 2, 28)],
        ),
        average_DT=xr.DataArray(
            np.array([31.0, 28.0], dtype="f8"), dims=("time"), attrs={"units": "days"}
        ),
    ),
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
time = []
average_T1 = []
average_T2 = []
average_DT = []
time_bnds = []
units = "days since 1900-01-01"
for year in range(2001, 2011):
    for month in range(1, 13):
        eom = monthrange(year, month)[-1]
        time.append(
            cftime.date2num(cftime.DatetimeGregorian(year, month, 15, 0, 0, 0), units)
        )
        average_T1.append(
            cftime.date2num(cftime.DatetimeGregorian(year, month, 1, 0, 0, 0), units)
        )
        average_T2.append(
            cftime.date2num(cftime.DatetimeGregorian(year, month, eom, 0, 0, 0), units)
        )
        average_DT.append(eom)
        time_bnds.append(
            [
                cftime.date2num(
                    cftime.DatetimeGregorian(year, month, 1, 0, 0, 0), units
                ),
                cftime.date2num(
                    cftime.DatetimeGregorian(year, month, eom, 0, 0, 0), units
                ),
            ]
        )

ds_1m = xr.Dataset(
    {
        "data": xr.DataArray(np.arange(nmonths), dims=("time")),
        "average_T1": xr.DataArray(average_T1, dims=("time")),
        "average_T2": xr.DataArray(average_T2, dims=("time")),
        "average_DT": xr.DataArray(average_DT, dims=("time")),
        "time_bnds": xr.DataArray(time_bnds, dims=("time", "nv")),
    },
    coords={"time": xr.DataArray(time, dims=("time"))},
)

nyears = 10
time = []
average_T1 = []
average_T2 = []
average_DT = []
time_bnds = []
units = "days since 1900-01-01"
for year in range(2001, 2011):
    time.append(cftime.date2num(cftime.DatetimeNoLeap(year, 6, 30, 0, 0, 0), units))
    average_T1.append(
        cftime.date2num(cftime.DatetimeNoLeap(year, 1, 1, 0, 0, 0), units)
    )
    average_T2.append(
        cftime.date2num(cftime.DatetimeNoLeap(year, 12, 31, 0, 0, 0), units)
    )
    average_DT.append(365)
    time_bnds.append(
        [
            cftime.date2num(cftime.DatetimeNoLeap(year, 1, 1, 0, 0, 0), units),
            cftime.date2num(cftime.DatetimeNoLeap(year, 12, 31, 0, 0, 0), units),
        ]
    )

ds_1y = xr.Dataset(
    {
        "data": xr.DataArray(np.arange(nyears), dims=("time")),
        "average_T1": xr.DataArray(average_T1, dims=("time")),
        "average_T2": xr.DataArray(average_T2, dims=("time")),
        "average_DT": xr.DataArray(average_DT, dims=("time")),
        "time_bnds": xr.DataArray(time_bnds, dims=("time", "nv")),
    },
    coords={"time": xr.DataArray(time, dims=("time"))},
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

    # ave_1d = simple_average(ds_1d)
    # expected = np.arange(ndays).sum() / ndays
    # assert np.allclose(ave_1d["data"], expected)


def test_weighted_by_month_length_average():
    from freedompp.libcompute import weighted_by_month_length_average

    ave = weighted_by_month_length_average(ds_1m)
    expected = (ds_1m["data"] * ds_1m["average_DT"]).sum() / (ds_1m["average_DT"]).sum()
    assert np.allclose(ave["data"].values, expected.values)


# def test_month_by_month_average():
#    from freedompp.libcompute import month_by_month_average
#
#    ave = month_by_month_average(ds_1m)
#    assert len(ave["data"]) == 12


#    ave = month_by_month_average(ds_1d)
#    assert len(ave["data"]) == 12
