#!/usr/bin/python2
# -*- coding: utf-8 -*-

import rospy
import serial

serialPort = "/dev/shoot"
baudRate = 9600
ser = serial.Serial(port=serialPort, baudrate=baudRate, parity="N", bytesize=8, stopbits=1)

def shoot_once():
    ser.write(b'\x55\x01\x12\x00\x00\x00\x01\x69')
    rospy.sleep(0.1)
    ser.write(b'\x55\x01\x11\x00\x00\x00\x01\x68')

if __name__ == '__main__':
    rospy.init_node('shoot')

    rospy.spin()