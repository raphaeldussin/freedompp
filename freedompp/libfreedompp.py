from freedompp.libcompute import extract_timeserie
from freedompp.libcompute import weighted_by_month_length_average
from freedompp.libcompute import (
    month_by_month_average,
    simple_average,
    extract_month_number,
)
from freedompp.libIO import (
    chkdir,
    close_all_filelikes,
    open_files_from_archives,
    write_ncfile,
)
from freedompp.libstruct import archives_needed, files_needed, infer_freq
from freedompp.libstruct import ppsubdirname, tsfilename, avfilename


def load_timeserie(
    field,
    comesfrom,
    yearstart,
    yearend,
    historydir="./",
    ftype="nc",
    prefix="./",
    in_memory=True,
):
    """load timeserie of a field from netcdf files contained in tar files

    Args:
        field (str): name of the field to load
        comesfrom (str): name of netcdf file containing field without date
                         prefix and filetype suffix (e.g. ocean_annual_z)
        yearstart (int): first year of the time serie
        yearend (int): last year of the time serie
        historydir (str, optional): path to the directory containing "history"
                                    tar files. Defaults to "./".
        ftype (str, optional): file type (e.g. nc or tileX.nc).
                               Defaults to "nc".
        prefix (str, optional): prefix of netcdf files in tar archives.
                                Defaults to "./".
        in_memory (bool, optional): extract data into memory (=no disk IO).
                                    Defaults to True.

    Returns:
        xarray.Dataset: timeserie for field and coordinates
    """

    # infer what tar archives are needed
    used_archives = archives_needed(yearstart, yearend, historydir=historydir)
    # infer which files from these archives are needed
    used_files = files_needed(comesfrom, yearstart, yearend, ftype=ftype, prefix=prefix)
    # load the dataset from multiple files
    ds, fids = open_files_from_archives(used_files, used_archives, in_memory=in_memory)
    # extract the timeserie of the chosen field
    ts = extract_timeserie(ds, field)

    return ts


def write_timeserie(
    field,
    comesfrom,
    yearstart,
    yearend,
    historydir="",
    ppdir="",
    rename_to=None,
    freq=None,
    ftype="nc",
    chunks=None,
    prefix="./",
    in_memory=True,
):
    """write timeserie of a field from netcdf files contained in tar files

    Args:
        field (str): name of the field to load
        comesfrom (str): name of netcdf file containing field without date
                         prefix and filetype suffix (e.g. ocean_annual_z)
        yearstart (int): first year of the time serie
        yearend (int): last year of the time serie
        historydir (str, optional): path to the directory containing "history"
                                    tar files. Defaults to "./".
        ppdir (str, optional): [description]. Defaults to "".
        rename_to ([type], optional): [description]. Defaults to None.
        freq ([type], optional): [description]. Defaults to None.
        ftype (str, optional): file type (e.g. nc or tileX.nc).
                               Defaults to "nc".
        chunks ([type], optional): [description]. Defaults to None.
        prefix (str, optional): prefix of netcdf files in tar archives.
                                Defaults to "./".
        in_memory (bool, optional): extract data into memory (=no disk IO).
                                    Defaults to True.

    """

    # infer what tar archives are needed
    used_archives = archives_needed(yearstart, yearend, historydir=historydir)
    # infer which files from these archives are needed
    used_files = files_needed(comesfrom, yearstart, yearend, ftype=ftype, prefix=prefix)
    # load the dataset from multiple files
    ds, fids = open_files_from_archives(used_files, used_archives, in_memory=in_memory)
    # extract the timeserie of the chosen field
    ts = extract_timeserie(ds, field)
    # define FRE-like pp subdirectory name
    ppsubdir = ppsubdirname(comesfrom, yearstart, yearend, freq=freq, pptype="ts")
    # override directory/file names in pp if override
    if rename_to is not None:
        comesfrom = rename_to
    # define the FRE-like name of the produced file
    fname = tsfilename(field, comesfrom, yearstart, yearend, freq=freq, ftype=ftype)
    # check the output directory exist or create it
    chkdir(ppdir, ppsubdir)
    # write the file
    write_ncfile(ts, f"{ppdir}/{ppsubdir}/{fname}", chunks=chunks)
    # close files
    if in_memory:
        close_all_filelikes(fids)

    return None


def compute_average(
    comesfrom,
    yearstart,
    yearend,
    historydir="",
    avtype="ann",
    freq=None,
    ftype="nc",
    prefix="./",
    avedim="time",
    in_memory=True,
):
    """compute averages of fields from netcdf files contained in tar files

    Args:
        comesfrom (str): name of netcdf file containing field without date
                         prefix and filetype suffix (e.g. ocean_annual_z)
        yearstart (int): first year of the time serie
        yearend (int): last year of the time serie
        historydir (str, optional): path to the directory containing "history"
                                    tar files. Defaults to "./".
        avtype (str, optional): annual or monthly average (ann/mm).
                                Defaults to "ann".
        freq (str, optional): override for file frequency. Defaults to None.
        ftype (str, optional): file type (e.g. nc or tileX.nc).
                               Defaults to "nc".
        prefix (str, optional): prefix of netcdf files in tar archives.
                                Defaults to "./".
        avedim (str, optional): override for name of time dimension.
                                Defaults to "time".
        in_memory (bool, optional): extract data into memory (=no disk IO).
                                    Defaults to True.

    Returns:
        xarray.Dataset: average dataset
    """

    # infer what tar archives are needed
    used_archives = archives_needed(yearstart, yearend, historydir=historydir)
    # infer which files from these archives are needed
    used_files = files_needed(comesfrom, yearstart, yearend, ftype=ftype, prefix=prefix)
    # load the dataset from multiple files
    ds, fids = open_files_from_archives(used_files, used_archives, in_memory=in_memory)

    # figure out frequency of dataset or exit if it cannot
    freq = infer_freq(comesfrom) if freq is None else freq
    if freq is None:
        raise ValueError(
            f"frequency not inferred from {comesfrom} \n"
            " please provide it explicitly as argument"
        )

    if avtype == "ann":
        if freq == "1m":
            ave = weighted_by_month_length_average(ds, avedim=avedim)
        elif freq in ["1y", "1d", "6hr", "3hr"]:
            ave = simple_average(ds, avedim=avedim)
        else:
            raise ValueError(f"unknown frequency {freq}")
    elif avtype == "mm":
        if freq == "1y":
            raise ValueError("Cannot build monthly averages from yearly files")
        elif freq in ["1m", "1d", "6hr", "3hr"]:
            ave = month_by_month_average(ds, avedim=avedim)
        else:
            raise ValueError(f"unknown frequency {freq}")
    else:
        raise ValueError(f"unknown average type {avtype}, available: ann / mm")

    return ave


def write_average(
    comesfrom,
    yearstart,
    yearend,
    historydir="",
    ppdir="",
    avtype="ann",
    rename_to=None,
    freq=None,
    ftype="nc",
    prefix="./",
    avedim="time",
    chunks=None,
    in_memory=True,
):
    """write averages of fields from netcdf files contained in tar files

    Args:
        comesfrom (str): name of netcdf file containing field without date
                         prefix and filetype suffix (e.g. ocean_annual_z)
        yearstart (int): first year of the time serie
        yearend (int): last year of the time serie
        historydir (str, optional): path to the directory containing "history"
                                    tar files. Defaults to "./".
        ppdir (str, optional): path for pp (output) files. Defaults to "".
        avtype (str, optional): annual or monthly average (ann/mm).
                                Defaults to "ann".
        rename_to (str, optional): replace parent name "comesfrom" by this
                                   override in pp. Defaults to None.
        freq (str, optional): override for file frequency. Defaults to None.
        ftype (str, optional): file type (e.g. nc or tileX.nc).
                               Defaults to "nc".
        prefix (str, optional): prefix of netcdf files in tar archives.
                                Defaults to "./".
        avedim (str, optional): override for name of time dimension.
                                Defaults to "time".
        chunks (dict, optional): chunk sizes for output file, e.g. {'time':1}.
                                 Defaults to None, i.e. original chunking
        in_memory (bool, optional): extract data into memory (=no disk IO).
                                    Defaults to True.

    """

    # infer what tar archives are needed
    used_archives = archives_needed(yearstart, yearend, historydir=historydir)
    # infer which files from these archives are needed
    used_files = files_needed(comesfrom, yearstart, yearend, ftype=ftype, prefix=prefix)
    # load the dataset from multiple files
    ds, fids = open_files_from_archives(used_files, used_archives, in_memory=in_memory)

    # figure out frequency of dataset or exit if it cannot
    freq = infer_freq(comesfrom) if freq is None else freq
    if freq is None:
        raise ValueError(
            f"frequency not inferred from {comesfrom} \n"
            " please provide it explicitly as argument"
        )

    if avtype == "ann":
        if freq == "1m":
            ave = weighted_by_month_length_average(ds, avedim=avedim)
        elif freq in ["1y", "1d", "6hr", "3hr"]:
            ave = simple_average(ds, avedim=avedim)
        else:
            raise ValueError(f"unknown frequency {freq}")
    elif avtype == "mm":
        if freq == "1y":
            raise ValueError("Cannot build monthly averages from yearly files")
        elif freq in ["1m", "1d", "6hr", "3hr"]:
            ave = month_by_month_average(ds, avedim=avedim)
        else:
            raise ValueError(f"unknown frequency {freq}")
    else:
        raise ValueError(f"unknown average type {avtype}, available: ann / mm")

    # override directory/file names in pp if override
    if rename_to is not None:
        comesfrom = rename_to
    # define FRE-like pp subdirectory name
    ppsubdir = ppsubdirname(comesfrom, yearstart, yearend, freq=freq, pptype="av")
    # check the output directory exist or create it
    chkdir(ppdir, ppsubdir)

    if avtype == "ann":
        # define the FRE-like name of the produced file
        fname = avfilename(comesfrom, yearstart, yearend, "ann", ftype=ftype)
        # write the file
        write_ncfile(ave, f"{ppdir}/{ppsubdir}/{fname}", chunks=chunks)
    elif avtype == "mm":
        for month in range(1, 12 + 1):  # loop over month
            cmonth = f"{month:02d}"  # in format 01-12
            # pick data for the current month
            ave_mm = extract_month_number(ave, month, avedim=avedim)
            # define the FRE-like name of the produced file
            fname = avfilename(comesfrom, yearstart, yearend, cmonth, ftype=ftype)
            # write the file
            write_ncfile(ave_mm, f"{ppdir}/{ppsubdir}/{fname}", chunks=chunks)
    else:
        raise ValueError(f"unknown average type {avtype}, available: ann / mm")

    # close files
    if in_memory:
        close_all_filelikes(fids)

    return None
