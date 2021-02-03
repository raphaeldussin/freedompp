# freedompp


## install

```
python setup.py install
```

## quick start guide

* load a timeserie in memory:

```python
from freedompp.libfreedompp import load_timeserie
hdir='/archive/Raphael.Dussin/FMS2019.01.03_devgfdl_20201120/CM4_piControl_c192_OM4p125/gfdl.ncrc4-intel18-prod-openmp/history'
ts, _ = load_timeserie('so', 'D2ocean_month_z', 96, 100, historydir=hdir)
```

* write a timeserie to disk

```python
from freedompp.libfreedompp import load_timeserie
hdir='/archive/Raphael.Dussin/FMS2019.01.03_devgfdl_20201120/CM4_piControl_c192_OM4p125/gfdl.ncrc4-intel18-prod-openmp/history'
ppdir='/local2/home/sandbox/pptest'
write_timeserie('so', 'D2ocean_month_z', 96, 100, historydir=hdir, ppdir=ppdir)
```
