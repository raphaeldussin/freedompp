import os
import subprocess
import tarfile

import xarray as xr


def filelike(archive, filename):
    """create an in-memory copy of a file extracted from archive

    Args:
        archive (str): name of the tar archive used containing file
        filename (str): name of the file to extract virtually

    Returns:
        path to file-like object
    """

    tar = tarfile.open(name=archive, mode="r:")
    flike = tar.extractfile(filename)
    return flike


def open_files_from_archives(files, archives, in_memory=True):
    """build a dataset from list of files and their corresponding archives

    Args:
        files (list): list of files to open
        archives (list): list of archives containing these files
        in_memory (bool, optional): Extract files into memory not disk.
                                    Defaults to True.

    Returns:
        xr.core.dataset.Dataset: produced dataset
    """

    if not isinstance(files, list):
        raise TypeError("files must be a list")
    if not isinstance(files, list):
        raise TypeError("archives must be a list")
    if len(files) != len(archives):
        raise ValueError(
            "files and archives must have \
                          the same number of elements"
        )

    if in_memory:
        flikes = []
        for f, a in zip(files, archives):
            flikes.append(filelike(a, f))
        ds = xr.open_mfdataset(flikes, decode_times=False)
    else:
        raise NotImplementedError("")

    return ds, flikes


def close_all_filelikes(flikes):
    """close all passed file-like objects

    Args:
        flikes (list): list of objects to close

    """

    for f in flikes:
        f.close()

    return None


def write_ncfile(ds, filename, chunks=None, avedim="time"):
    """write dataset to netcdf file

    Args:
        ds (xarray.core.dataset.Dataset): dataset to write
        filename (str): name of the output file
        chunks (dict, optional): dictionary containing chunk sizes,
                                 e.g. {'time': 1, 'z': 35}.
                                 Defaults to None.
        avedim (str, optional): Name of time dimension. Defaults to "time".
    """
    # fix chunksize
    if chunks is not None:
        ds = ds.chunk(chunks)

    ds.to_netcdf(filename, unlimited_dims=[avedim])

    return None


def chkdir(ppdir, ppsubdir):
    """create directory if it does not exists

    Args:
        ppdir (str): pp directory (e.g. CM4_piControl/ncrc4.intel18/pp)
        ppsubdir (str): pp subdirectory (e.g. ocean_annual/ts/annual/10yr)

    """

    if not os.path.exists(ppdir):
        raise IOError(f"{ppdir} does not exists")

    if not os.path.exists(f"{ppdir}/{ppsubdir}"):
        _ = subprocess.check_call(f"mkdir -p {ppdir}/{ppsubdir}", shell=True)

    return None
