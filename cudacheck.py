#!/usr/bin/env python
"""
Cudacheck.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : cudacheck
# @created     : Sunday Jun 15, 2025 20:42:38 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
