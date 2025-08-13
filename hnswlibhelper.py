#!/usr/bin/env python
"""
Hnswlibhelper.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : hnswlibhelper
# @created     : Wednesday Aug 13, 2025 13:47:09 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
def recommend_hnsw_params(N: int):
    """
    Recommend HNSWlib parameters based on dataset size.

    Parameters:
        N (int): Number of records (vectors) in the dataset.

    Returns:
        dict: Recommended values for M, ef_construction, ef_search.
    """

    # M (max number of connections per node)
    if N <= 100:
        M = min(N - 1, 64)
    elif N <= 10_000:
        M = 48 if N > 1000 else 32
    elif N <= 1_000_000:
        M = 32
    else:
        M = 16  # huge datasets — memory control

    # ef_construction (index build quality)
    if N <= 100:
        ef_construction = 500
    elif N <= 10_000:
        ef_construction = 400
    elif N <= 1_000_000:
        ef_construction = 200
    else:
        ef_construction = 150

    # ef_search (query thoroughness)
    if N <= 100:
        ef_search = N  # exact search for small datasets
    elif N <= 10_000:
        ef_search = M * 3
    elif N <= 1_000_000:
        ef_search = M * 2
    else:
        ef_search = M  # speed over recall

    return {
        "M": M,
        "ef_construction": ef_construction,
        "ef_search": ef_search
    }
