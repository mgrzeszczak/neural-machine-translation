#!/usr/bin/env python3

import argparse
import logging

import tensorflow as tf

from model import TranslatorModel
from utils import prepare_sentence, light_prepare


def parse_arguments():
    parser = argparse.ArgumentParser(description='Neural machine translation')
    parser.add_argument('--src-vocab', type=str, help='location of src vocabulary', required=True)
    parser.add_argument('--dst-vocab', type=str, help='location of dst vocabulary', required=True)

    parser.add_argument('--model-dir', type=str, help='location of the model', required=True)
    parser.add_argument('--mode', type=str, help='program mode', default='TRAIN', choices=['TRAIN', 'REPL', 'BLEU'])

    parser.add_argument('--src-train-data', type=str, help='location of src train data file')
    parser.add_argument('--dst-train-data', type=str, help='location of dst train data file')

    parser.add_argument('--src-validation-data', type=str, help='location of src validation data file')
    parser.add_argument('--dst-validation-data', type=str, help='location of dst validation data file')

    parser.add_argument('--src-predict-data', type=str, help='location of src predict data file')
    parser.add_argument('--dst-predict-data', type=str, help='location of dst predict data file')

    parser.add_argument('--cell-units', type=int, default=1024, help='number of cell units')
    parser.add_argument('--embedding-size', type=int, default=300, help='embedding size')
    parser.add_argument('--max-sentence-length', type=int, default=39, help='max sentence length')
    parser.add_argument('--batch-size', type=int, default=128, help='batch size')
    parser.add_argument('--beam-width', type=int, default=None, help='decoder beam width (disabled by default)')

    args = parser.parse_args()

    if args.mode == 'TRAIN':
        if args.src_train_data is None or args.dst_train_data is None:
            parser.error('src-train-data and dst-train-data are required when mode = TRAIN')
        if args.src_predict_data is None or args.dst_predict_data is None:
            parser.error('src-predict-data and dst-predict-data are required when mode = TRAIN')
        if args.src_validation_data is None or args.dst_validation_data is None:
            parser.error(
                'src-validation-data and dst-validation-data are required when mode = TRAIN')

    if args.mode == 'BLEU':
        if args.src_validation_data is None or args.dst_validation_data is None:
            parser.error('src-validation-data and dst-validation-data are required when mode = BLEU')
    if args.beam_width == 0:
        args.beam_width = None
    return args


def main():
    # tf.logging._logger.setLevel(logging.INFO)
    config = tf.estimator.RunConfig(
        save_summary_steps=100,
        session_config=None,
        keep_checkpoint_max=1,
        keep_checkpoint_every_n_hours=10000,
        log_step_count_steps=100
    )
    args = parse_arguments()
    translator = TranslatorModel(args, config)
    if args.mode == 'TRAIN':
        translator.train(10)
    elif args.mode == 'BLEU':
        print('BLEU = {}'.format(translator.calculate_bleu(args.src_validation_data, args.dst_validation_data)[0]))
    else:
        try:
            while 1:
                sentence = ' '.join(light_prepare(input('>> ')))
                for src, translation in translator.translate([sentence]):
                    print(translation)
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    main()
