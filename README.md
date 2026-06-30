# Dual_openManipulator_humanoid_ros2

Workspace local para simulaciones ROS 2 Humble/Gazebo Classic con OpenMANIPULATOR-X.
El repositorio contiene iteraciones para un prototipo bimanual universitario: dos brazos
OpenMANIPULATOR-X sobre una estructura de aluminio, con control independiente o conjunto.

## Paquetes locales

- `dual_openmanipulator`: paquete base con dos OpenMANIPULATOR-X.
- `dual_openmanipulator_vslot_sim`: simulacion nueva con dos OpenMANIPULATOR-X montados sobre un bastidor V-slot 60x60, fixtures de prototipo y configuracion MoveIt en una sola interfaz.
- `bimanual_setup_description`: paquete nuevo y modular de descripcion/simulacion del prototipo bimanual segun la referencia `referencia/Gemini_Generated_Image_vipksvvipksvvipk.png`. Incluye marco estructural, placas atornilladas, fixture, camara y controladores `ros2_control`.

## Preparacion del workspace

Desde `/home/utec/robotis_ws`:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Para compilar solo el paquete nuevo:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to bimanual_setup_description
source install/setup.bash
```

## Prototipo bimanual nuevo

El paquete recomendado para la nueva iteracion es `bimanual_setup_description`.

Lanzar Gazebo Classic con controladores independientes:

```bash
ros2 launch bimanual_setup_description spawn_bimanual.launch.py
```

Lanzar Gazebo Classic con un controlador conjunto para ambos brazos:

```bash
ros2 launch bimanual_setup_description spawn_bimanual.launch.py use_combined_controller:=true
```

Controladores disponibles:

- `left_arm_controller`: trayectoria del brazo izquierdo.
- `right_arm_controller`: trayectoria del brazo derecho.
- `both_arms_controller`: trayectoria conjunta de los dos brazos.
- `left_gripper_controller`: gripper izquierdo.
- `right_gripper_controller`: gripper derecho.
- `joint_state_broadcaster`: publicacion de estados articulares.

La camara del prototipo esta configurada para publicar:

```text
/camera/image_raw
/camera/camera_info
```

Nota: si esos topicos no aparecen, falta el runtime de `gazebo_plugins` con
`libgazebo_ros_camera.so` en la instalacion local.

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

## Archivos principales del paquete nuevo

```text
bimanual_setup_description/
  config/initial_joint_positions.yaml
  config/ros2_controllers.yaml
  launch/spawn_bimanual.launch.py
  urdf/bimanual_setup.urdf.xacro
  urdf/macros/
  worlds/lab_empty.world
```

## Validacion rapida

```bash
source /opt/ros/humble/setup.bash
source /home/utec/robotis_ws/install/setup.bash
xacro /home/utec/robotis_ws/install/bimanual_setup_description/share/bimanual_setup_description/urdf/bimanual_setup.urdf.xacro > /tmp/bimanual_setup.urdf
check_urdf /tmp/bimanual_setup.urdf
```
