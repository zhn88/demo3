#!/bin/bash

### gmapping with abot ###

gnome-terminal --window -e 'bash -c "roscore; exec bash"' \
--tab -e 'bash -c "sleep 3; source ~/demo_shoot/devel/setup.bash; roslaunch abot_bringup robot_with_imu.launch; exec bash"' \
--tab -e 'bash -c "sleep 3; source ~/demo_shoot/devel/setup.bash; roslaunch abot_shoot cam.launch; exec bash"' \
--tab -e 'bash -c "sleep 3; source ~/demo_shoot/devel/setup.bash; roslaunch track_tag ar_track_camera.launch; exec bash"' \
--tab -e 'bash -c "sleep 3; source ~/demo_shoot/devel/setup.bash; roslaunch robot_voice voice_wakeup.launch; exec bash"' \
--tab -e 'bash -c "sleep 4; source ~/demo_shoot/devel/setup.bash; roslaunch robot_slam navigation.launch; exec bash"' \
--tab -e 'bash -c "sleep 4; source ~/demo_shoot/devel/setup.bash; roslaunch robot_slam main.launch; exec bash"'