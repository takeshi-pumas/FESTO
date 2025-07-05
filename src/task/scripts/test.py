#!/usr/bin/env python3
from utils import misc_utils, grasp_utils
import rospy
from std_msgs.msg import String

rospy.init_node("test_node")
voice = misc_utils.Talker()
rospy.sleep(0.2)
arm = grasp_utils.ARM(joint_names = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"], 
                      arm_controller_action_client = "/xarm/xarm6_traj_controller/follow_joint_trajectory")

head = grasp_utils.GAZE(arm = arm)

bumper = grasp_utils.BUMPER()

rospy.sleep(0.1)

result = voice.talk(sentence = "hello, my name is festino", wait = True)

rospy.sleep(0.1)
poses = [[1.01, -0.03, -2.98, 0, 1.49],[1.01, -0.31, 0.03, 0, -0.51], [1.01, 0.23, -1.22, 0, -0.53], [1.01, -0.65, -0.64, 0.0, 0.1]]

# 58, -2, -171, 0, 85.2, 0 #face
# 1.01, -0.03, -2.98, 0, 1.49

# 58, -17.8, 1.6, 0, -29.2, 0 #navigation
#1.01, -0.31, 0.03, 0, -0.51

# 58, 13.4, -70.1, 0, -30.2, 0 #pointing
# 1.01, 0.23, -1.22, 0, -0.53,0

# 58, -37.2, -36.9, 0, 5.7, 0 #table
#1.01, 0.65, 0.64, 0.0, 0.1, 0

#arm.set_joint_values(joint_values = poses[1])

#for pose in poses:
#    print(pose)
    #arm.set_joint_values(joint_values = pose)
    #rospy.sleep(1.0)

#arm.set_named_target("head")
#head.look_at(x = 2.0, y = -1.5, z = 0.0, frame = "base_link")
#head.move_head(pan = 0, tilt= 0)
#rospy.spin()

response = bumper.wait_for_bumper()
if response:
    voice.talk("Bumper pressed")
else:
    voice.talk("Bumper not pressed")