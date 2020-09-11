# ugh wtf?? in theory __init__.py  isn't necessary
# however, without it, something like
# MYPYPATH=src mypy -p endoexport
# doesn't seem to detect errors in files (e.g. export.py)
# similarly, mypy src only works properly if __init__.py is present. ugh.
