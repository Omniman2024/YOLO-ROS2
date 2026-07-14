# ME222 Warehouse Simulation Workspace

This is a standard ROS 2 workspace.

```text
exp/
  src/
    warehouse_simulation/
      package.xml
      CMakeLists.txt
      launch/
      models/
      worlds/
```

## Build

```bash
source /opt/ros/jazzy/setup.bash
colcon build --packages-select warehouse_simulation
source install/setup.bash
```

## Run

```bash
ros2 launch warehouse_simulation warehouse_environment.launch.py
```

## After Editing

Because this workspace uses a normal copied install, rebuild after changing launch
files, worlds, models, or assets:

```bash
colcon build --packages-select warehouse_simulation
source install/setup.bash
```
