#!/usr/bin/env python3
"""
Spawn a URDF/Xacro model into Gazebo Harmonic as a named entity.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time

import xacro
from ament_index_python.packages import get_package_share_directory


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True, help='URDF/Xacro filename in share/<pkg>/urdf')
    parser.add_argument('--name', required=True, help='Entity name in Gazebo')
    parser.add_argument(
        '--xacro-arg',
        action='append',
        default=[],
        help='Xacro mapping in the form key:=value',
    )
    parser.add_argument('--x', default='0.0')
    parser.add_argument('--y', default='0.0')
    parser.add_argument('--z', default='0.0')
    parser.add_argument('--R', default='0.0')
    parser.add_argument('--P', default='0.0')
    parser.add_argument('--Y', default='0.0')
    args, _unknown = parser.parse_known_args()
    return args


def main():
    args = parse_args()
    pkg = get_package_share_directory('conveyor_belt')
    xacro_path = os.path.join(pkg, 'urdf', args.model)

    if not os.path.exists(xacro_path):
      print(f'Model file not found: {xacro_path}', file=sys.stderr)
      sys.exit(1)

    mappings = {}
    for raw_mapping in args.xacro_arg:
        if ':=' not in raw_mapping:
            print(f'Invalid --xacro-arg value: {raw_mapping}', file=sys.stderr)
            sys.exit(1)
        key, value = raw_mapping.split(':=', 1)
        mappings[key] = value

    xml_string = xacro.process_file(xacro_path, mappings=mappings).toxml()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False) as f:
        f.write(xml_string)
        tmp_path = f.name

    try:
        result = subprocess.run([
            'ros2', 'run', 'ros_gz_sim', 'create',
            '-name', args.name,
            '-file', tmp_path,
            '-x', args.x,
            '-y', args.y,
            '-z', args.z,
            '-R', args.R,
            '-P', args.P,
            '-Y', args.Y,
        ], check=False)
        # Gazebo may read the file shortly after the create command returns.
        time.sleep(2.0)
    finally:
        os.unlink(tmp_path)

    if result.returncode != 0:
        sys.exit(result.returncode)


if __name__ == '__main__':
    main()
