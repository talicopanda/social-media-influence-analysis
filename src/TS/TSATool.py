from typing import Sequence
import numpy as np


def identity(x: Sequence) -> Sequence:
    return x


def sma(x: Sequence, window: int) -> Sequence:
    # Note that <window> should be an odd number
    if not isinstance(window, int) or window % 2 != 1 or window < 0:
        raise ValueError("Window size should be positive odd integer")

    seq_len = len(x)
    ma = [0] * seq_len

    if len(x) <= window:
        raise ValueError("window size too large")

    half_w = window // 2
    for i in range(seq_len):
        if i < half_w:
            target_list = x[:i + half_w + 1] + [x[0]] * (window - i - half_w - 1)
        elif i > seq_len - half_w - 1:
            target_list = x[i - half_w:] + [x[-1]] * (window - seq_len + i - half_w)
        else:
            target_list = x[i - half_w: i + half_w + 1]
        assert len(target_list) == window
        ma[i] = np.average(target_list)
    return ma


def wma(x: Sequence, window: int, weight: Sequence) -> Sequence:
    # Note that <window> should be an odd number
    if not isinstance(window, int) or window % 2 != 1 or window < 0:
        raise ValueError("Window size should be positive odd integer")
    if len(weight) != window:
        raise ValueError("Weight should have the length window")

    seq_len = len(x)
    ma = [0] * seq_len

    # normalize weight
    weight = weight / np.sum(weight)

    if len(x) <= window:
        raise ValueError("window size too large")

    half_w = window // 2
    for i in range(seq_len):
        if i < half_w:
            target_list = x[:i + half_w + 1] + [x[0]] * (window - i - half_w - 1)
        elif i > seq_len - half_w - 1:
            target_list = x[i - half_w:] + [x[-1]] * (window - seq_len + i - half_w)
        else:
            target_list = x[i - half_w: i + half_w + 1]
        assert len(target_list) == window
        ma[i] = np.dot(weight, target_list)
    return ma
