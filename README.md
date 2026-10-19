

Tool to export your personal Endomondo data

**Note**: Endomondo has shut down, so the export script is only kept for reference in [old/export.py](old/export.py).
The DAL still reads existing exports.

# Installing

`pip3 install 'endoexport[dal,optional] @ git+https://github.com/karlicoss/endoexport'`

- `dal` is needed to access exported data
- `optional` is for faster JSON processing

# Using the data

``` python
from endoexport.dal import DAL

# e.g. DAL(['/path/to/endomondo/export.json'])
dal = DAL([fake_export])
for w in dal.workouts():
    if isinstance(w, Exception):
        print('error:', w)
        continue
    print(f'{w.start_time:%Y-%m-%d} {w.sport} {w.duration} avg HR {w.heart_rate_avg:.0f}')
```

    2010-01-01 Running 0:38:00 avg HR 160
    2010-01-02 Running 1:01:00 avg HR 160
    2010-01-03 Running 0:45:00 avg HR 160
    2010-01-04 Running 0:38:00 avg HR 160
    2010-01-05 Running 0:40:00 avg HR 160

The DAL also has a command line interface:

You can use this DAL (Data Access/Abstraction Layer) module to access your exported data, even offline.
I elaborate on motivation behind it [here](https://beepb00p.xyz/exports.html#dal).

- the main use case is importing it as a Python module for **programmatic access** to your data.

  You can find some inspiration in [`my.`](https://beepb00p.xyz/mypkg.html) package that I’m using as an API to all my personal data.

- to test it against your export, simply run: `python3 -m endoexport.dal /path/to/export`

- you can also try it interactively in an IPython shell: `python3 -m endoexport.dal /path/to/export --interactive`

# Updating README

This README is generated from a ‘literate’ Quarto [README.qmd](README.qmd) via the following command:

`tox -e quarto`

If you want to correct something, feel free to simply update `README.md` though, I can reconcile the changes next time I regenerate it.
