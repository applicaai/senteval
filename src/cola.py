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

        self.sst_data = {'train': {'X': trainsentence, 'y': trainlabel},
                         'dev': {'X': devsentence, 'y': devlabel}}

    def do_prepare(self, params, prepare):
        samples = self.sst_data['train']['X'] + self.sst_data['dev']['X']
        return prepare(params, samples)

    def loadFile(self, fpath, label=False):
        with codecs.open(fpath, 'rb', 'latin-1') as f:
            if label:
                return [int(line) for line in f.read().splitlines()]
            else:
                return [line.split() for line in f.read().splitlines()]

    def run(self, params, batcher):
        sst_embed = {'train': {}, 'dev': {}}
        bsize = params.batch_size

        for key in self.sst_data:
            logging.info('Computing embedding for {0}'.format(key))
            # Sort to reduce padding
            sorted_data = sorted(zip(self.sst_data[key]['X'],
                                     self.sst_data[key]['y']),
                                 key=lambda z: (len(z[0]), z[1]))
            self.sst_data[key]['X'], self.sst_data[key]['y'] = map(list, zip(*sorted_data))

            sst_embed[key]['X'] = []
            for ii in range(0, len(self.sst_data[key]['y']), bsize):
                batch = self.sst_data[key]['X'][ii:ii + bsize]
                embeddings = batcher(params, batch)
                sst_embed[key]['X'].append(embeddings)
            sst_embed[key]['X'] = np.vstack(sst_embed[key]['X'])
            sst_embed[key]['y'] = np.array(self.sst_data[key]['y'])
            logging.info('Computed {0} embeddings'.format(key))

        config_classifier = {'nclasses': 2, 'seed': self.seed,
                             'usepytorch': params.usepytorch,
                             'classifier': params.classifier}

        clf = SplitClassifier(X={'train': sst_embed['train']['X'],
                                 'valid': sst_embed['dev']['X']},
                              y={'train': sst_embed['train']['y'],
                                 'valid': sst_embed['dev']['y']},
                              config=config_classifier,
                              matthews=True,
                              test=False)

        devacc = clf.run()
        logging.debug('\nDev Matthews correlation : {0}  for \
            CoLA classification\n'.format(devacc))

        return {'devacc': devacc,
                'ndev': len(sst_embed['dev']['X'])}

# # Copyright (c) 2017-present, Facebook, Inc.
# # All rights reserved.
# #
# # This source code is licensed under the license found in the
# # LICENSE file in the root directory of this source tree.
# #
#
# '''
# Binary classifier and corresponding datasets : MR, CR, SUBJ, MPQA
# '''
# from __future__ import absolute_import, division, unicode_literals
#
# import io
# import os
# import numpy as np
# import logging
#
# from senteval.tools.validation import InnerKFoldClassifier
#
#
# class CoLAEval(object):
#     def __init__(self, task_path, seed=1111):
#         logging.debug('***** Transfer task : CoLA *****\n\n')
#         self.samples = self.loadFile(os.path.join(task_path, 'sentences.train'))
#         valid = self.loadFile(os.path.join(task_path, 'sentences.dev'))
#         self.labels = self.loadFile(os.path.join(task_path, 'labels.train'), label=True)
#         validlabels = self.loadFile(os.path.join(task_path, 'labels.dev'), label=True)
#
#         print(valid)
#         print(validlabels)
#
#         self.seed = seed
#         # self.samples, self.labels = pos + neg, [1] * len(pos) + [0] * len(neg)
#         self.n_samples = len(self.samples)
#
#     def do_prepare(self, params, prepare):
#         # prepare is given the whole text
#         return prepare(params, self.samples)
#         # prepare puts everything it outputs in "params" : params.word2id etc
#         # Those output will be further used by "batcher".
#
#     def loadFile(self, fpath, label=False):
#         with io.open(fpath, 'r', encoding='latin-1') as f:
#             if label:
#                 return [int(line) for line in f.read().splitlines()]
#
#             else:
#                 return [line.split() for line in f.read().splitlines()]
#
#     def run(self, params, batcher):
#         enc_input = []
#         # Sort to reduce padding
#         sorted_corpus = sorted(zip(self.samples, self.labels),
#                                key=lambda z: (len(z[0]), z[1]))
#         sorted_samples = [x for (x, y) in sorted_corpus]
#         sorted_labels = [y for (x, y) in sorted_corpus]
#         logging.info('Generating sentence embeddings')
#         for ii in range(0, self.n_samples, params.batch_size):
#             batch = sorted_samples[ii:ii + params.batch_size]
#             embeddings = batcher(params, batch)
#             enc_input.append(embeddings)
#         enc_input = np.vstack(enc_input)
#         logging.info('Generated sentence embeddings')
#
#         config = {'nclasses': 2, 'seed': self.seed,
#                   'usepytorch': params.usepytorch,
#                   'classifier': params.classifier,
#                   'nhid': params.nhid, 'kfold': params.kfold}
#         clf = InnerKFoldClassifier(enc_input, np.array(sorted_labels), config)
#         devacc, testacc = clf.run()
#         logging.debug('Dev acc : {0} Test acc : {1}\n'.format(devacc, testacc))
#         return {'devacc': devacc, 'acc': testacc, 'ndev': self.n_samples,
#                 'ntest': self.n_samples}
#
