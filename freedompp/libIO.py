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
    files, archives, in_memory=True, recombine=False, nsplit=0, chunks=None
):
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

    kwargs = dict(combine="by_coords", decode_times=False)
    if recombine:
        kwargs.update({"data_vars": "minimal"})
        if chunks is None:
            raise ValueError(
                "chunks must be explicitly passed when using recombine=True"
            )
        else:
            kwargs.update({"chunks": chunks})

    if in_memory:
        flikes = []
        for f, a in zip(files, archives):
            if recombine:
                for kn in range(nsplit):
                    fnnnn = f"{f}.{kn:04d}"
                    flikes.append(filelike(a, fnnnn))
            else:
                flikes.append(filelike(a, f))
        ds = xr.open_mfdataset(flikes, **kwargs)
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


def var_files_from_diagtable(diagtable):
    """ Read the diag_table and return dictionary of outputted variables
    and the file root (e.g. ocean_month_z) in which they are written in

    Args:
        diagtable (str): path to the diag_table to use

    Returns:
        list of dict: a list of {variable:file} e.g. {"thetao": "ocean_daily"}

    """
    # open file and read all lines
    fid = open(diagtable, "r")
    all_lines = fid.readlines()

    # clean up comments and empty lines
    processed_lines = []
    for line in all_lines:
        # find and remove comment
        indexcomment = line.find("#")
        line_nocomment = line[:indexcomment] if indexcomment >= 0 else line
        # remove empty lines
        if line_nocomment.strip() != "":
            processed_lines.append(line_nocomment)

    assert len(processed_lines) > 1

    # build a list of key:value = variable:file
    variables_in_files = []
    # clean up punctuation and split line into words
    for line in processed_lines:
        words = line.replace('"', "").replace(",", " ").replace("'", "").split()

        # luckily lines defining variables have 8 words
        # 3rd word is netcdf variable and 4th is the netcdf file type
        if len(words) == 8:
            variables_in_files.append({words[2]: words[3]})

    return variables_in_files


def extract_files_diagtable(diagtable):
    """ return all files found in diag_table

    Args:
        diagtable (str): path to the diag_table to use

    Returns:
        list: all files defined in diag_table

    """

    variables_in_files = var_files_from_diagtable(diagtable)

    all_occurences = []
    for k in variables_in_files:
        all_occurences.append(list(k.values())[0])

    files = list(set(all_occurences))
    return files
