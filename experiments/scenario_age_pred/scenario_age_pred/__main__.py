import argparse
import logging

if __name__ == '__main__':
    import sys
    sys.path.append('../../')

    from dltranz.util import switch_reproducibility_on
    switch_reproducibility_on()

from scenario_age_pred import fit_target, pseudo_labeling, fit_finetuning
from scenario_age_pred import compare_approaches

logger = logging.getLogger(__name__)


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    for module in [compare_approaches, fit_target, fit_finetuning, pseudo_labeling]:
        sub_parser = subparsers.add_parser(module.__name__.split('.')[-1])
        sub_parser.set_defaults(func=module.main)
        module.prepare_parser(sub_parser)

    config, _ = parser.parse_known_args(args)
    return vars(config)


if __name__ == '__main__':
    conf = parse_args()
    if 'func' not in conf:
        print('Choose scenario. Use --help for more information')
        exit(-1)

    conf['func'](conf)
