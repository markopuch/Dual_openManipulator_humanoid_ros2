# bimanual_setup_description

Paquete ROS 2 Humble para simular en Gazebo Classic un prototipo bimanual con dos OpenMANIPULATOR-X montados en un marco de perfiles de aluminio.

## Creacion del paquete

Comando usado desde `src/Dual_openManipulator_humanoid_ros2`:

```bash
source /opt/ros/humble/setup.bash
ros2 pkg create bimanual_setup_description --build-type ament_cmake --dependencies rclcpp gazebo_ros robot_state_publisher xacro
```

Carpetas principales:

```text
bimanual_setup_description/
  config/
  launch/
  urdf/
  worlds/
```

## Construccion

```bash
cd /home/utec/robotis_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to bimanual_setup_description
source install/setup.bash
```

## Gazebo

Controladores independientes para cada brazo:

```bash
ros2 launch bimanual_setup_description spawn_bimanual.launch.py
```

Controlador unico para mandar trayectorias a los dos brazos en una sola accion:

```bash
ros2 launch bimanual_setup_description spawn_bimanual.launch.py use_combined_controller:=true
```

## Topicos de camara esperados

El URDF incluye `libgazebo_ros_camera.so` para publicar:

```text
/camera/image_raw
/camera/camera_info
```

En esta maquina puede faltar el paquete runtime `gazebo_plugins`; si el plugin no esta instalado, Gazebo cargara el robot pero no publicara los topicos ROS de la camara.
