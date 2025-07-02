#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import subprocess
from std_msgs.msg import String

class EspeakNode:
    def __init__(self):
        rospy.init_node("speaker_node")

        self.voice = rospy.get_param("~voice", "mb-en1")
        self.speed = rospy.get_param("~speed", "150")

        rospy.Subscriber("/robot_speech", String, self.speak_callback)
        rospy.loginfo(f"Nodo speaker iniciado con voz {self.voice} y velocidad {self.speed}")
        rospy.spin()
    
    def speak_callback(self, msg):
        text = msg.data.strip()
        rospy.loginfo(f"speaking: {text}")

        try:
            subprocess.Popen(["espeak", "-v", self.voice, "-s", str(self.speed), text])
        except:
            rospy.logerr("Error")

if __name__ == "__main__":
    try:
        EspeakNode()
    except rospy.ROSInitException:
        pass
