# freedompp: post-processing tool xml-free


## Install

```
python setup.py install
```

## Quick start guide

This tool can be used either on the command line or interpreted in python. On the command line, run
```freedompp -h``` to see which options are available. Most common are choice of type (timeserie = ts,
annual average = ann or monthly average = mm), field of interest, years to process and paths to history
and pp directories.

* Create a timeserie of **so** with:

```
freedompp -t ts -f so -c ocean_month_z -s 96 -e 100 -d /archive/myrun/history -o /archive/myrun/pp
```

* Compute the monthly averages with:

```
freedompp -t mm -c ocean_month -s 96 -e 100 -d /archive/myrun/history -o /archive/myrun/pp
```

Other useful options include renaming the output component e.g. ```-r new_component_name```,
changing chunk sizes e.g. ```-K time 1 z_l 35```, support for tiled output ```-N tile1.nc```,
split files, as well as various other overrides. For example:

```
freedompp -t ts -f thetao -c ocean_month_z -s 2018 -e 2018 \
          -d /archive/myrun/history -o /archive/myrun/pp \
          -K time 1 --prefix="" -R -N 4
```

recombines (-R) split files .nc.000[0-3] (-N/--nsplit=4) stored in the tar file without a prefix and write the recombined file with a chunking (-K/--chunk) of 1 time record.

By default, freedompp will load netcdf files from the tar files directly into memory. There is an option to write the history files to disk, using:

```
freedompp -t ts -f so -c D2ocean_month_z -s 2012 -e 2017 \
          -d /archive/myrun/history -o /archive/myrun/pp \
          -W -X /work/tmpdir
```

The package can also be used in interactive python environments, with function to load and write
timeseries and averages.

* load a timeserie in memory:

```python
from freedompp.libfreedompp import load_timeserie
ts = load_timeserie('so', 'ocean_month_z', 96, 100,
                    historydir='/archive/myrun/history')
```

* write a timeserie to disk:

```python
from freedompp.libfreedompp import write_timeserie
write_timeserie('so', 'ocean_month_z', 96, 100,
                historydir='/archive/myrun/history',
                ppdir='/archive/myrun/pp')
```
* compute monthly and annual averages:

```python
from freedompp.libfreedompp import compute_average
monthly = compute_average('ocean_daily', 96,1 00, avtype='mm',
                          historydir='/archive/myrun/history')
annual = compute_average('ocean_daily', 96, 100, avtype='ann',
                         historydir='/archive/myrun/history')
```

* or write them to disk:

```python
from freedompp.libfreedompp import write_average
monthly = write_average('ocean_daily', 96, 100, avtype='mm',
                          historydir='/archive/myrun/history',
                          ppdir='/archive/myrun/pp')
annual = write_average('ocean_daily', 96, 100, avtype='ann',
                         historydir='/archive/myrun/history',
                         ppdir='/archive/myrun/pp')
```

and all aforementioned options are obviously available in python as well.
