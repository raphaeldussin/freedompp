from jinja2 import Template


mheader = """SHELL=/bin/bash
HISTORYDIR ?= {{ hdir }}
PPDIR ?= {{ ppdir }}
YBEG ?= {{ ybeg }}
YEND ?= {{ yend }}

# Build the list of years between year begin and year end
YEARS = $(shell seq -f %04g $(YBEG) $(YEND) )
# FMS output write in the format YYYY0101
JAN1 = 0101
# Suffix of history tar files
TARSUFFIX = .nc.tar
FIRSTTAG = $(YBEG)$(JAN1)
FIRSTTAR = $(FIRSTTAG)$(TARSUFFIX)
ALLTARS = $(foreach year,$(YEARS),$(year)$(JAN1)$(TARSUFFIX))

"""

mrule = """
{{ ppdir }}/{{outfile}}: $(ALLTARS)
\t{{ runcmd }}

"""


def write_makefile_header(historydir, ppdir, ybeg, yend, mfile='Makefile'):
    """ write the header of the Makefile """

    lines = Template(mheader).render(hdir=historydir, ppdir=ppdir,
                                     ybeg=ybeg, yend=yend)
    fid = open(mfile, 'w')
    fid.write(lines)
    fid.close()
    return None


def write_rule(ppdir, outfile, runcmd, mfile='Makefile'):
    """ write an individual rule in Makefile """

    lines = Template(mrule).render(ppdir=ppdir, outfile=outfile, runcmd=runcmd)
    fid = open(mfile, 'a')
    fid.write(lines)
    fid.close()
    return None
