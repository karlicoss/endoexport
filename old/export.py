#!/usr/bin/env python3
import argparse
import json

from .exporthelpers.export_helper import Json

import endoapi


def get_json(**params) -> Json:
    endomondo = endoapi.endomondo.Endomondo(**params)

    maximum_workouts = None # None means all
    workouts = endomondo.get_workouts_raw(maximum_workouts)
    return workouts


Token = str
def login(email: str) -> Token:
    print(f"Logging in as {email}")
    password = input('Your password: ')
    endomondo = endoapi.endomondo.Endomondo(email=email, password=password)
    token = endomondo.token
    print('Your token:')
    print(token)
    return token


def make_parser():
    from .exporthelpers.export_helper import setup_parser, Parser
    parser = Parser("Tool to export your personal Endomondo data")
    setup_parser(parser=parser, params=['email', 'token']) # TODO exports -- need help for each param?
    parser.add_argument('--login', action='store_true', help='''
This will log you in and give you the token (you'll need your password).
You only need to do it once, after that just store the token and use it.
    ''')
    return parser


def main() -> None:
    # TODO add logger configuration to export_helper?
    # TODO autodetect logzero?
    args = make_parser().parse_args()

    params = args.params
    dumper = args.dumper

    if args.login:
        login(email=params['email'])
        return

    j = get_json(**params)
    js = json.dumps(j, indent=1, ensure_ascii=False)
    dumper(js)


if __name__ == '__main__':
    main()
