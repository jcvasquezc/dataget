#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x2e70997d

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

import urllib
import zipfile
import os
import shutil
from dataget.utils import get_file
from dataget.dataset import DataSet
from dataget.dataset import SubSet


TRAINING_SET_URL = "http://benchmark.ini.rub.de/Dataset/GTSRB_Final_Training_Images.zip"
TEST_SET_URL = "http://benchmark.ini.rub.de/Dataset/GTSRB_Final_Test_Images.zip"
TEST_CSV_URL = "http://benchmark.ini.rub.de/Dataset/GTSRB_Final_Test_GT.zip"


class GermanTrafficSignsDataset(DataSet):

    def __init__(self, *args, **kwargs):
        super(GermanTrafficSignsDataset, self).__init__(*args, **kwargs)

        self._training_images_path = os.path.join(self.training_set.path, "GTSRB/Final_Training/Images")
        self._test_images_path = os.path.join(self.test_set.path, "GTSRB/Final_Test/Images")


    @property
    def training_set_class(self):
        return TrainingGermanTrafficSignsDataset

    @property
    def test_set_class(self):
        return TestGermanTrafficSignsDataset

    @property
    def help(self):
        return "TODO"

    def reqs(self, **kwargs):
        return "pillow pandas numpy"


    def _download(self, **kwargs):
        get_file(TRAINING_SET_URL, self.path, "training-set.zip")
        get_file(TEST_SET_URL, self.path, "test-set.zip")
        get_file(TEST_CSV_URL, self.path, "GT-final_test.csv.zip")


    def _extract(self, **kwargs):
        print("extracting training-set.zip")
        zip_ref = zipfile.ZipFile(self.training_set.path + ".zip", 'r')
        zip_ref.extractall(self.training_set.path)
        zip_ref.close()


        print("extracting test-set.zip")
        zip_ref = zipfile.ZipFile(self.test_set.path + ".zip", 'r')
        zip_ref.extractall(self.test_set.path)
        zip_ref.close()
        os.remove(self.test_set.path + "/GTSRB/Final_Test/Images/GT-final_test.test.csv")


        print("extracting GT-final_test.csv.zip")
        zip_ref = zipfile.ZipFile(self.path + "/GT-final_test.csv.zip", 'r')
        zip_ref.extract("GT-final_test.csv", self.test_set.path + "/GTSRB/Final_Test/Images")
        zip_ref.close()

        print("organizing files")
        for dir in os.listdir(self._training_images_path):
            old_dir = os.path.join(self._training_images_path, dir)
            new_dir = os.path.join(self.training_set.path, dir)

            os.rename(old_dir, new_dir)

        for dir in os.listdir(self._test_images_path):
            old_dir = os.path.join(self._test_images_path, dir)
            new_dir = os.path.join(self.test_set.path, dir)

            os.rename(old_dir, new_dir)

#training images readme
        old_dir = os.path.join(self.training_set.path, "GTSRB/Readme-Images.txt")
        new_dir = os.path.join(self.training_set.path, "Readme-Images.txt")
        os.rename(old_dir, new_dir)
        (shutil.rmtree)(os.path.join(self.training_set.path, "GTSRB"))

#training images readme
        old_dir = os.path.join(self.test_set.path, "GTSRB/Readme-Images-Final-test.txt")
        new_dir = os.path.join(self.test_set.path, "Readme-Images.txt")
        os.rename(old_dir, new_dir)
        (shutil.rmtree)(os.path.join(self.test_set.path, "GTSRB"))


    def _remove_compressed(self, **kwargs):
        print("removing compressed")
        os.remove(self.training_set.path + ".zip")
        os.remove(self.test_set.path + ".zip")
        os.remove(self.path + "/GT-final_test.csv.zip")

    def _process(self, dims="32x32", format="jpg", **kwargs):
        import os
        import sys
        from PIL import Image

        dims = dims.split('x')
        dims = tuple(map(int, dims))

        print("Image dims: {}, Image format: {}".format(dims, format))

        CLASS = None

        for root, dirs, files in os.walk(self.path):
            for file in files:
                file = os.path.join(root, file)

                if file.endswith(".ppm"):

                    new_file = file.replace(".ppm", ".{}".format(format))

                    with Image.open(file) as im :
                        im = im.resize(dims)
                        im.save(new_file, quality=100)

                    dirs = file.split("/")
                    _class = dirs[-2]

                    if _class != CLASS:
                        CLASS = _class
                        print("formating {_class}".format(_class=_class))

                elif file.endswith(".csv"):
                    with open(file, 'r') as f :
                        csv = f.read()

                    csv = csv.replace(".ppm", ".{}".format(format))

                    with open(file, 'w') as f :
                        f.write(csv)


    def _remove_raw(self, **kwargs):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                file = os.path.join(root, file)
                if file.endswith(".ppm"):
                    os.remove(file)



class SetBase(SubSet):

    def __init__(self, *args, **kwargs):
        super(SetBase, self).__init__(*args, **kwargs)
        self._dataframe = None
        self._features = None
        self._labels = None


    def _load_dataframe(self):
        if self._dataframe is None:
            import pandas as pd
            self._dataframe = pd.concat(self._dataframe_generator())
            self._dataframe["class_id"] = self._dataframe["ClassId"]
            self._dataframe["filename"] = self._dataframe["Filename"]

            del self._dataframe["ClassId"]
            del self._dataframe["Filename"]

    def dataframe(self):
        from scipy.misc import imread

        self._load_dataframe()

        if not "image" in self._dataframe:
            self._dataframe["image"] = self._dataframe.filename.apply(imread)

        return self._dataframe


    def arrays(self):
        import numpy as np

        if self._features is None or self._labels is None:
            dataframe = self.dataframe()

            self._features = np.stack(dataframe.image.as_matrix())
            self._labels = np.stack(dataframe.class_id.as_matrix())

        return self._features, self._labels


    def random_batch_dataframe_generator(self, batch_size):
        from scipy.misc import imread

        self._load_dataframe()

        while True:
            batch = self._dataframe.sample(batch_size)

            if not "image" in batch:
                batch["image"] = batch.filename.apply(imread)

            yield batch


    def random_batch_arrays_generator(self, batch_size):
        import numpy as np

        for data in self.random_batch_dataframe_generator(batch_size):
            features = np.stack(data.image.as_matrix())
            labels = np.stack(data.class_id.as_matrix())

            yield features, labels


class TestGermanTrafficSignsDataset(SetBase):

    def __init__(self, dataset):
        super(TestGermanTrafficSignsDataset, self).__init__(dataset, "test-set")

    def _dataframe_generator(self):
        import pandas as pd
        csv_path = csv_path = os.path.join(self.path, "GT-final_test.csv")

        df = pd.read_csv(csv_path, sep=";")
        df['Filename'] = self.path + "/" + df['Filename']

        yield df




class TrainingGermanTrafficSignsDataset(SetBase):

    def __init__(self, dataset):
        super(TrainingGermanTrafficSignsDataset, self).__init__(dataset, "training-set")


    def _dataframe_generator(self):
        import pandas as pd

        for cls_string in os.listdir(self.path):
            if (os.path.isdir)(os.path.join(self.path, cls_string)):
                csv_path = (_coconut.functools.partial(os.path.join, self.path))("{0}/GT-{0}.csv".format(cls_string))

                df = pd.read_csv(csv_path, sep=";")
                df['Filename'] = os.path.join(self.path, cls_string) + "/" + df['Filename']

                yield df