import xarray as xr
import numpy as np


aux_time_vars = ["time_bnds", "average_T1", "average_T2", "average_DT"]


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
    for var in aux_time_vars:
        ts[var] = ds[var].copy()
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
    # overwrite time variables:
    ave = compute_time_vars_ann(ds, ave, avedim=avedim)
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

    # remove aux time variables
    # these dates don't play nice with weighted average
    dsnt = remove_aux_time_vars(ds)
    # do weighted average using length of each time interval
    ave = dsnt.weighted(ds["average_DT"]).mean(dim=avedim)
    # re-introduce a time dimension in the arrays
    ave = ave.expand_dims(dim=avedim)
    # then add time variables back:
    ave = compute_time_vars_ann(ds, ave, avedim=avedim)
    return ave


def month_by_month_average(ds, avedim="time", bndsdim="nv"):
    """compute interannual averages for each month

    Args:
        ds (xr.core.dataset.Dataset): multiple variable dataset
        avedim (str, optional): name of time dimension. Defaults to "time".
        bndsdim (str, optional): name of bounds dimension. Defaults to "nv".

    Returns:
        xr.core.dataset.Dataset: averaged dataset
    """

    # remove aux time variables
    # these dates don't play nice with weighted average
    dsnt = remove_aux_time_vars(ds)
    # decode times into cftime objects inside a cftime dataset
    cftime = xr.decode_cf(ds[avedim].to_dataset(name="cftime"), use_cftime=True)
    # use the cftime to group by month
    monthly_ave = dsnt.groupby(cftime[avedim].dt.month).mean(dim=avedim)
    # replace month by time
    monthly_ave = monthly_ave.rename({"month": avedim})
    # add the time variables
    monthly_ave = compute_time_vars_mm(ds, monthly_ave, avedim=avedim, bndsdim=bndsdim)
    return monthly_ave


def extract_month_number(ave, month, avedim="time"):
    """pick a month between 1-12 and add corresponding time variables

    Args:
        ave (xr.core.dataset.Dataset): 12 month averaged dataset
        month (int): month (1-12)
        avedim (str, optional): name of time dimension. Defaults to "time".

    Returns:
        xr.core.dataset.Dataset: 1 month dataset
    """

    ds_mm = ave.isel({avedim: month - 1}).expand_dims(
        dim=avedim
    )  # pick data for the current month

    return ds_mm


def compute_time_vars_ann(ds_in, ds_out, avedim="time"):
    """compute and append the time variables for an annual mean
    dataset

    Args:
        ds_in (xr.core.dataset.Dataset): input (non-averaged) dataset
        ds_out (xr.core.dataset.Dataset): output (averaged) dataset
        avedim (str, optional): name of time dimension. Defaults to "time".

    Returns:
        xr.core.dataset.Dataset: appended averaged dataset
    """

    # * average_T1 is the first (in chronological order) bound
    # of the interval, hence we take the min value, which correspond
    # to the start of the new total time interval
    average_T1 = ds_in["average_T1"].min(dim=avedim).values
    # * average_T2 is the second (in chronological order) bound
    # of the interval, hence we take the max value, which correspond
    # to the end of the new total time interval
    average_T2 = ds_in["average_T2"].max().values
    # * time is the middle of the interval
    time = 0.5 * (average_T1 + average_T2)
    # * the new average_DT will be the sum of the individual intervals
    average_DT = ds_in["average_DT"].sum(dim=avedim).values
    # * time_bnds is a redundance
    time_bnds = np.array([[average_T1, average_T2]])
    # add the variables as data arrays:
    ds_out[avedim] = xr.DataArray([time], dims=(avedim), attrs=ds_in[avedim].attrs)

    ds_out["time_bnds"] = xr.DataArray(
        time_bnds, dims=ds_in["time_bnds"].dims, attrs=ds_in["time_bnds"].attrs,
    )
    ds_out["average_T1"] = xr.DataArray(
        [average_T1], dims=ds_in["average_T1"].dims, attrs=ds_in["average_T1"].attrs
    )
    ds_out["average_T2"] = xr.DataArray(
        [average_T2], dims=ds_in["average_T2"].dims, attrs=ds_in["average_T2"].attrs
    )
    ds_out["average_DT"] = xr.DataArray(
        [average_DT], dims=ds_in["average_DT"].dims, attrs=ds_in["average_DT"].attrs
    )
    return ds_out


def compute_time_vars_mm(ds_in, ds_out, avedim="time", bndsdim="nv"):
    """compute and append the time varaibles for a monthly mean dataset

    Args:
        ds_in (xr.core.dataset.Dataset): input (non-averaged) dataset
        ds_out (xr.core.dataset.Dataset): output (averaged) dataset
        avedim (str, optional): name of time dimension. Defaults to "time".
        bndsdim (str, optional): name of bounds dimension. Defaults to "nv".

    Returns:
        xr.core.dataset.Dataset: appended averaged dataset
    """

    cftime = xr.decode_cf(ds_in["time"].to_dataset(name="cftime"), use_cftime=True)
    gby = ds_in.groupby(cftime[avedim].dt.month)

    average_T1 = []
    average_T2 = []
    average_DT = []
    time = []

    for month in range(1, 12 + 1):
        indexes = gby.groups[month]
        index_T1 = gby.groups[month][0]
        index_T2 = gby.groups[month][-1]

        # * average_T1 is the first bound (first day) of the given month
        # of the first year
        average_T1.append(
            ds_in["time_bnds"].isel({avedim: index_T1, bndsdim: 0}).values
        )
        # * average_T2 is the second bound (last day) of the given month
        # of the last year
        average_T2.append(
            ds_in["time_bnds"].isel({avedim: index_T2, bndsdim: 1}).values
        )
        # * average_DT is the sum of the individual months
        average_DT.append(
            ds_in["average_DT"].isel({avedim: indexes}).sum(dim=avedim).values
        )
        # * time is the middle of the month in the last year
        time.append(
            ds_in["time_bnds"].isel({avedim: index_T2, bndsdim: 1})
            - 0.5 * ds_in["average_DT"].isel({avedim: index_T2}).values
        )

    # add the variables as data arrays:
    ds_out[avedim] = xr.DataArray(time, dims=(avedim), attrs=ds_in[avedim].attrs)

    ds_out["average_T1"] = xr.DataArray(
        average_T1, dims=ds_in["average_T1"].dims, attrs=ds_in["average_T1"].attrs
    )
    ds_out["average_T2"] = xr.DataArray(
        average_T2, dims=ds_in["average_T2"].dims, attrs=ds_in["average_T2"].attrs
    )
    ds_out["average_DT"] = xr.DataArray(
        average_DT, dims=ds_in["average_DT"].dims, attrs=ds_in["average_DT"].attrs
    )
    return ds_out


def remove_aux_time_vars(ds):
    """remove auxiliary time variables

    Args:
        ds (xr.core.dataset.Dataset): input dataset

    Returns:
        xr.core.dataset.Dataset: dataset without aux time variables
    """

    out = ds.copy()
    for var in aux_time_vars:
        if var in ds.variables:
            out = out.drop_vars([var])
    return out


# this is where refineDiag should go
