import cftime
import numpy as np
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


def test_extract_timeserie():
    from freedompp.libcompute import extract_timeserie

    ds = extract_timeserie(mom6like, "tos")
    assert isinstance(ds, xr.core.dataset.Dataset)
    assert "tos" in ds.variables
