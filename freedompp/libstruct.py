# this module includes functions relative to pp structure and names

import warnings

allowed_1m_tags = ["monthly", "month", "1m"]
allowed_1y_tags = ["annual", "yearly", "1y"]
allowed_1d_tags = ["daily", "day", "1d"]
allowed_6hr_tags = ["4xdaily", "6hr"]
allowed_3hr_tags = ["8xdaily", "3hr"]


def ppsubdirname(comesfrom, yearstart, yearend, freq=None, pptype="av"):
    """construct the name of the pp subdirectory

    Args:
        comesfrom (str): parent dataset
        yearstart (int): first bound of time segment
        yearend (int): second bound of time segment
        freq (str, optional): override frequency of the dataset.
                              Defaults to None.
        pptype (str, optional): type of pp (av/ts). Defaults to "av".

    Returns:
        str: name of constructed pp subdirectory
    """

    if comesfrom in [None, ""]:
        raise ValueError("comesfrom cannot be empty")

    check_bounds(yearstart, yearend)
    segment_len = f"{yearend-yearstart+1}yr"

    if freq is None:
        freq = infer_freq(comesfrom)
    if freq is None:
        raise ValueError(
            "frequency not inferred from name \n"
            " please provide it explicitly as argument"
        )
    cfreq = print_freq(freq)

    if pptype == "av":
        ppdir = f"{comesfrom}/av/{cfreq}_{segment_len}"
    elif pptype == "ts":
        ppdir = f"{comesfrom}/ts/{cfreq}/{segment_len}"
    else:
        raise ValueError("unknown pp type, available are av and ts")

    return ppdir


def avfilename(comesfrom, yearstart, yearend, suffix, ftype="nc"):
    """construct the name of an average pp file

    Args:
        comesfrom (str): parent dataset
        yearstart (int): first bound of time segment
        yearend (int): second bound of time segment
        suffix (str): "ann" for annual, 01-12 for months
        ftype (str, optional): file type (nc or tile[1-6].nc).
                               Defaults to "nc".

    Returns:
        str: name of constructed average file
    """

    if comesfrom in [None, ""]:
        raise ValueError("comesfrom cannot be empty")
    if suffix in [None, ""]:
        raise ValueError("suffix cannot be empty")

    check_bounds(yearstart, yearend)
    cyearstart, cyearend = format_year_bounds(yearstart, yearend, cformat="yyyy")

    filename = f"{comesfrom}.{cyearstart}-{cyearend}.{suffix}.{ftype}"
    return filename


def tsfilename(field, comesfrom, yearstart, yearend, freq=None, ftype="nc"):
    """construct the name of a timeserie pp file

    Args:
        field (str): name of the physical field
        comesfrom (str): parent dataset
        yearstart (int): first bound of time segment
        yearend (int): second bound of time segment
        freq (str, optional): override frequency for dataset.
                              Defaults to None.
        ftype (str, optional): file type (nc or tile[1-6].nc).
                               Defaults to "nc".

    Returns:
        str: name of constructed timeserie file
    """

    if field in [None, ""]:
        raise ValueError("field cannot be empty")
    if comesfrom in [None, ""]:
        raise ValueError("comesfrom cannot be empty")

    check_bounds(yearstart, yearend)
    if freq is None:
        freq = infer_freq(comesfrom)
    if freq is None:
        raise ValueError(
            "frequency not inferred from name \n"
            " please provide it explicitly as argument"
        )

    if freq == "1y":
        cyearstart, cyearend = format_year_bounds(yearstart, yearend, cformat="yyyy")
    elif freq == "1m":
        cyearstart, cyearend = format_year_bounds(yearstart, yearend, cformat="yyyymm")
    elif freq == "1d":
        cyearstart, cyearend = format_year_bounds(
            yearstart, yearend, cformat="yyyymmdd"
        )
    elif freq in ["12hr", "6hr", "3hr", "1hr"]:
        cyearstart, cyearend = format_year_bounds(
            yearstart, yearend, cformat="yyyymmddhh"
        )

    filename = f"{comesfrom}.{cyearstart}-{cyearend}.{field}.{ftype}"
    return filename


def infer_freq(comesfrom):
    """ infer dataset frequency from its name, testing from low to high
    frequency from list of tags. The order of tests matter because of
    sub-daily tags.

    Args:
        comesfrom (str): dataset (e.g. ocean_annual)

    Returns:
        str: inferred frequency or None
    """

    freq = None
    for tag in allowed_1y_tags:
        freq = "1y" if tag in comesfrom else freq
    for tag in allowed_1m_tags:
        freq = "1m" if tag in comesfrom else freq
    for tag in allowed_1d_tags:
        freq = "1d" if tag in comesfrom else freq
    for tag in allowed_6hr_tags:
        freq = "6hr" if tag in comesfrom else freq
    for tag in allowed_3hr_tags:
        freq = "3hr" if tag in comesfrom else freq

    if freq is None:
        warnings.warn(f"could not infer frequency from name {comesfrom}")
    return freq


def print_freq(freq):
    """print frequency for directory tree

    Args:
        freq (str): dataset frequency as internally defined

    Returns:
        str: frequency as defined in directory tree
    """

    if freq == "1y":
        cfreq = "annual"
    elif freq == "1m":
        cfreq = "monthly"
    elif freq == "1d":
        cfreq = "daily"
    elif freq == "6hr":
        cfreq = "6hr"
    elif freq == "3hr":
        cfreq = "3hr"
    else:
        raise ValueError(f"unknown format for frequency {freq}")

    return cfreq


def format_year_bounds(yearstart, yearend, cformat="yyyy"):
    """generate formatted bounds for time segment according to
       required format

    Args:
        yearstart (int): start year of segment
        yearend (int): final year of segment
        cformat (str, optional): desired format (yyyy, yyyymm,
                                                 yyyymmdd, yyyymmddhh).
                                Defaults to "yyyy".

    Raises:
        ValueError: unknown format if format not in list of available formats

    Returns:
        str, str: time bounds
    """

    if cformat == "yyyy":
        cyearstart = f"{yearstart:04d}"
        cyearlast = f"{yearend:04d}"
    elif cformat == "yyyymm":
        cyearstart = f"{yearstart:04d}01"
        cyearlast = f"{yearend:04d}12"
    elif cformat == "yyyymmdd":
        cyearstart = f"{yearstart:04d}0101"
        cyearlast = f"{yearend:04d}1231"
    elif cformat == "yyyymmddhh":
        cyearstart = f"{yearstart:04d}010100"
        cyearlast = f"{yearend:04d}123123"
    else:
        raise ValueError("unknown format for bounds")

    return cyearstart, cyearlast


def check_bounds(yearstart, yearend):
    """check that second bound is not less than first bound

    Args:
        yearstart (int): first bound of segment
        yearend (int): second bound of segment
    """

    if yearend < yearstart:
        raise ValueError("last year cannot be less than first year")

    return None


def archives_needed(yearstart, yearend, historydir=""):
    """create a list of the archive files needed for a segment of years

    Args:
        yearstart (int): start year of time segment
        yearend (int): end year of time segment
        historydir (str, optional): path to history directory,
                                    where .nc.tar live.
                                    Defaults to "".

    Returns:
        list of str: list of archive files
    """

    archives = []
    for year in range(yearstart, yearend + 1):
        archives.append(f"{historydir}/{year:04d}0101.nc.tar")

    return archives


def files_needed(comesfrom, yearstart, yearend, ftype="nc"):
    """create a list of files needed for the creation of dataset

    Args:
        comesfrom (str): parent dataset
        yearstart (int): start year of time segment
        yearend (int): end year of time segment
        ftype (str, optional): file type (nc or tile[1-6].nc).
                               Defaults to "nc".

    Returns:
        list of str: list of files needed inside archives
    """

    files = []
    for year in range(yearstart, yearend + 1):
        files.append(f"./{year:04d}0101.{comesfrom}.{ftype}")

    return files
