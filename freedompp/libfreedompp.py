from freedompp.libcompute import extract_timeserie
from freedompp.libIO import (
    chkdir,
    close_all_filelikes,
    open_files_from_archives,
    write_ncfile,
)
from freedompp.libstruct import archives_needed, files_needed
from freedompp.libstruct import ppsubdirname, tsfilename


def load_timeserie(
    field, comesfrom, yearstart, yearend, historydir="", in_memory=True, ftype="nc",
):

    # infer what tar archives are needed
    used_archives = archives_needed(yearstart, yearend, historydir=historydir)
    # infer which files from these archives are needed
    used_files = files_needed(comesfrom, yearstart, yearend, ftype=ftype)
    # load the dataset from multiple files
    ds, fids = open_files_from_archives(used_files, used_archives, in_memory=in_memory)
    # extract the timeserie of the chosen field
    ts = extract_timeserie(ds, field)

    return ts, fids


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
):

    # load the timeserie
    ts, fids = load_timeserie(
        field,
        comesfrom,
        yearstart,
        yearend,
        historydir=historydir,
        in_memory=in_memory,
        ftype=ftype,
    )
    # define FRE-like pp subdirectory name
    ppsubdir = ppsubdirname(comesfrom, yearstart, yearend, freq=freq, pptype="ts")
    # define the FRE-like name of the produced file
    fname = tsfilename(field, comesfrom, yearstart, yearend, freq=freq, ftype=ftype)
    # check the output directory exist or create it
    chkdir(ppdir, ppsubdir)
    # write the file
    write_ncfile(ts, f"{ppdir}/{ppsubdir}/{fname}")
    # close files
    if in_memory:
        close_all_filelikes(fids)
