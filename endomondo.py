#!/usr/bin/env python3.6
from sys import stdout, stderr
import json

import endoapi.endomondo
from endomondo_secrets import USERNAME, TOKEN

def main():
    endomondo = endoapi.endomondo.Endomondo(email=USERNAME, token=TOKEN)
    maximum_workouts = None # None means all

    workouts = endomondo.get_workouts_raw(maximum_workouts)
    json.dump(workouts, stdout, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
