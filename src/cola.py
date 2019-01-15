# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

'''
CoLA - binary classification
'''

from __future__ import absolute_import, division, unicode_literals

import os
import codecs
import logging
import numpy as np

from src.tools.validation import SplitClassifier


class CoLAEval(object):
    def __init__(self, task_path, seed=1111):
        self.seed = seed

        logging.debug('***** Transfer task : CoLA classification *****\n\n')

        trainsentence = self.loadFile(os.path.join(task_path, 'sentences.train'))
        devsentence = self.loadFile(os.path.join(task_path, 'sentences.dev'))
        trainlabel = self.loadFile(os.path.join(task_path, 'labels.train'), label=True)
        devlabel = self.loadFile(os.path.join(task_path, 'labels.dev'), label=True)

        testsentence = self.loadFile(os.path.join(task_path, 'sentences.test'))

        self.sst_data = {'train': {'X': trainsentence, 'y': trainlabel},
                         'dev': {'X': devsentence, 'y': devlabel},
                         'test': {'X': testsentence}}

    def do_prepare(self, params, prepare):
        samples = self.sst_data['train']['X'] + self.sst_data['dev']['X'] \
                  + self.sst_data['test']['X']
        return prepare(params, samples)

    def loadFile(self, fpath, label=False):
        with codecs.open(fpath, 'rb', 'latin-1') as f:
            if label:
                return [int(line) for line in f.read().splitlines()]
            else:
                return [line.split() for line in f.read().splitlines()]

    def run(self, params, batcher):
        sst_embed = {'train': {}, 'dev': {}, 'test': {}}
        bsize = params.batch_size

        for key in self.sst_data:
            logging.info('Computing embedding for {0}'.format(key))
            # Sort to reduce padding
            if key != 'test':
                sorted_data = sorted(zip(self.sst_data[key]['X'],
                                         self.sst_data[key]['y']),
                                     key=lambda z: (len(z[0]), z[1]))
                self.sst_data[key]['X'], self.sst_data[key]['y'] = map(list, zip(*sorted_data))

            sst_embed[key]['X'] = []
            for ii in range(0, len(self.sst_data[key]['X']), bsize):
                batch = self.sst_data[key]['X'][ii:ii + bsize]
                embeddings = batcher(params, batch)
                sst_embed[key]['X'].append(embeddings)
            sst_embed[key]['X'] = np.vstack(sst_embed[key]['X'])
            if key != 'test':
                sst_embed[key]['y'] = np.array(self.sst_data[key]['y'])
            logging.info('Computed {0} embeddings'.format(key))

        config_classifier = {'nclasses': 2, 'seed': self.seed,
                             'usepytorch': params.usepytorch,
                             'classifier': params.classifier}

        clf = SplitClassifier(X={'train': sst_embed['train']['X'],
                                 'valid': sst_embed['dev']['X'],
                                 'test': sst_embed['test']},
                              y={'train': sst_embed['train']['y'],
                                 'valid': sst_embed['dev']['y']},
                              config=config_classifier,
                              matthews=True,
                              test="CoLA")

        devacc = clf.run()
        logging.debug('\nDev Matthews correlation : {0}  for \
            CoLA classification\n'.format(devacc))

        return {'devacc': devacc,
                'ndev': len(sst_embed['dev']['X'])}