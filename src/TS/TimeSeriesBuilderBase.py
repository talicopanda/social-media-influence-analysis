from abc import ABC, abstractmethod
from User.UserType import UserType
from Aggregation.ContentSpace import ContentSpace
from Aggregation.ContentDemandSupply import ContentDemandSupply

from typing import List, Union, Any, Sequence
from datetime import datetime, timedelta
import numpy as np


class TimeSeriesBuilderBase(ABC):
    """
    A parent class to all time series builder classes.
    """
    ds: ContentDemandSupply
    space: ContentSpace
    time_stamps: List[datetime]

    def _create_time_stamps(self, start: datetime, end: datetime,
                            period: timedelta) -> None:
        """Create a list of time stamps for partitioning the Tweet, and
        store in self.time_stamps.
        """
        curr_time = start
        while curr_time <= end:
            self.time_stamps.append(curr_time)
            curr_time += period

    def get_time_stamps(self) -> List[datetime]:
        return self.time_stamps

    @abstractmethod
    def create_time_series(self, user_type_or_id: Union[UserType, int],
                           content_repr: Any, mapping: str) -> Sequence:
        """Return the time series for <user_type_or_id> for <content_repr>.
        """
        raise NotImplementedError

    def create_all_type_time_series(self, user_type_or_id: Union[UserType, int],
                                    mapping: str) -> Sequence:
        """Return demand or supply time series for <user_type_or_id>.
        """
        # initialization
        series = None

        # accumulation
        for content_type in self.space.get_all_content_type_repr():
            a = self.create_time_series(user_type_or_id, content_type, mapping)
            if series is None:
                series = a
            else:
                series = np.add(series, a)

        # convert back
        return list(series)

    def create_agg_time_series(self, content_repr: Any, mapping: str) -> Sequence:
        """Return aggregate time series.
        """
        # check
        if mapping not in ["demand_in_community", "demand_out_community",
                           "supply"]:
            raise KeyError(f"Invalid Mapping Type {mapping}.")

        # demand
        if mapping == "demand_in_community":
            consumer_demand = self.create_time_series(UserType.CONSUMER,
                                                      content_repr, mapping)
            core_node_demand = self.create_time_series(UserType.CORE_NODE,
                                                       content_repr, mapping)
            demand = np.add(consumer_demand, core_node_demand)
            return demand.tolist()

        # supply
        elif mapping == "supply":
            producer_supply = self.create_time_series(UserType.PRODUCER,
                                                      content_repr, mapping)
            core_node_supply = self.create_time_series(UserType.CORE_NODE,
                                                       content_repr, mapping)
            supply = np.add(producer_supply, core_node_supply)
            return supply.tolist()

