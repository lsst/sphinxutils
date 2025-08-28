# -*- python -*-
from lsst.sconsUtils import scripts, state

# Python-only package
scripts.BasicSConstruct("sphinxutils", disableCc=True, noCfgFile=True)

mypy = state.env.Command(
    "mypy.log",
    "python/lsst/sphinxutils",
    "mypy python/lsst 2>&1 | tee -a mypy.log"
)
state.env.Alias("mypy", mypy)
