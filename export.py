#!/usr/bin/env python3
import argparse
import json
import logging

from export_helper import Json


def get_json(**params) -> Json:
    # TODO get rid of kython
    # meh, just use my fork
    from kython import import_from
    endoapi = import_from('/L/repos/endoapi', 'endoapi')
    import endoapi.endomondo # type: ignore
    endomondo = endoapi.endomondo.Endomondo(**params)

    maximum_workouts = None # None means all
    workouts = endomondo.get_workouts_raw(maximum_workouts)
    return workouts


def login(email: str):
    from kython import import_from
    endoapi = import_from('/L/repos/endoapi', 'endoapi')
    import endoapi.endomondo # type: ignore

    print(f"Logging in as {email}")
    password = input('Your password: ')
    endomondo = endoapi.endomondo.Endomondo(email=email, password=password)
    print('Your token:')
    print(endomondo.token)


def main():
    # TODO add logger configuration to export_helper?
    # TODO autodetect logzero?
    from export_helper import setup_parser
    parser = argparse.ArgumentParser("Tool to export your personal Endomondo data")
    setup_parser(parser=parser, params=['email', 'token']) # TODO exports -- need help for each param?
    parser.add_argument('--login', action='store_true', help='''
This will log you in and give you the token (you'll need your password).
You only need to do it once, after that just store the token and use it.
    ''')
    args = parser.parse_args()

    params = args.params
    dumper = args.dumper

    if args.login:
        login(email=params['email'])
        return

    j = get_json(**params)
    js = json.dumps(j, indent=1, ensure_ascii=False)
    dumper(js)


if __name__ == '__main__':
    # from kython.klogging import setup_logzero
    # setup_logzero(logging.getLogger('requests_oauthlib'), level=logging.DEBUG)
    main()

