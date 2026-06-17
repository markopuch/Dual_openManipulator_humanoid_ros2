# Dual_openManipulator_humanoid_ros2

Workspace local para simulaciones ROS 2 Humble/Gazebo Classic con OpenMANIPULATOR-X.

## Paquetes locales

- `dual_openmanipulator`: paquete base con dos OpenMANIPULATOR-X.
- `dual_openmanipulator_vslot_sim`: simulacion nueva con dos OpenMANIPULATOR-X montados sobre un bastidor V-slot 60x60, fixtures de prototipo y configuracion MoveIt en una sola interfaz.

## Simulacion V-slot

Compilar desde `/home/utec/robotis_ws`:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to dual_openmanipulator_vslot_sim
source install/setup.bash
```

Lanzar Gazebo:

```bash
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_gazebo.launch.py
```

Lanzar MoveIt/RViz en otra terminal:

```bash
source /opt/ros/humble/setup.bash
source /home/utec/robotis_ws/install/setup.bash
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_moveit.launch.py
```

En RViz se puede seleccionar `left_arm`, `right_arm` o `both_arms` para mover los brazos de forma individual o simultanea.

La referencia visual usada para el bastidor esta en `referencia/ffecce71-3056-4589-a7c7-72426ed2470d.png`.
