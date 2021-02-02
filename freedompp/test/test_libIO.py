import os
import tarfile

import numpy as np
import xarray as xr

testds = xr.DataArray(np.arange(10), dims=("x")).to_dataset(name="x")
testds2 = xr.DataArray(10 + np.arange(10), dims=("x")).to_dataset(name="x")


def test_filelike(tmpdir):
    from freedompp.libIO import filelike, close_all_filelikes

    # first create tar file. This is done in a rather ugly fashion
    # but the nc file needs to be created in the current directory so
    # its name is encoded correctly in the tar file, i.e. ./dummy.00000101.nc
    ncout = "dummy.00000101.nc"
    testds.to_netcdf(f"{ncout}")
    with tarfile.open(f"{tmpdir}/00000101.nc.tar", "w:") as tar_handle:
        tar_handle.add(os.path.join("./", ncout))

    if os.path.exists(os.path.join("./", ncout)):
        os.remove(os.path.join("./", ncout))

    fid = filelike(f"{tmpdir}/00000101.nc.tar", "./dummy.00000101.nc")
    assert isinstance(fid, tarfile.ExFileObject)

    ds = xr.open_dataset(fid)
    assert isinstance(ds, xr.core.dataset.Dataset)
    assert np.allclose(ds["x"], np.arange(10))

    close_all_filelikes(fid)


def test_open_files_from_archives(tmpdir):
    from freedompp.libIO import open_files_from_archives, close_all_filelikes

    ncout = "dummy.00000101.nc"
    testds.to_netcdf(f"{ncout}")
    with tarfile.open(f"{tmpdir}/00000101.nc.tar", "w:") as tar_handle:
        tar_handle.add(os.path.join("./", ncout))

    ncout2 = "dummy.00010101.nc"
    testds2.to_netcdf(f"{ncout2}")
    with tarfile.open(f"{tmpdir}/00010101.nc.tar", "w:") as tar_handle:
        tar_handle.add(os.path.join("./", ncout2))

    if os.path.exists(os.path.join("./", ncout)):
        os.remove(os.path.join("./", ncout))
    if os.path.exists(os.path.join("./", ncout2)):
        os.remove(os.path.join("./", ncout2))

    ds, fids = open_files_from_archives(
        ["./dummy.00000101.nc", "./dummy.00010101.nc"],
        [f"{tmpdir}/00000101.nc.tar", f"{tmpdir}/00010101.nc.tar"],
    )

    assert isinstance(ds, xr.core.dataset.Dataset)
    assert len(ds["x"].values) == 20

    close_all_filelikes(fids)


def test_chkdir(tmpdir):
    from freedompp.libIO import chkdir

    chkdir(tmpdir, "test/test/test")
    assert os.path.exists(os.path.join(tmpdir, "test/test/test"))
