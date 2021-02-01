import pytest


def test_check_bounds():
    from freedompp.libstruct import check_bounds

    with pytest.raises(ValueError):
        check_bounds(2, 1)

    check_bounds(1, 1)
    check_bounds(1, 2)


def test_format_year_bounds():
    from freedompp.libstruct import format_year_bounds

    ys, ye = format_year_bounds(1, 2, cformat="yyyy")
    assert len(ys) == 4
    assert len(ye) == 4
    assert ys == "0001"
    assert ye == "0002"

    ys, ye = format_year_bounds(1, 2, cformat="yyyymm")
    assert len(ys) == 6
    assert len(ye) == 6
    assert ys == "000101"
    assert ye == "000212"

    ys, ye = format_year_bounds(1, 2, cformat="yyyymmdd")
    assert len(ys) == 8
    assert len(ye) == 8
    assert ys == "00010101"
    assert ye == "00021231"

    ys, ye = format_year_bounds(1, 2, cformat="yyyymmddhh")
    assert len(ys) == 10
    assert len(ye) == 10
    assert ys == "0001010100"
    assert ye == "0002123123"


@pytest.mark.parametrize("FREQ", ["1y", "1m", "1d", "6hr", "3hr", "wrong"])
def test_print_freq(FREQ):
    from freedompp.libstruct import print_freq

    if FREQ == "wrong":
        with pytest.raises(ValueError):
            out = print_freq(FREQ)
    else:
        out = print_freq(FREQ)
        assert isinstance(out, str)


def test_infer_freq():
    from freedompp.libstruct import infer_freq

    freq = infer_freq("ocean_annual")
    assert freq == "1y"

    freq = infer_freq("ocean_monthly")
    assert freq == "1m"

    freq = infer_freq("ocean_daily")
    assert freq == "1d"

    freq = infer_freq("ocean_4xdaily")
    assert freq == "6hr"

    freq = infer_freq("ocean_8xdaily")
    assert freq == "3hr"

    freq = infer_freq("ocean")
    assert freq is None


def test_tsfilename():
    from freedompp.libstruct import tsfilename

    # test infer
    fname = tsfilename("so", "ocean_annual", 1981, 1985)
    assert fname == "ocean_annual.1981-1985.so.nc"

    fname = tsfilename("so", "ocean_monthly", 1981, 1985)
    assert fname == "ocean_monthly.198101-198512.so.nc"

    fname = tsfilename("so", "ocean_daily", 1981, 1985)
    assert fname == "ocean_daily.19810101-19851231.so.nc"

    fname = tsfilename("so", "ocean_8xdaily", 1981, 1985)
    assert fname == "ocean_8xdaily.1981010100-1985123123.so.nc"

    # test override
    fname = tsfilename("so", "ocean_8xdaily", 1981, 1985, freq="1y")
    assert fname == "ocean_8xdaily.1981-1985.so.nc"

    fname = tsfilename("so", "river_8xdaily", 1981, 1985, ftype="tile1.nc")
    assert fname == "river_8xdaily.1981010100-1985123123.so.tile1.nc"


def test_avfilename():
    from freedompp.libstruct import avfilename

    fname = avfilename("ocean_annual", 1981, 1985, "ann")
    assert fname == "ocean_annual.1981-1985.ann.nc"

    fname = avfilename("ocean_annual", 1981, 1985, "01")
    assert fname == "ocean_annual.1981-1985.01.nc"

    fname = avfilename("river_cubic", 1981, 1985, "01", ftype="tile1.nc")
    assert fname == "river_cubic.1981-1985.01.tile1.nc"


def test_ppsubdirname():
    from freedompp.libstruct import ppsubdirname

    dirname = ppsubdirname("ocean_annual", 1, 5, pptype="av")
    assert dirname == "ocean_annual/av/annual_5yr"

    dirname = ppsubdirname("ocean_month", 1, 10, pptype="av")
    assert dirname == "ocean_month/av/monthly_10yr"

    dirname = ppsubdirname("ocean_annual", 1, 5, pptype="ts")
    assert dirname == "ocean_annual/ts/annual/5yr"

    dirname = ppsubdirname("ocean_daily", 1, 10, pptype="ts")
    assert dirname == "ocean_daily/ts/daily/10yr"
