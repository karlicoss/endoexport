#!/usr/bin/env python3
from sys import stdout, stderr
import json

from kython import import_from
endoapi = import_from('/L/zzz_syncthing/repos/endoapi', 'endoapi')
import endoapi.endomondo
from endomondo_secrets import USERNAME, TOKEN

def main():
    endomondo = endoapi.endomondo.Endomondo(email=USERNAME, token=TOKEN)
    maximum_workouts = None # None means all

    workouts = endomondo.get_workouts_raw(maximum_workouts)
    json.dump(workouts, stdout, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
