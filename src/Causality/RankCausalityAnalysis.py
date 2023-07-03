from Aggregation.ContentSpace import ContentSpace
from Aggregation.ContentDemandSupply import ContentDemandSupply
from TS.TimeSeriesBuilder import TimeSeriesBuilder

from Causality.CausalityAnalysisTool import cos_similarity, gc_score_for_lags
from analysis import calculate_bhattacharyya_ranks,\
    calculate_social_support_ranks

from typing import Dict, List, Set, Callable, Sequence


class RankCausalityAnalysis:

    space: ContentSpace
    ts_builder: TimeSeriesBuilder
    ds: ContentDemandSupply

    b_rank_list: Dict[int, List[int]]
    ss_rank_list: Dict[int, List[int]]

    user_ids: Set[int] # helper

    def __init__(self, space: ContentSpace, ts_builder: TimeSeriesBuilder):
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
        demand_in_community_list = self.ts_builder.create_mapping_series("demand_in_community")
        original_tweets_list = self.ts_builder.partition_tweets_by_tweet_type("original_tweets")
        retweets_of_in_comm_list = self.ts_builder.partition_tweets_by_tweet_type("retweets_of_in_comm")

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

    def do_cos_similarity(self, filter_method: Callable[[Sequence], Sequence],
                          user_id: int, lags: List[int]) -> Dict[int, float]:
        b_seq = self.b_rank_list[user_id]
        ss_seq = self.ss_rank_list[user_id]
        result_dict = {}
        for l in lags:
            if l < 0:
                result_dict[l] = cos_similarity(filter_method(ss_seq[:l]),
                                                filter_method(b_seq[-l:]))
            elif l > 0:
                result_dict[l] = cos_similarity(filter_method(b_seq[:-l]),
                                                filter_method(ss_seq[l:]))
            else:
                result_dict[l] = cos_similarity(filter_method(b_seq),
                                                filter_method(ss_seq))
        return result_dict

    def do_granger_cause(self, filter_method: Callable[[Sequence], Sequence],
        user_id: int, lags: List[int]) -> Dict[int, float]:
        b_seq = self.b_rank_list[user_id]
        ss_seq = self.ss_rank_list[user_id]

        # filter
        b_seq = filter_method(b_seq)
        ss_seq = filter_method(ss_seq)

        result_p_val = gc_score_for_lags(b_seq, ss_seq, lags)
        return dict(zip(lags, result_p_val))
