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


def compute_average(ds, avedim="time"):
    """[summary]

    Args:
        ds (xr.core.dataset.Dataset): multiple variable dataset
        avedim (str, optional): [description]. Defaults to "time".

    Returns:
        [type]: [description]
    """

    if not isinstance(ds, xr.core.dataset.Dataset):
        raise TypeError("ds must be a xarray.Dataset")

    av = ds.mean(dim=avedim)
    return av


# this is where refineDiag should go
