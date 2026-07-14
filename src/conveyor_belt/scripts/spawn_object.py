#!/usr/bin/env python3
"""
spawn_object.py  –  Gazebo Harmonic version

Spawns a box into Gazebo using ros_gz_sim's create executable.
"""

import argparse
import os
import sys
import random
import subprocess
import xacro
import tempfile

from ament_index_python.packages import get_package_share_directory

VARIANT_MESH_URIS = {
    'default': 'package://conveyor_belt/meshes/box/box.dae',
    'box1': 'package://conveyor_belt/meshes/variants/box1/box.dae',
    'box2': 'package://conveyor_belt/meshes/variants/box2/box.dae',
    'box3': 'package://conveyor_belt/meshes/variants/box3/box.dae',
    'box4': 'package://conveyor_belt/meshes/variants/box4/box.dae',
    'box5': 'package://conveyor_belt/meshes/variants/box5/box.dae',
    'box6': 'package://conveyor_belt/meshes/variants/box6/box.dae',
    'img0554': 'package://conveyor_belt/meshes/variants/img0554/box.dae',
    'img0583': 'package://conveyor_belt/meshes/variants/img0583/box.dae',
    'img0641': 'package://conveyor_belt/meshes/variants/img0641/box.dae',
    'img0771': 'package://conveyor_belt/meshes/variants/img0771/box.dae',
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--x', default='2.0')
    parser.add_argument('--y', default='0.0')
    parser.add_argument('--z', default='1.5')
    parser.add_argument('--R', default='0.0')
    parser.add_argument('--P', default='0.0')
    parser.add_argument('--Y', default='0.0')
    parser.add_argument('--name', default='')
    parser.add_argument('--variant', default='default')
    args, _unknown = parser.parse_known_args()
    return args


def main():
    args = parse_args()
    pkg = get_package_share_directory('conveyor_belt')
    xacro_path = os.path.join(pkg, 'urdf', 'box.urdf.xacro')

    print(f'Processing xacro: {xacro_path}')
    mesh_uri = VARIANT_MESH_URIS.get(args.variant)
    if mesh_uri is None:
        print(
            f'Unknown variant "{args.variant}". '
            f'Available: {", ".join(sorted(VARIANT_MESH_URIS))}',
            file=sys.stderr,
        )
        sys.exit(1)

    robot_desc = xacro.process_file(
        xacro_path,
        mappings={'mesh_uri': mesh_uri},
    )
    xml_string = robot_desc.toxml()

    # Write URDF to a temp file — ros_gz_sim create needs a file path
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.urdf', delete=False
    ) as f:
        f.write(xml_string)
        tmp_path = f.name

    entity_name = args.name or (f'{args.variant}_' + str(random.randint(0, 9999)))

    print(f'Spawning entity: {entity_name}')

    result = subprocess.run([
        'ros2', 'run', 'ros_gz_sim', 'create',
        '-name', entity_name,
        '-file', tmp_path,
        '-x', args.x,
        '-y', args.y,
        '-z', args.z,
        '-R', args.R,
        '-P', args.P,
        '-Y', args.Y,
    ], capture_output=False)

    os.unlink(tmp_path)

    if result.returncode == 0:
        print(f'Box "{entity_name}" spawned successfully.')
    else:
        print(f'Failed to spawn box. Return code: {result.returncode}')
        sys.exit(1)


if __name__ == '__main__':
    main()
