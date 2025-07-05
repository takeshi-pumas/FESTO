#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import PointCloud2
from human_detector.srv import Point_detector, Point_detectorResponse
from human_detector.srv import Human_detector, Human_detectorResponse
from detector_utils import PointingDetector, HumanDetector

class HumanPointingServiceNode:
    def __init__(self):
        rospy.init_node('human_pointing_detector')

        self.pointing_detector = PointingDetector()
        self.human_detector = HumanDetector()

        rospy.Service('/detect_pointing', Point_detector, self.handle_pointing)
        rospy.Service('/detect_human', Human_detector, self.handle_human)

        rospy.loginfo("human pose detection services available")
        rospy.spin()

    def handle_pointing(self, request):
        rospy.loginfo('Received pointing detection request')
        points_msg = rospy.wait_for_message("/camera/depth_registered/points", PointCloud2, timeout=25)
        dist = 6 if request.dist == 0 else request.dist
        return self.pointing_detector.detect(points_msg, dist, request.removeBKG)

    def handle_human(self, request):
        rospy.loginfo('Received human detection request')
        points_msg = rospy.wait_for_message("/camera/depth_registered/points", PointCloud2, timeout=25)
        dist = 6 if request.dist == 0 else request.dist
        return self.human_detector.detect(points_msg, dist, request.removeBKG)

if __name__ == '__main__':
    try:
        HumanPointingServiceNode()
    except rospy.ROSInterruptException:
        pass
