from setuptools import setup, find_namespace_packages # type: ignore


def main():
    pkgs = find_namespace_packages('src')
    pkg = min(pkgs)
    return setup(
        name=pkg,
        zip_safe=False,
        packages=pkgs,
        package_dir={'': 'src'},
        package_data={pkg: ['py.typed']},

        install_requires=[
            # I'm using some upstream unmerged changes, so unfortunately need my own fork
            'endoapi @ git+https://github.com/karlicoss/endoapi.git',
            # TODO hmm maybe I need to rename the setup.py for my fork? to make it less confusing
            # uncomment to test against the filesystem package
            # 'endoapi @ git+file://DUMMY/path/to/endoapi',
        ],
        extras_require={
            'testing': ['pytest', 'numpy'],
            'linting': ['pytest', 'mypy'],
        },
    )


if __name__ == '__main__':
    main()
