from Aggregation.ContentSpace import ContentSpace
from Aggregation.ContentDemandSupply import ContentDemandSupply
from TS.SimpleTimeSeriesBuilder import SimpleTimeSeriesBuilder

from Causality.CausalityAnalysisTool import *
from analysis import calculate_bhattacharyya_ranks, \
    calculate_social_support_ranks

from typing import Dict, List, Set
import matplotlib.pyplot as plt


class RankCausalityAnalysis:

    space: ContentSpace
    ts_builder: SimpleTimeSeriesBuilder
    ds: ContentDemandSupply

    b_rank_list: Dict[int, List[int]]
    ss_rank_list: Dict[int, List[int]]

    user_ids: Set[int]  # helper

    def __init__(self, space: ContentSpace, ts_builder: SimpleTimeSeriesBuilder):
        self.space = space
        self.ts_builder = ts_builder
        self.ds = ts_builder.ds

        self.user_ids = space.get_all_user_ids()

        self.b_rank_list = {user_id: [] for user_id in self.user_ids}
        self.ss_rank_list = {user_id: [] for user_id in self.user_ids}
        self._create_b_distance_and_social_support_rank()

    def _create_b_distance_and_social_support_rank(self) -> None:
        """Copy most code from analysis.py
        plot_bhattacharyya_and_social_support_rank().
        """
        supply_list = self.ts_builder.create_mapping_series("supply")
        demand_in_community_list = self.ts_builder.create_mapping_series(
            "demand_in_community")
        original_tweets_list = self.ts_builder.partition_tweets_by_tweet_type(
            "original_tweets")
        retweets_of_in_comm_list = self.ts_builder.partition_tweets_by_tweet_type(
            "retweets_of_in_comm")

        for i in range(len(supply_list)):
            # Creation
            b_ranks = calculate_bhattacharyya_ranks(
                self.space, self.ds, supply_list[i], demand_in_community_list[i]
            )
            ss_ranks = calculate_social_support_ranks(
                self.space, original_tweets_list[i], retweets_of_in_comm_list[i]
            )

            # Storage
            for user_id in self.user_ids:
                self.b_rank_list[user_id].append(b_ranks[user_id])
                self.ss_rank_list[user_id].append(ss_ranks[user_id])

    def do_cos_similarity(self, user_id: int, lags: List[int]) -> \
            Dict[int, float]:
        """Perform Cosine Similarity Measure to Bhattacharyya distance
        and social support series for <user_id>.
        """
        b_seq = self.b_rank_list[user_id]
        ss_seq = self.ss_rank_list[user_id]

        output_list = cs_for_lags(b_seq, ss_seq, lags)
        return dict(zip(lags, output_list))

    def do_granger_cause(self, user_id: int, lags: List[int]) -> \
            Dict[int, float]:
        """Perform Granger Causality to Bhattacharyya distance
        and social support series for <user_id>.
        """
        b_seq = self.b_rank_list[user_id]
        ss_seq = self.ss_rank_list[user_id]

        result = {}
        for lag in lags:
            if lag < 0:
                result[lag] = gc_score_for_lag(ss_seq, b_seq, -lag)
            elif lag > 0:
                result[lag] = gc_score_for_lag(b_seq, ss_seq, lag)
            else:
                result[lag] = 1
        return result

    def plot_user_curve(self, user_id: int, save: bool) -> None:
        b_seq = self.b_rank_list[user_id]
        ss_seq = self.ss_rank_list[user_id]

        plt.figure()
        plt.plot(self.ts_builder.time_stamps, b_seq, label="B distance")
        plt.plot(self.ts_builder.time_stamps, ss_seq, label="social support")
        plt.gcf().autofmt_xdate()
        title = "user tweet_id: " + str(user_id)
        plt.title(title)
        if save:
            plt.savefig("../results/" + title)
        else:
            plt.show()
