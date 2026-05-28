#!/usr/bin/python2
# -*- coding: utf-8 -*-

import rospy
from shoot import shoot_once

def shoot_ar(data):
    for marker in data.markers:
        if marker.id == target_case:
            ar_x_0 = marker.pose.pose.position.x
            ar_y_0 = marker.pose.pose.position.y

            shoot_once()