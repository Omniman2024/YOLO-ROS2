#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time


VARIANT_SEQUENCE = [
    'default',
    'box4',
    'box2',
    'box5',
    'box6',
    'box1',
    'box3',
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--x', default='2.0')
    parser.add_argument('--y', default='0.0')
    parser.add_argument('--z', default='1.5')
    parser.add_argument('--R', default='0.0')
    parser.add_argument('--P', default='0.0')
    parser.add_argument('--Y', default='0.0')
    parser.add_argument('--interval', default='10.0')
    return parser.parse_args()


def main():
    args = parse_args()
    interval_sec = float(args.interval)

    for index, variant in enumerate(VARIANT_SEQUENCE):
        entity_name = f'{variant}_{index + 1:02d}'
        result = subprocess.run(
            [
                'ros2',
                'run',
                'conveyor_belt',
                'spawn_object.py',
                '--variant',
                variant,
                '--name',
                entity_name,
                '--x',
                args.x,
                '--y',
                args.y,
                '--z',
                args.z,
                '--R',
                args.R,
                '--P',
                args.P,
                '--Y',
                args.Y,
            ],
            check=False,
        )
        if result.returncode != 0:
            sys.exit(result.returncode)

        if index != len(VARIANT_SEQUENCE) - 1:
            time.sleep(interval_sec)


if __name__ == '__main__':
    main()
