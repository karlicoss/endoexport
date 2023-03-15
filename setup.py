# see https://github.com/karlicoss/pymplate for up-to-date reference


from setuptools import setup, find_namespace_packages # type: ignore


COMMON_DEPS = [
    # I'm using some upstream unmerged changes, so unfortunately need my own fork
    'endoapi @ git+https://github.com/karlicoss/endoapi.git',
    # TODO hmm maybe I need to rename the setup.py for my fork? to make it less confusing
    # uncomment to test against the filesystem package
    # 'endoapi @ git+file://DUMMY/path/to/endoapi',
]


EXPORT_DEPS = COMMON_DEPS

DAL_DEPS = COMMON_DEPS

ALL_DEPS = sorted({*EXPORT_DEPS, *DAL_DEPS})


def main() -> None:
    # works with both ordinary and namespace packages
    pkgs = find_namespace_packages('src')
    pkg = min(pkgs) # lexicographically smallest is the correct one usually?
    setup(
        name=pkg,
        use_scm_version={
            'version_scheme': 'python-simplified-semver',
            'local_scheme': 'dirty-tag',
        },
        setup_requires=['setuptools_scm'],

        # otherwise mypy won't work
        # https://mypy.readthedocs.io/en/stable/installed_packages.html#making-pep-561-compatible-packages
        zip_safe=False,

        packages=pkgs,
        package_dir={'': 'src'},
        # necessary so that package works with mypy
        package_data={pkg: ['py.typed']},

        ## ^^^ this should be mostly automatic and not requiring any changes

        install_requires=ALL_DEPS,
        extras_require={
            'dal': DAL_DEPS,
            'export': EXPORT_DEPS,
            'testing': [
                'pytest',
                'numpy',  # for data generator
            ],
            'linting': [
                'pytest',
                'mypy',
                'lxml',  # lxml for mypy coverage report
                'orjson',  # optional packages
            ],
        },
    )


if __name__ == '__main__':
    main()

