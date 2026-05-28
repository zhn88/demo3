#!/usr/bin/python2
# -*- coding: utf-8 -*-

import rospy
from shoot import shoot_once

def shoot_image(msg):
    case = rospy.get_param("/common/case", -1)
    if case == -1:
        rospy.loginfo("获取全局case失败")
        return
    if case == 1:
        pass
        # 如果在误差范围内,更新case为2，停止调整，开始射击
        rospy.set_param("/common/case", 2)
    elif case == 2:
        # 等待惯性稳定
        rospy.sleep(1)
        shoot_once()
        rospy.set_param("/common/case", 0)
        rospy.sleep(1)