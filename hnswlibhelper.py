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
from typing import Tuple

def recommend_hnsw_params(N: int, dim: int) -> Tuple[int, int, int]:
    """
    Recommend HNSWlib parameters based on dataset size and vector dimensions.

    Args:
        N: Number of items in the dataset
        dim: Dimensionality of the vectors

    Returns:
        Tuple containing:
            M: Number of bi-directional links for each element
            ef_construction: Construction time parameter
            ef_search: Search time parameter
    """
    # M
    if N <= 100:
        M = min(N - 1, 64 if dim > 512 else N - 1)
    elif N <= 10_000:
        M = 48 if dim > 512 else 32
    elif N <= 1_000_000:
        M = 32 if dim > 512 else 24
    else:
        M = 24 if dim > 512 else 16

    # ef_construction
    if N <= 100:
        ef_construction = 500
    elif N <= 10_000:
        ef_construction = 400
    elif N <= 1_000_000:
        ef_construction = 200
    else:
        ef_construction = 150

    # ef_search
    if N <= 100:
        ef_search = N
    elif N <= 10_000:
        ef_search = M * 3
    elif N <= 1_000_000:
        ef_search = M * 2
    else:
        ef_search = M

    return M, ef_construction, ef_search
