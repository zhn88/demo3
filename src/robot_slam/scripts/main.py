#!/usr/bin/python2
# -*- coding: utf-8 -*-

import rospy
import serial
import cv2
from math import pi
import rospkg

from geometry_msgs.msg import Twist
from ar_track_alvar_msgs.msg import AlvarMarkers
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf_conversions import transformations
from actionlib import SimpleActionClient
from actionlib_msgs.msg import GoalStatus
from sensor_msgs.msg import Image
from std_msgs.msg import String
import os

from shoot_image import shoot_image
from shoot_ar import shoot_ar

# Chinese number word -> digit mapping
CN_NUM = {
    u"一": 1, u"二": 2, u"三": 3, u"四": 4, u"五": 5,
    u"六": 6, u"七": 7, u"八": 8, u"九": 9, u"十": 10,
    u"零": 0, u"两": 2,
}

class Shoot:
    def __init__(self, goals):
        self.goals = goals

        # 相机中心坐标
        self.center_x, self.center_y =320, 240
        # 第一个目标的上下左右裁减
        self.height_up, self.height_down, self.width_left, self.width_right = 10, 10, 10, 10

        # 发布速度指令
        self.pub_cmd = rospy.Publisher("/cmd_vel",Twist,queue_size=1000)
        # 发布目标指令
        self.move_base = SimpleActionClient("move_base", MoveBaseAction)
        self.move_base.wait_for_server(rospy.Duration(60))
        # 获得当前的图像
        self.image_sub = rospy.Subscriber('/camera/image_raw', Image, shoot_image)
        # 获得二维码的位置
        # voice wakeup publisher
        self.wakeup_pub = rospy.Publisher("voiceWakeup", String, queue_size=10)
        # voice recognition subscriber
        self.voice_sub = rospy.Subscriber("voiceWords", String, self.voice_callback)
        self.recognized_text = None
        self.voice_received = False

        self.ar_sub = rospy.Subscriber('/ar_pose_marker', AlvarMarkers, shoot_ar)

        # 标记设计目标
        # 0: 为巡航状态
        # 1: 为第一个目标的调整状态
        # 2: 为第一个目标的射击状态
        # 3: 为第二个目标的调整状态
        # 4: 为第二个目标的射击状态
        # 5: 为第三个目标的调整状态
        # 6: 为第三个目标的射击状态
        rospy.set_param("/common/case", 0)

        # 语音保存的两个目标靶子的编号
        self.shoot_case1, self.shoot_case2 = None, None

        # 摄像机当前的图像
        self.image = None

        # 目标导航超时时间
        self.timeout = 30

        # 导航状态
        self.STATUS_DICT = {
            GoalStatus.PENDING:    "PENDING(等待中)",
            GoalStatus.ACTIVE:     "ACTIVE(执行中)",
            GoalStatus.PREEMPTED:  "PREEMPTED(被抢占)",
            GoalStatus.SUCCEEDED:  "SUCCEEDED(成功)",
            GoalStatus.ABORTED:    "ABORTED(失败)",
            GoalStatus.REJECTED:   "REJECTED(被拒绝)",
            GoalStatus.PREEMPTING: "PREEMPTING(抢占中)",
            GoalStatus.RECALLING:  "RECALLING(召回中)",
            GoalStatus.RECALLED:   "RECALLED(已召回)",
            GoalStatus.LOST:       "LOST(连接丢失)",
        }

        self.rospack = rospkg.RosPack()

    def run(self):
        rospy.loginfo("比赛开始")
        self.start_audio()
        rospy.loginfo("请语音输入两个目标靶子的编号")
        self.get_nums_from_audio()
        rospy.sleep(1)

        self.goto(self.goals[0])
        rospy.sleep(1)
        # self.case = 1

        # 开始处理第一个目标，对应函数为shoot_image
        # 当case==1的时候，调整机器车，当误差达到范围时候，更新case为2，停止调整，开始射击

        self.goto(self.goals[1])
        rospy.sleep(1)
        # self.case = 3

        # 开始处理第二个目标，对应函数为shoot_ar
        # 当case==3的时候，调整机器车，当误差达到范围时候，更新case为4，停止调整，开始射击

        self.goto(goals[2])
        rospy.sleep(1)

        # 开始处理第三个目标，对应函数为shoot_ar
        # 当case==4的时候，调整机器车，当误差达到范围时候，更新case为5，停止调整，开始射击

        # 最后巡航到第三个目标点
        self.goto(goals[3])

    def start_audio(self):
        # 播放“比赛开始”的语音
        # 获取包路径
        mp3_path = self.rospack.get_path('robot_slam') + '/mp3/start_competition.mp3'

        # 播放
        os.system('mplayer "%s"' % mp3_path)

    def get_nums_from_audio(self):
        # wakeup voice recognition
        self.wakeup_pub.publish(String(data="wakeup"))
        rospy.loginfo("说两个数字")

        self.recognized_text = None
        self.voice_received = False

        # wait for voice recognition result (max 15 seconds)
        timeout = rospy.Time.now() + rospy.Duration(15)
        while not self.voice_received and rospy.Time.now() < timeout:
            rospy.sleep(0.1)

        if not self.voice_received or not self.recognized_text:
            rospy.logwarn("没有语音结果, 默认 1, 6")
            self.shoot_case1, self.shoot_case2 = 1, 6
        else:
            # msg.data is GBK bytes from iFlytek SDK, decode to unicode
            text = self.recognized_text
            if isinstance(text, str):
                try:
                    text = text.decode("gbk")
                except:
                    try:
                        text = text.decode("utf-8")
                    except:
                        text = text.decode("utf-8", errors="replace")
            rospy.loginfo("识别到: " + text.encode("utf-8"))

            # iterate character by character, extract numbers
            nums = []
            for ch in text:
                if u"0" <= ch <= u"9":
                    nums.append(int(ch))
                elif ch in CN_NUM:
                    nums.append(CN_NUM[ch])

            if len(nums) >= 2:
                self.shoot_case1, self.shoot_case2 = nums[0], nums[1]
                rospy.loginfo("目标: %d, %d" % (self.shoot_case1, self.shoot_case2))
            else:
                rospy.logwarn("无法找到数字, 默认 1, 6")
                self.shoot_case1, self.shoot_case2 = 1, 6

        mp3_path = self.rospack.get_path("robot_slam") + "/mp3/"
        os.system("mplayer \"%s\"" % mp3_path + "rotating_target.mp3")
        os.system("mplayer \"%s\"" % mp3_path + str(self.shoot_case1) + ".mp3")
        os.system("mplayer \"%s\"" % mp3_path + "moving_target.mp3")
        os.system("mplayer \"%s\"" % mp3_path + str(self.shoot_case2) + ".mp3")

    def voice_callback(self, msg):
        self.recognized_text = msg.data
        self.voice_received = True
        rospy.loginfo("voice received: %s" % repr(msg.data))


    def goto(self, target):
        x, y, z = target
        goal = MoveBaseGoal()

        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        q = transformations.quaternion_from_euler(0.0, 0.0, z/180.0*pi)
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]

        self.move_base.send_goal(goal)
        result = self.move_base.wait_for_result(rospy.Duration(self.timeout))

        if result and self.move_base.get_state() == GoalStatus.SUCCEEDED:
            rospy.loginfo("成功到达目标点")
            return True
        else:
            if not result:
                rospy.loginfo("达到目标点超时, " + str(self.timeout))
            else:
                rospy.loginfo(self.STATUS_DICT[self.move_base.get_result()])
            return False

if __name__ == '__main__':
    rospy.init_node('main',anonymous=True)
    goalListX = rospy.get_param('~goalListX', '2.0, 2.0,2.0')
    goalListY = rospy.get_param('~goalListY', '2.0, 4.0,2.0')
    goalListYaw = rospy.get_param('~goalListYaw', '0, 90.0,2.0')
    goals = [[float(x), float(y), float(yaw)] for (x, y, yaw) in zip(goalListX.split(","),goalListY.split(","),goalListYaw.split(","))]

    shoot = Shoot(goals)
    raw_input("请按回车键开始比赛...")

    shoot.run()

