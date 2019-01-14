#!/usr/bin/env bash
# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

data_path=.
preprocess_exec=./tokenizer.sed

PTBTOKENIZER="sed -f tokenizer.sed"

python download_glue_data.py --data_dir $data_path


### process QNLI
for split in train dev test
do
    fpath=$data_path/QNLI/$split.txt
    cat $data_path/QNLI/$split.tsv | cut -f 2,3,4 | sed '1d' > $fpath
    cut -f1 $fpath | $PTBTOKENIZER > $data_path/QNLI/s1.$split
    cut -f2 $fpath | $PTBTOKENIZER > $data_path/QNLI/s2.$split
    cut -f3 $fpath > $data_path/QNLI/labels.$split
    rm $fpath
done
rm -r $data_path/QNLI/*.tsv


### process MNLI
fpath=$data_path/MNLI/train.txt
awk '{ if ( $15 != "-" ) { print $0; } }' $data_path/MNLI/train.tsv | cut -f 9,10,12 | sed '1d' > $fpath
cut -f1 $fpath | $PTBTOKENIZER > $data_path/MNLI/s1.train
cut -f2 $fpath | $PTBTOKENIZER > $data_path/MNLI/s2.train
cut -f3 $fpath > $data_path/MNLI/labels.train
rm $fpath
for split in dev_matched dev_mismatched
do
    fpath=$data_path/MNLI/$split.txt
    awk '{ if ( $15 != "-" ) { print $0; } }' $data_path/MNLI/$split.tsv | cut -f 9,10,16 | sed '1d' > $fpath
    cut -f1 $fpath | $PTBTOKENIZER > $data_path/MNLI/s1.$split
    cut -f2 $fpath | $PTBTOKENIZER > $data_path/MNLI/s2.$split
    cut -f3 $fpath > $data_path/MNLI/labels.$split
    rm $fpath
done
for split in test_matched test_mismatched
do
    fpath=$data_path/MNLI/$split.txt
    awk '{ if ( $15 != "-" ) { print $0; } }' $data_path/MNLI/$split.tsv | cut -f 9,10 | sed '1d' > $fpath
    cut -f1 $fpath | $PTBTOKENIZER > $data_path/MNLI/s1.$split
    cut -f2 $fpath | $PTBTOKENIZER > $data_path/MNLI/s2.$split
    rm $fpath
done
rm -r $data_path/MNLI/*.tsv
rm -r $data_path/MNLI/original
rm -r $data_path/MNLI/README.txt


### process QQP
sed -i '18285d' $data_path/QQP/dev.tsv
sed -i '36734d;37885d;83114d;97931d;112415d;130312d;131597d;136146d;139218d;154867d;189974d;195314d;210045d;228831d;300907d;304584d;313478d;324460d;329265d;345531d;355943d' $data_path/QQP/train.tsv
for split in train dev
do
    fpath=$data_path/QQP/$split.txt
    cat $data_path/QQP/$split.tsv | cut -f 4,5,6 | sed '1d' > $fpath
    cut -f1 $fpath | $PTBTOKENIZER > $data_path/QQP/s1.$split
    cut -f2 $fpath | $PTBTOKENIZER > $data_path/QQP/s2.$split
    cut -f3 $fpath > $data_path/QQP/labels.$split
    rm $fpath
done

fpath=$data_path/QQP/test.txt
cat $data_path/QQP/test.tsv | cut -f 2,3 | sed '1d' > $fpath
cut -f1 $fpath | $PTBTOKENIZER > $data_path/QQP/s1.test
cut -f2 $fpath | $PTBTOKENIZER > $data_path/QQP/s2.test
rm $fpath

rm -r $data_path/QQP/*.tsv
rm -r $data_path/QQP/original


### process RTE
for split in train dev
do
    fpath=$data_path/RTE/$split.txt
    cat $data_path/RTE/$split.tsv | cut -f 2,3,4 | sed '1d' > $fpath
    cut -f1 $fpath | $PTBTOKENIZER > $data_path/RTE/s1.$split
    cut -f2 $fpath | $PTBTOKENIZER > $data_path/RTE/s2.$split
    cut -f3 $fpath > $data_path/RTE/labels.$split
    rm $fpath
done
fpath=$data_path/RTE/test.txt
cat $data_path/RTE/test.tsv | cut -f 2,3 | sed '1d' > $fpath
cut -f1 $fpath | $PTBTOKENIZER > $data_path/RTE/s1.test
cut -f2 $fpath | $PTBTOKENIZER > $data_path/RTE/s2.test
rm $fpath
rm -r $data_path/RTE/*.tsv


### process WNLI
for split in train dev
do
    fpath=$data_path/WNLI/$split.txt
    cat $data_path/WNLI/$split.tsv | cut -f 2,3,4 | sed '1d' > $fpath
    cut -f1 $fpath | $PTBTOKENIZER > $data_path/WNLI/s1.$split
    cut -f2 $fpath | $PTBTOKENIZER > $data_path/WNLI/s2.$split
    cut -f3 $fpath > $data_path/WNLI/labels.$split
    rm $fpath
done
fpath=$data_path/WNLI/test.txt
cat $data_path/WNLI/test.tsv | cut -f 2,3 | sed '1d' > $fpath
cut -f1 $fpath | $PTBTOKENIZER >C $data_path/WNLI/s1.test
cut -f2 $fpath | $PTBTOKENIZER > $data_path/WNLI/s2.test
rm $fpath
rm -r $data_path/WNLI/*.tsv


### process CoLA
for split in train dev
do
    fpath=$data_path/CoLA/$split.txt
    cat $data_path/CoLA/$split.tsv | cut -f 2,4 | sed '1d' > $fpath
    cut -f1 $fpath > $data_path/CoLA/labels.$split
    cut -f2 $fpath | $PTBTOKENIZER > $data_path/CoLA/sentences.$split
    rm $fpath
done
fpath=$data_path/CoLA/test.txt
cat $data_path/CoLA/test.tsv | cut -f 2 | sed '1d' > $fpath
cut -f1 $fpath | $PTBTOKENIZER > $data_path/CoLA/sentences.test
rm $fpath
rm -r $data_path/CoLA/*.tsv



