#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x72e9b98a

# Compiled with Coconut version 1.2.2-post_dev12 [Colonel]

# Coconut Header: --------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_compose, _coconut_pipe, _coconut_starpipe, _coconut_backpipe, _coconut_backstarpipe, _coconut_bool_and, _coconut_bool_or, _coconut_minus, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: ------------------------------------------------------

import os
from platform import python_version
from inspect import getmembers
from inspect import isclass
from dataget import get_path
from dataget.dataset import DataSet


def load_datasets(DATASETS, module_root, datasets_path):
    datasets = ((_coconut.functools.partial(map, _coconut.operator.methodcaller("replace", ".py", "")))((_coconut.functools.partial(filter, lambda x: not x.startswith("_")))((_coconut.functools.partial(filter, _coconut.operator.methodcaller("endswith", ".py")))(os.listdir(datasets_path)))))

    for dataset in datasets:
        dataset_module_name = dataset.replace("-", "_")
        module_name = "{}.{}".format(module_root, dataset_module_name)

        dataset_module = (_coconut.functools.partial(get_dataset_module, module_name))((_coconut.functools.partial(os.path.join, datasets_path))("{}.py".format(dataset)))
        [(dataset_class_name, dataset_class)] = getmembers(dataset_module, is_subclass_of_dataset)

        DATASETS.update({dataset: dataset_class})


def load_custom_datasets(DATASETS):
    datasets_path = "/".join(__file__.split("/")[:-1])
    datasets_path = os.path.join(datasets_path, "datasets")

    load_datasets(DATASETS, "datasets", datasets_path)


def load_plugin_datasets(DATASETS):
    datasets_path = get_path(global_=True)
    datasets_path = os.path.join(datasets_path, "datasets")

    if not os.path.exists(datasets_path):
        os.makedirs(datasets_path)
    else:
        load_datasets(DATASETS, "datasets", datasets_path)


def get_dataset_module(module_name, file_path):
    if python_version() >= "3.5":
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    elif python_version() >= "3":
        from importlib.machinery import SourceFileLoader
        module = SourceFileLoader(module_name, file_path).load_module()

    else:
        import imp
        module = imp.load_source(module_name, file_path)

    return module

def is_subclass_of_dataset(x):
    return isclass(x) and issubclass(x, DataSet) and x is not DataSet