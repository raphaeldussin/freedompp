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
    historydir="",
    in_memory=True,
    ftype="nc",
    prefix="./",
):

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
    ppdir="",
    historydir="",
    freq=None,
    in_memory=True,
    ftype="nc",
    chunks=None,
):

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
    freq=None,
    in_memory=True,
    ftype="nc",
    prefix="./",
    avtype="ann",
    avedim="time",
):

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
    freq=None,
    in_memory=True,
    ftype="nc",
    prefix="./",
    avtype="ann",
    avedim="time",
    chunks=None,
):

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
        for kt in range(12):  # loop over month
            month = f"{kt+1:02d}"  # in format 01-12
            # pick data for the current month
            ave_mm = extract_month_number(ave, kt, avedim=avedim)
            # define the FRE-like name of the produced file
            fname = avfilename(comesfrom, yearstart, yearend, month, ftype=ftype)
            # write the file
            write_ncfile(ave_mm, f"{ppdir}/{ppsubdir}/{fname}", chunks=chunks)
    else:
        raise ValueError(f"unknown average type {avtype}, available: ann / mm")

    # close files
    if in_memory:
        close_all_filelikes(fids)

    return None
