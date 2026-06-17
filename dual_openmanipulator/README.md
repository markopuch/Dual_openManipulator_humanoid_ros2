# dual_openmanipulator

Paquete base local para simular y planificar dos OpenMANIPULATOR-X en ROS 2.

Para la version con bastidor prototipo V-slot 60x60, fixtures y configuracion MoveIt independiente/simultanea de ambos brazos, usar el paquete nuevo:

```bash
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_gazebo.launch.py
ros2 launch dual_openmanipulator_vslot_sim dual_openmanipulator_vslot_moveit.launch.py
```

Esta nota es solo documentacion; este paquete se mantiene como referencia base.
