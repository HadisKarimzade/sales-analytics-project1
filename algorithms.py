"""
Custom sorting and searching algorithms + timing helpers.

Requirements satisfied:
- Custom sorting algorithm (merge sort)
- Custom searching algorithm (linear + binary search)
- Timing comparisons with built-ins (via timeit)
"""
from __future__ import annotations

from dataclasses import dataclass
from timeit import timeit
from typing import Callable, List, Sequence, TypeVar

T = TypeVar("T")


def merge_sort(arr: List[T]) -> List[T]:
    """Stable merge sort. Time: O(n log n), Space: O(n)."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: List[T], right: List[T]) -> List[T]:
    merged: List[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def linear_search(arr: Sequence[T], target: T) -> int:
    """Linear search. Time: O(n). Returns index or -1."""
    for i, v in enumerate(arr):
        if v == target:
            return i
    return -1


def binary_search(sorted_arr: Sequence[T], target: T) -> int:
    """Binary search on a sorted array. Time: O(log n). Returns index or -1."""
    lo, hi = 0, len(sorted_arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_arr[mid] == target:
            return mid
        if sorted_arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


@dataclass
class TimingResult:
    custom_seconds: float
    builtin_seconds: float
    speedup: float  # builtin/custom


def compare_sort_timing(data: List[float], repeats: int = 3) -> TimingResult:
    custom = timeit(lambda: merge_sort(list(data)), number=repeats)
    builtin = timeit(lambda: sorted(list(data)), number=repeats)
    speedup = (custom / builtin) if builtin > 0 else float("inf")
    return TimingResult(custom_seconds=custom, builtin_seconds=builtin, speedup=speedup)


def compare_search_timing(sorted_data: List[float], target: float, repeats: int = 1000) -> TimingResult:
    custom = timeit(lambda: binary_search(sorted_data, target), number=repeats)
    builtin = timeit(lambda: (target in sorted_data), number=repeats)
    speedup = (custom / builtin) if builtin > 0 else float("inf")
    return TimingResult(custom_seconds=custom, builtin_seconds=builtin, speedup=speedup)
