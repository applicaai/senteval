# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

'''
NLI - Entailment
'''
from __future__ import absolute_import, division, unicode_literals

import codecs
import os
import io
import copy
import logging
import numpy as np

from src.tools.validation import SplitClassifier


class NLIEval(object):
    def __init__(self, taskpath, name, seed=1111):
        self.seed = seed
        self.name = name
        self.X = {}
        self.y = {}

        train1 = self.load_file(os.path.join(taskpath, 's1.train'))
        train2 = self.load_file(os.path.join(taskpath, 's2.train'))

        trainlabels = io.open(os.path.join(taskpath, 'labels.train'),
                              encoding='utf-8').read().splitlines()

        valid1 = self.load_file(os.path.join(taskpath, 's1.dev'))
        valid2 = self.load_file(os.path.join(taskpath, 's2.dev'))
        validlabels = io.open(os.path.join(taskpath, 'labels.dev'),
                              encoding='utf-8').read().splitlines()

        test1 = self.load_file(os.path.join(taskpath, 's1.test'))
        test2 = self.load_file(os.path.join(taskpath, 's2.test'))

        # sort data (by s2 first) to reduce padding
        sorted_train = sorted(zip(train2, train1, trainlabels),
                              key=lambda z: (len(z[0]), len(z[1]), z[2]))
        train2, train1, trainlabels = map(list, zip(*sorted_train))

        sorted_valid = sorted(zip(valid2, valid1, validlabels),
                              key=lambda z: (len(z[0]), len(z[1]), z[2]))
        valid2, valid1, validlabels = map(list, zip(*sorted_valid))

        self.samples = train1 + train2 + valid1 + valid2 + test1 + test2
        self.data = {'train': (train1, train2, trainlabels),
                     'valid': (valid1, valid2, validlabels),
                     'test': (test1, test2)
                     }

    def do_prepare(self, params, prepare):
        return prepare(params, self.samples)

    @staticmethod
    def load_file(fpath):
        with codecs.open(fpath, 'rb', 'latin-1') as f:
            return [line.split() for line in
                    f.read().splitlines()]

    def run(self, params, batcher):

        if self.name in {"RTE", "QNLI"}:
            dico_label = {'entailment': 0,  'not_entailment': 1}
        elif self.name in {"QQP", "WNLI"}:
            dico_label = {'0': 0,  '1': 1}
        elif self.name in {"SNLI", "MNLI-m", "MNLI-mm"}:
            dico_label = {'entailment': 0,  'neutral': 1, 'contradiction': 2}

        for key in self.data:
            logging.info(f"Encoding {key} set for {self.name}...")
            if key not in self.X:
                self.X[key] = []
            if key not in self.y:
                self.y[key] = []

            if len(self.data[key]) == 3:
                input1, input2, mylabels = self.data[key]
            else:
                input1, input2 = self.data[key]
            enc_input = []
            n_data = len(input1)
            for ii in range(0, n_data, params.batch_size):
                batch1 = input1[ii:ii + params.batch_size]
                batch2 = input2[ii:ii + params.batch_size]

                if len(batch1) == len(batch2) and len(batch1) > 0:
                    enc1 = batcher(params, batch1)
                    enc2 = batcher(params, batch2)
                    enc_input.append(np.hstack((enc1, enc2, enc1 * enc2,
                                                np.abs(enc1 - enc2))))
            self.X[key] = np.vstack(enc_input)
            if len(self.data[key]) == 3:
                self.y[key] = np.array([dico_label[y] for y in mylabels])

        if self.name in {"SNLI", "MNLI-m", "MNLI-mm"}:
            nclasses = 3
        else:
            nclasses = 2

        config = {'nclasses': nclasses, 'seed': self.seed,
                  'usepytorch': params.usepytorch,
                  'cudaEfficient': True,
                  'nhid': params.nhid, 'noreg': True}

        config_classifier = copy.deepcopy(params.classifier)
        config_classifier['max_epoch'] = 15
        config_classifier['epoch_size'] = 1
        config['classifier'] = config_classifier

        clf = SplitClassifier(self.X, self.y, config, test=self.name)
        devacc = clf.run()
        logging.debug(f'Dev acc : {devacc} for {self.name}\n')
        return {'dev_score': devacc,
                'ndev': len(self.data['valid'][0])}


class QNLIEval(NLIEval):
    def __init__(self, taskpath, seed=1111):
        super().__init__(taskpath, name='QNLI', seed=seed)


class QQPEval(NLIEval):
    def __init__(self, taskpath, seed=1111):
        super().__init__(taskpath, name='QQP', seed=seed)


class RTEEval(NLIEval):
    def __init__(self, taskpath, seed=1111):
        super().__init__(taskpath, name='RTE', seed=seed)


class WNLIEval(NLIEval):
    def __init__(self, taskpath, seed=1111):
        super().__init__(taskpath, name='WNLI', seed=seed)


class MNLIMEval(NLIEval):
    def __init__(self, taskpath, seed=1111):
        super().__init__(taskpath, name='MNLI-m', seed=seed)


class MNLIMMEval(NLIEval):
    def __init__(self, taskpath, seed=1111):
        super().__init__(taskpath, name='MNLI-mm', seed=seed)


class SNLIEval(object):
    def __init__(self, taskpath, seed=1111):
        self.seed = seed
        train1 = self.load_file(os.path.join(taskpath, 's1.train'))
        train2 = self.load_file(os.path.join(taskpath, 's2.train'))

        trainlabels = io.open(os.path.join(taskpath, 'labels.train'),
                              encoding='utf-8').read().splitlines()

        valid1 = self.load_file(os.path.join(taskpath, 's1.dev'))
        valid2 = self.load_file(os.path.join(taskpath, 's2.dev'))
        validlabels = io.open(os.path.join(taskpath, 'labels.dev'),
                              encoding='utf-8').read().splitlines()

        test1 = self.load_file(os.path.join(taskpath, 's1.test'))
        test2 = self.load_file(os.path.join(taskpath, 's2.test'))
        testlabels = io.open(os.path.join(taskpath, 'labels.test'),
                             encoding='utf-8').read().splitlines()

        # sort data (by s2 first) to reduce padding
        sorted_train = sorted(zip(train2, train1, trainlabels),
                              key=lambda z: (len(z[0]), len(z[1]), z[2]))
        train2, train1, trainlabels = map(list, zip(*sorted_train))

        sorted_valid = sorted(zip(valid2, valid1, validlabels),
                              key=lambda z: (len(z[0]), len(z[1]), z[2]))
        valid2, valid1, validlabels = map(list, zip(*sorted_valid))

        sorted_test = sorted(zip(test2, test1, testlabels),
                             key=lambda z: (len(z[0]), len(z[1]), z[2]))
        test2, test1, testlabels = map(list, zip(*sorted_test))

        self.samples = train1 + train2 + valid1 + valid2 + test1 + test2
        self.data = {'train': (train1, train2, trainlabels),
                     'valid': (valid1, valid2, validlabels),
                     'test': (test1, test2, testlabels)
                     }

    def do_prepare(self, params, prepare):
        return prepare(params, self.samples)

    @staticmethod
    def load_file(fpath):
        with codecs.open(fpath, 'rb', 'latin-1') as f:
            return [line.split() for line in
                    f.read().splitlines()]

    def run(self, params, batcher):
        self.X, self.y = {}, {}
        dico_label = {'entailment': 0,  'neutral': 1, 'contradiction': 2}
        for key in self.data:
            logging.info(f"Encoding {key} set for SNLI...")
            if key not in self.X:
                self.X[key] = []
            if key not in self.y:
                self.y[key] = []

            input1, input2, mylabels = self.data[key]
            enc_input = []
            n_labels = len(mylabels)
            for ii in range(0, n_labels, params.batch_size):
                batch1 = input1[ii:ii + params.batch_size]
                batch2 = input2[ii:ii + params.batch_size]

                if len(batch1) == len(batch2) and len(batch1) > 0:
                    enc1 = batcher(params, batch1)
                    enc2 = batcher(params, batch2)
                    enc_input.append(np.hstack((enc1, enc2, enc1 * enc2,
                                                np.abs(enc1 - enc2))))
            self.X[key] = np.vstack(enc_input)
            self.y[key] = np.array([dico_label[y] for y in mylabels])

        config = {'nclasses': 3, 'seed': self.seed,
                  'usepytorch': params.usepytorch,
                  'cudaEfficient': True,
                  'nhid': params.nhid, 'noreg': True}

        config_classifier = copy.deepcopy(params.classifier)
        config_classifier['max_epoch'] = 15
        config_classifier['epoch_size'] = 1
        config['classifier'] = config_classifier

        clf = SplitClassifier(self.X, self.y, config)
        devacc, testacc = clf.run()
        logging.debug(f'Dev acc : {devacc} Test acc : {testacc} for SNLI\n')
        return {'dev_score': devacc, 'test_score': testacc,
                'ndev': len(self.data['valid'][0]),
                'ntest': len(self.data['test'][0])}
