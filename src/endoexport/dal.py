#!/usr/bin/env python3
from datetime import timedelta, datetime, timezone as TZ
import json
from pathlib import Path
from typing import Any, Dict, NamedTuple, Sequence, Union, List, TypeVar, Iterable, Optional

from .exporthelpers import dal_helper, logging_helper
from .exporthelpers.dal_helper import Res, PathIsh, Json

import endoapi.endomondo
from endoapi.endomondo import Point


logger = logging_helper.logger('endoexport.dal', level='debug')


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
        # endomondo exports all data, so not worth merging?
        src = max(self.sources)

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


class FakeData:
    def __init__(self, seed: int=0) -> None:
        self.seed = seed
        import numpy as np # type: ignore
        self.gen = np.random.default_rng(seed=self.seed)
        self.id = 0


        # hr is sort of a random walk?? probably not very accurate, but whatever
        # also keep within certain boundaries?
        self.cur_avg_hr  = 160.0
        self.avg_distance_km = 10
        self.avg_duration_min = 40

        # todo would be nice to separate parameters and the state
        import pytz # type: ignore
        self.tz = pytz.timezone('America/New_York')
        self.first_day = datetime.strptime('20100101', '%Y%m%d')
        # todo gaussian distribution??
       
    @property
    def today(self) -> datetime:
        return self.first_day + timedelta(days=self.id)

    # for now, only tuned to generate runs... later could have individual stateful generators for different exercise?
    # todo import some route from geo, and generate run based on a trace through it?
    def generate_one(self) -> Json:
        G = self.gen
        D = timedelta
        def N(mean, sigma):
            return max(G.normal(mean, sigma), 0) # meh

        def ntd(mean, sigma):
            # 'normal' timedelta minutes
            return D(minutes=int(N(mean, sigma)))

        start = self.today + D(hours=10) # todo randomize
        distance = N(self.avg_distance_km, 0.5)
        duration = ntd(self.avg_duration_min, 10)

        def fmtdt(x: datetime) -> str:
            return x.astimezone(TZ.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        ###
        points = [dict(
            # todo lat, lnt, alt??
            time=fmtdt(start + D(i)),
            hr=G.normal(self.cur_avg_hr, 20),
        ) for i in range(0, duration // D(seconds=1), 3)]
        d = dict(
            id=self.id,
            sport=0, # running
            start_time=fmtdt(start),
            duration=duration // D(seconds=1),
            points=points,
            speed_avg=distance / (duration / D(hours=1)),
            heart_rate_avg=self.cur_avg_hr,
        )
        ###

        self.id += 1
        self.cur_avg_hr += G.normal(0, 0.1)
        return d

    # TODO Json type should be union with List?
    def generate(self, count: int):
        return [self.generate_one() for _ in range(count)]


def test(tmp_path: Path) -> None:
    f = FakeData()
    data = f.generate(count=20)
    jf = tmp_path / 'data.json'
    jf.write_text(json.dumps(data))

    dal = DAL([jf])

    # todo generate errors too?
    for x in list(dal.workouts()):
        assert isinstance(x, Workout)
        assert x.sport is not None
        assert len(x.points) > 0
        assert x.speed_avg is not None


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
