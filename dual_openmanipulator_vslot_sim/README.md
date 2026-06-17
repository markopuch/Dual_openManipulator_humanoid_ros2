# dual_openmanipulator_vslot_sim

Paquete nuevo para simular dos OpenMANIPULATOR-X montados sobre un bastidor prototipo V-slot 60x60 en Gazebo Classic y controlarlos desde una sola interfaz MoveIt/RViz.

Este paquete no modifica el codigo funcional del paquete base `dual_openmanipulator`. Reutiliza sus macros prefijadas del OpenMANIPULATOR-X y agrega el bastidor, los fixtures, la configuracion Gazebo/ros2_control y una configuracion MoveIt propia.

## Contenido

- `urdf/dual_openmanipulator_vslot.urdf.xacro`: robot completo con placa base, columna, viga superior, fixtures y dos brazos.
- `urdf/macros/vslot_60x60.xacro`: macro del perfil V-slot 60x60 con masa e inercia parametrizadas.
- `urdf/macros/simple_fixture.xacro`: fixtures simples para placa, soportes y piezas demo.
- `config/controllers.yaml`: controladores ros2_control para Gazebo.
- `config/dual_openmanipulator_vslot.srdf`: grupos MoveIt `left_arm`, `right_arm`, `both_arms`, `left_gripper` y `right_gripper`.
- `config/dual_arm_vslot_positions.yaml`: dimensiones principales y posiciones de montaje.
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
  column_height:=0.75 beam_length:=1.10 left_mount_x:=-0.42 right_mount_x:=0.42
```

Parametros utiles:

- `base_x`, `base_y`, `base_z`: dimensiones de la placa base.
- `column_height`: altura de la columna V-slot.
- `beam_length`: largo de la viga superior.
- `left_mount_x`, `right_mount_x`: separacion horizontal de los soportes.
- `arm_base_z_offset`: offset vertical entre soporte y base del brazo.
- `left_arm_yaw`, `right_arm_yaw`: orientacion de cada brazo.

## Modelo V-slot

El perfil se aproxima como una caja de 60 mm para visualizacion/colision. La masa e inercia usan parametros editables en `urdf/macros/vslot_60x60.xacro`:

- `mass_per_meter`: 2.58 kg/m.
- `area`: 9.521e-4 m2.
- `i_area_y` y `i_area_z`: 3.70420e-7 m4.

La macro calcula `mass = mass_per_meter * length` y asigna la inercia segun el eje del perfil.

## Validacion rapida

```bash
source /opt/ros/humble/setup.bash
source /home/utec/robotis_ws/install/setup.bash
xacro install/dual_openmanipulator_vslot_sim/share/dual_openmanipulator_vslot_sim/urdf/dual_openmanipulator_vslot.urdf.xacro > /tmp/dual_openmanipulator_vslot.urdf
check_urdf /tmp/dual_openmanipulator_vslot.urdf
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_gazebo.launch.py --show-args
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_moveit.launch.py --show-args
```
