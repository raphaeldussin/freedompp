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


def open_files_from_archives(
    files, archives, in_memory=True, recombine=False, nsplit=0, chunks=None, tmpdir=None
):
    """build a dataset from list of files and their corresponding archives

    Args:
        files (list): list of files to open
        archives (list): list of archives containing these files
        in_memory (bool, optional): Extract files into memory not disk.
                                    Defaults to True.
        tmpdir (str, optional): Where to extract data files.
                                Defaults to None.

    Returns:
        xr.core.dataset.Dataset: produced dataset
        list of str: open files
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

    if not in_memory and tmpdir is None:
        raise ValueError(
            "when not uncompressing files in memory, `tmpdir` must be set explicitly"
        )

    kwargs = dict(combine="by_coords", decode_times=False)
    if recombine:
        kwargs.update({"data_vars": "minimal"})
        if chunks is None:
            raise ValueError(
                "chunks must be explicitly passed when using recombine=True"
            )
        else:
            kwargs.update({"chunks": chunks})

    open_files = []
    for f, a in zip(files, archives):
        if not in_memory:
            htar = tarfile.open(a)
        if recombine:
            for kn in range(nsplit):
                fnnnn = f"{f}.{kn:04d}"
                if in_memory:
                    open_files.append(filelike(a, fnnnn))
                else:
                    if not os.path.exists(f"{tmpdir}/{fnnnn}"):
                        htar.extract(fnnnn, tmpdir)
                    open_files.append(f"{tmpdir}/{fnnnn}")
        else:
            if in_memory:
                open_files.append(filelike(a, f))
            else:
                if not os.path.exists(f"{tmpdir}/{f}"):
                    htar.extract(f, tmpdir)
                open_files.append(f"{tmpdir}/{f}")

        if not in_memory:
            htar.close()
    ds = xr.open_mfdataset(open_files, **kwargs)

    return ds, open_files


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

    encoding = {}
    for var in ds:
        if chunks is not None:
            chunksizes = ()
            for dim in ds[var].dims:
                if dim in chunks:
                    chunksizes = chunksizes + (chunks[dim],)
                else:
                    chunksizes = chunksizes + (len(ds[dim]),)
            encoding.update({var: {"_FillValue": 1e20, "chunksizes": chunksizes}})
        else:
            encoding.update({var: {"_FillValue": 1e20}})

    ds.to_netcdf(
        filename,
        unlimited_dims=[avedim],
        encoding=encoding,
        engine="netcdf4",
        format="NETCDF4",
    )

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
