#!/usr/bin/env python3
from datetime import timedelta, datetime
import json
from pathlib import Path
from typing import Any, Dict, NamedTuple, Sequence, Union, List, TypeVar, Iterable, Optional

from .exporthelpers import dal_helper
from .exporthelpers.dal_helper import Res, PathIsh

import endoapi.endomondo
from endoapi.endomondo import Point


logger = dal_helper.logger('endoexport.dal', level='debug')


class Workout(endoapi.endomondo.Workout):
    # todo could patch up sports list in endoapi?
    # todo move type annotations to endoexport.Workout?
    id: str
    duration: timedelta
    sport: str
    start_time: datetime

    @property
    def heart_rate_avg(self) -> Optional[float]:
        # NOTE: sometimes it's missing in raw data, so has to be optional
        return self.properties.get('heart_rate_avg')

    # todo would be interesting to calculate from gps and compare?
    # todo hopefully it's km/h?
    @property
    def speed_avg(self) -> Optional[float]:
        return self.properties.get('speed_avg')

    @property
    def kcal(self) -> float:
        return self.calories

    @property
    def measurements(self) -> Sequence[Res[Point]]:
        return self.points


class DAL:
    def __init__(self, sources: Sequence[PathIsh]) -> None:
        self.sources = list(map(Path, sources))

    def workouts(self) -> Iterable[Res[Workout]]:
        src = max(self.sources)
        # todo endomondo exports all data, so not worth merging?
        js = json.loads(src.read_text())
        # for some reason they are in reverse chronological order in jsons
        for j in reversed(js):
            try:
                endoapi_workout = Workout(j)
            except Exception as e:
                e.__cause__ = RuntimeError(f'While parsing {j}')
                logger.exception(e)
                yield e
                continue
            # todo not sure if there is an easier way of doing this??
            # basically we want to add some extra methods (declared in Workout) to the original class, without explicit delegation
            nw = Workout.__new__(Workout)
            nw.__dict__ = endoapi_workout.__dict__
            yield nw


def demo(dao: DAL) -> None:
    import pandas as pd # type: ignore
    import matplotlib.pyplot as plt # type: ignore

    # TODO split errors properly? move it to dal_helper?
    # todo or add some basic error handlign stuff to dal_helper?
    workouts: List[Workout] = [w for w in dao.workouts() if not isinstance(w, Exception)]

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
