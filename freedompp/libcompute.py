import xarray as xr


def extract_timeserie(ds, field):
    """extract field from dataset containing several fields,
    basically a wrapper around xarray

    Args:
        ds (xr.core.dataset.Dataset): multiple variable dataset
        field (str): field to extract

    Returns:
        xr.core.dataset.Dataset: dataset containing field only
    """

    if not isinstance(ds, xr.core.dataset.Dataset):
        raise TypeError("ds must be a xarray.Dataset")

    ts = ds[field].to_dataset(name=field)
    return ts


def simple_average(ds, avedim="time"):
    """the most simple average, valid for non-weighted averages such as
    interannual from annual means

    Args:
        ds (xr.core.dataset.Dataset): multiple variable dataset
        avedim (str, optional): name of time dimension. Defaults to "time".

    Returns:
        xr.core.dataset.Dataset: averaged dataset
    """

    if not isinstance(ds, xr.core.dataset.Dataset):
        raise TypeError("ds must be a xarray.Dataset")

    ave = ds.mean(dim=avedim).expand_dims(dim=avedim)
    dates = []
    dates.append(ds[avedim].mean().values)
    ave[avedim] = xr.DataArray(dates, dims=(avedim))
    ave = ave.set_coords([avedim])
    return ave


def weighted_by_month_length_average(ds, avedim="time"):
    """average weighted by the number of days in each month,
    e.g. valid for annual mean from monthly means

    Args:
        ds (xr.core.dataset.Dataset): multiple variable dataset
        avedim (str, optional): name of time dimension. Defaults to "time".

    Returns:
        xr.core.dataset.Dataset: averaged dataset
    """

    tmp = ds.copy()
    problem_children = ["time_bnds", "average_T1", "average_T2", "average_DT"]
    for var in problem_children:
        if var in ds.variables:
            tmp = tmp.drop_vars([var])
    days_in_month = ds[avedim].dt.days_in_month
    ave = (tmp * days_in_month).sum(dim=avedim).expand_dims(
        dim=avedim
    ) / days_in_month.sum()
    # add time variables back
    meantime = ds[avedim].mean().values
    ave[avedim] = xr.DataArray([meantime], dims=(avedim))
    # this does not work yet
    # for var in problem_children:
    #    if var in ds.variables:
    #        ave[var] = ds[var].mean(dim=avedim)
    return ave


def month_by_month_average(ds, avedim="time"):
    """compute interannual averages for each month

    Args:
        ds (xr.core.dataset.Dataset): multiple variable dataset
        avedim (str, optional): name of time dimension. Defaults to "time".

    Returns:
        xr.core.dataset.Dataset: averaged dataset
    """

    monthly_ave = ds.groupby(ds[avedim].dt.month).mean(dim=avedim)
    # replace month by time
    monthly_ave = monthly_ave.rename({"month": avedim})
    dates = []
    for month in range(12):
        dates.append(ds[avedim][month::12].mean().values)
    monthly_ave[avedim] = xr.DataArray(dates, dims=(avedim))

    return monthly_ave


def extract_month_number(ds, month, avedim="time"):
    """pick a month between 0-11 and add time dimension

    Args:
        ds (xr.core.dataset.Dataset): 12 month dataset
        month (int): month (0-11)
        avedim (str, optional): name of time dimension. Defaults to "time".

    Returns:
        ds_mm: 1 month dataset
    """

    ds_mm = ds.isel({avedim: month}).expand_dims(
        dim=avedim
    )  # pick data for the current month

    return ds_mm


# this is where refineDiag should go
