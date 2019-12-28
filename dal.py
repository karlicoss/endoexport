#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict, NamedTuple, Sequence, Union, List, TypeVar, Iterator

import dal_helper
from dal_helper import Json, PathIsh


T = TypeVar('T')
Res = Union[T, Exception]


from modules.endoapi import endoapi
Workout = endoapi.endomondo.Workout


logger = dal_helper.logger('endoexport', level='debug')


class DAL:
    def __init__(self, sources: Sequence[PathIsh]) -> None:
        self.sources = list(map(Path, sources))

    def workouts(self) -> Iterator[Res[Workout]]:
        src = max(self.sources) # TODO not sure if worth merging?
        js = json.loads(src.read_text())
        # for some reason they are in reverse chronological order in jsons
        for j in reversed(js):
            try:
                yield Workout(j)
            except Exception as e:
                e.__cause__ = RuntimeError(f'While parsing {j}')
                logger.exception(e)
                yield e


def demo(dao: DAL) -> None:
    import pandas as pd # type: ignore
    import matplotlib.pyplot as plt # type: ignore

    # TODO split errors properly? move it to dal_helper?
    workouts = list(w for w in dao.workouts() if not isinstance(w, Exception))

    print(f"Parsed {len(workouts)} workouts")
    df = pd.DataFrame({
        'dt'      : w.start_time,
        'calories': w.calories,
        'sport'   : w.sport,
    } for w in workouts)
    df.set_index('dt', inplace=True)

    print(df)

    cal = df.resample('D').sum() # index by days
    cal = cal.rolling('30D').mean() # use moving average to smooth out the plot
    cal.plot(title='Exercise (30 days moving average)')

    plt.figure()
    breakdown = df.groupby('sport')['calories'].sum()
    breakdown.plot.pie(title='Breakdown of calories burnt by sport')

    plt.show()


if __name__ == '__main__':
    dal_helper.main(DAL=DAL, demo=demo)
