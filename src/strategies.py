# Coalescence strategies
# These all take the JSON output of n servers
# and coalesces them based on the strategy listed
from typing import Callable, Dict, List


def default_strategy(oop_max_list, remaining_oop_max_list, copay_list):
    """Default strategy is to take the max oop_max and remaining_oop_max, and
    take the max copay, but ensure it is no higher than the remaining_oop_max"""
    oop_max = max(oop_max_list)
    remaining_oop_max = max(remaining_oop_max_list)
    copay = min(remaining_oop_max, max(copay_list))
    return oop_max, remaining_oop_max, copay

def min_all(oop_max_list, remaining_oop_max_list, copay_list):
    return min(oop_max_list), min(remaining_oop_max_list), min(copay_list)

def max_all(oop_max_list, remaining_oop_max_list, copay_list):
    return max(oop_max_list), max(remaining_oop_max_list), max(copay_list)

def avg_all(oop_max_list, remaining_oop_max_list, copay_list):
    oop_max_avg = int(round(sum(oop_max_list) / len(oop_max_list), 0))
    remaining_oop_max_avg = int(round(sum(remaining_oop_max_list) / len(remaining_oop_max_list), 0))
    copay_list_avg = int(round(sum(copay_list) / len(copay_list), 0))
    return oop_max_avg, remaining_oop_max_avg, copay_list_avg

def coalesce(server_outputs: List[Dict[str, int]], coalesce_function: Callable[[List[int], List[int], List[int]], any]):
    oop_max_list = []
    remaining_oop_max_list = []
    copay_list = []

    for output in server_outputs:
        oop_max_list.append(output.get('oop_max', -1))
        remaining_oop_max_list.append(output.get('remaining_oop_max', -1))
        copay_list.append(output.get('copay', -1))

    oop_max, remaining_oop_max, copay = coalesce_function(oop_max_list, remaining_oop_max_list, copay_list)
    return {
        'oop_max': oop_max,
        'remaining_oop_max': remaining_oop_max,
        'copay': copay
    }
    