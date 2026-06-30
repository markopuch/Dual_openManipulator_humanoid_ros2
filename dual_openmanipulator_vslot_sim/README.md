# dual_openmanipulator_vslot_sim

Paquete nuevo para simular dos OpenMANIPULATOR-X montados sobre un bastidor prototipo con columna V-slot 60x60, viga superior 20x40 y cámara central en Gazebo Classic.

Este paquete no modifica el codigo funcional del paquete base `dual_openmanipulator`. Reutiliza sus macros prefijadas del OpenMANIPULATOR-X y agrega el bastidor, los fixtures, la configuracion Gazebo/ros2_control y una configuracion MoveIt propia.

## Contenido

- `urdf/dual_openmanipulator_vslot.urdf.xacro`: robot completo con placa base, columna, viga 20x40, fixture, cámara y dos brazos.
- `urdf/macros/vslot_60x60.xacro`: macros de perfiles lineales 60x60 y 20x40 con masa lineal.
- `urdf/macros/simple_fixture.xacro`: cajas/cilindros simples para placa, soporte y fixture.
- `urdf/macros/dual_open_manipulator_vslot.ros2_control.xacro`: `ros2_control` local con posiciones iniciales.
- `config/controllers.yaml`: controladores ros2_control para Gazebo.
- `config/dual_openmanipulator_vslot.srdf`: grupos MoveIt `left_arm`, `right_arm`, `both_arms`, `left_gripper` y `right_gripper`.
- `config/dual_arm_vslot_positions.yaml`: dimensiones principales y posiciones de montaje.
- `config/initial_joint_positions.yaml`: postura inicial bimanual.
- `launch/dual_openmanipulator_vslot_gazebo.launch.py`: Gazebo con los dos brazos sobre el bastidor.
- `launch/dual_openmanipulator_vslot_moveit.launch.py`: MoveIt/RViz para planificar cada brazo o ambos.
- `worlds/dual_arm_vslot_demo.world`: mundo local sin depender de la base de modelos online de Gazebo.

## Compilacion

Desde `/home/utec/robotis_ws`:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to dual_openmanipulator_vslot_sim
source install/setup.bash
```

## Gazebo

```bash
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_gazebo.launch.py
```

El launch inicia Gazebo, publica `robot_description`, spawnea el robot y activa:

- `joint_state_broadcaster`
- `vslot_dual_arm_controller`
- `left_vslot_gripper_controller`
- `right_vslot_gripper_controller`

Para revisar controladores:

```bash
ros2 control list_controllers
```

## MoveIt

Con Gazebo ya ejecutandose, en otra terminal:

```bash
source /opt/ros/humble/setup.bash
source /home/utec/robotis_ws/install/setup.bash
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_moveit.launch.py
```

En RViz, usar el panel `MotionPlanning`:

- `left_arm`: planifica y ejecuta solo el brazo izquierdo.
- `right_arm`: planifica y ejecuta solo el brazo derecho.
- `both_arms`: planifica y ejecuta los dos brazos al mismo tiempo.
- `left_gripper` y `right_gripper`: control independiente de las pinzas.

El controlador de brazos tiene `allow_partial_joints_goal: true`, por lo que MoveIt puede enviar trayectorias de un brazo individual al mismo controlador combinado.

## Ajustes principales

Los valores por defecto estan en `config/dual_arm_vslot_positions.yaml` y tambien se pueden sobreescribir como argumentos del launch de Gazebo:

```bash
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_gazebo.launch.py \
  vertical_column_height:=0.48 horizontal_beam_length:=0.86 left_arm_mount_x:=-0.28 right_arm_mount_x:=0.28
```

Valores finales de esta iteracion:

- `vertical_column_height`: 0.45 m
- `column_y_offset`: 0.18 m
- `horizontal_beam_length`: 0.82 m
- `horizontal_beam_profile_y`: 0.020 m
- `horizontal_beam_profile_z`: 0.040 m
- `left_arm_mount_x`: -0.26 m
- `right_arm_mount_x`: 0.26 m
- `arm_mount_y`: 0.08 m
- `arm_mount_z`: 0.30 m
- `workcell_center_xyz`: `[0.0, -0.06, 0.13]`
- `center_camera_xyz`: `[0.0, 0.10, 0.36]`

Parametros utiles:

- `base_x`, `base_y`, `base_z`: dimensiones de la placa base.
- `vertical_column_height`: altura de la columna V-slot 60x60.
- `column_y_offset`: posicion Y de la columna y la viga.
- `horizontal_beam_length`: largo de la viga superior 20x40.
- `horizontal_beam_profile_y`, `horizontal_beam_profile_z`: seccion de la viga; `profile_z=0.040` deja el lado de 40 mm vertical.
- `left_arm_mount_x`, `right_arm_mount_x`: separacion horizontal de los brazos.
- `arm_mount_y`, `arm_mount_z`: posicion de los mounts de los brazos.
- `workcell_center_x`, `workcell_center_y`, `workcell_center_z`: frame logico de zona de trabajo.
- `center_camera_x`, `center_camera_y`, `center_camera_z`: posicion de la camara central.
- `profile_6060_mass_per_meter`, `profile_2040_mass_per_meter`: masas lineales de perfiles.
- `left_arm_yaw`, `right_arm_yaw`: orientacion de cada brazo.

## Modelo V-slot

Los perfiles se aproximan como cajas simples para visualizacion/colision. La columna es 60x60 y la viga superior es 20x40 con el lado de 40 mm en Z.

- `profile_6060_mass_per_meter`: 2.6 kg/m.
- `profile_2040_mass_per_meter`: 0.76 kg/m.

La macro calcula `mass = mass_per_meter * length` y usa inercia de caja uniforme con esa masa real.

## Camara

La camara central esta en `center_camera_link` con frame optico `center_camera_optical_frame`.

En esta instalacion no esta disponible `gazebo_plugins/libgazebo_ros_camera.so`, por lo que la camara se publica por Gazebo transport:

```bash
gz topic -l | grep center_camera
```

Topic validado:

```text
/gazebo/default/dual_openmanipulator_vslot/vslot_base_plate_link/center_camera_sensor/image
```

Para verificar TF:

```bash
ros2 run tf2_ros tf2_echo world center_camera_optical_frame
```

Si se instala soporte ROS de camara para Gazebo Classic, el topic ROS esperado para habilitar seria `/dual_openmanipulator_vslot/center_camera/image_raw` y `/dual_openmanipulator_vslot/center_camera/camera_info`.

## Validacion rapida

```bash
source /opt/ros/humble/setup.bash
source /home/utec/robotis_ws/install/setup.bash
xacro install/dual_openmanipulator_vslot_sim/share/dual_openmanipulator_vslot_sim/urdf/dual_openmanipulator_vslot.urdf.xacro > /tmp/dual_openmanipulator_vslot.urdf
check_urdf /tmp/dual_openmanipulator_vslot.urdf
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_gazebo.launch.py --show-args
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_moveit.launch.py --show-args
```
