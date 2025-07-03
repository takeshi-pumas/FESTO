# -*- coding: utf-8 -*-
import sys
import rospkg
import yaml
import cv2
import tf as tf
import tf2_ros as tf2
import rospy
import numpy as np
import ros_numpy
from std_msgs.msg import String
#from tmc_msgs.msg import Voice
from geometry_msgs.msg import Twist,PoseStamped
from geometry_msgs.msg import  TransformStamped, Pose, Point, Quaternion
from sensor_msgs.msg import Image as ImageMsg, PointCloud2
from sensor_msgs.msg import JointState, LaserScan
#import tmc_control_msgs.msg
import trajectory_msgs.msg
import control_msgs.msg
#from tmc_msgs.msg import TalkRequestActionGoal, TalkRequestAction
import actionlib
from actionlib_msgs.msg import GoalStatus
#from hmm_navigation.msg import NavigateActionGoal, NavigateAction
#from sensor_msgs.msg import LaserScan
from glob import glob
from os import path
# Class to get XTION camera info (head)


class RGBD:
    def __init__(self, PC_rectified_point_topic = "camera/depth_registered/points"):
        self._br = tf.TransformBroadcaster()
        self._cloud_sub = rospy.Subscriber(PC_rectified_point_topic,
            PointCloud2, self._cloud_cb)
        self._points_data = None
        self._image_data = None
        self._h_image = None
        self._region = None
        self._h_min = 0
        self._h_max = 0
        self._xyz = [0, 0, 0]
        self._frame_name = None

    def _cloud_cb(self, msg):
        self._points_data = ros_numpy.numpify(msg)
        self._image_data = \
            self._points_data['rgb'].view((np.uint8, 4))[..., [2, 1, 0]]
        hsv_image = cv2.cvtColor(self._image_data, cv2.COLOR_RGB2HSV_FULL)
        self._h_image = hsv_image[..., 0]
        self._region = \
            (self._h_image > self._h_min) & (self._h_image < self._h_max)
        if not np.any(self._region):
            return

        (y_idx, x_idx) = np.where(self._region)
        x = np.average(self._points_data['x'][y_idx, x_idx])
        y = np.average(self._points_data['y'][y_idx, x_idx])
        z = np.average(self._points_data['z'][y_idx, x_idx])
        self._xyz = [y, x, z]
        if self._frame_name is None:
            return

        self._br.sendTransform(
            (x, y, z), tf.transformations.quaternion_from_euler(0, 0, 0),
            rospy.Time(msg.header.stamp.secs, msg.header.stamp.nsecs),
            self._frame_name,
            msg.header.frame_id)

    def get_image(self):
        rgb_img = cv2.cvtColor(self._image_data, cv2.COLOR_BGR2RGB)
        return rgb_img

    def get_points(self):
        return self._points_data

    def get_h_image(self):
        return self._h_image

    def get_region(self):
        return self._region

    def get_xyz(self):
        return self._xyz

    def set_h(self, h_min, h_max):
        self._h_min = h_min
        self._h_max = h_max

    def set_coordinate_name(self, name):
        self._frame_name = name

# Color segmentator
    def color_segmentator(self, color="orange"):
        image = self.get_image()
        if(color == "blue"):
            lower_threshold = (100, 120, 100)
            upper_threshold = (150, 220, 240)
        else:
            lower_threshold = (102, 95, 97)
            upper_threshold = (115, 255, 255)
        img_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(img_hsv, lower_threshold, upper_threshold)
        res = cv2.bitwise_and(img_hsv, img_hsv, mask=mask)
        pos = []
        pixels = cv2.findNonZero(mask)
        pixels = list(cv2.mean(pixels))
        pos.append(pixels[:2])
        return pos

class TF_MANAGER:
    def __init__(self):
        self._tfbuff = tf2.Buffer()
        self._lis = tf2.TransformListener(self._tfbuff)
        self._tf_static_broad = tf2.StaticTransformBroadcaster()
        self._broad = tf2.TransformBroadcaster()

    def _fillMsg(self, pos=[0, 0, 0], rot=[0, 0, 0, 1], point_name='', ref="map"):
        TS = TransformStamped()
        TS.header.stamp = rospy.Time.now()
        TS.header.frame_id = ref
        TS.child_frame_id = point_name
        TS.transform.translation = Point(*pos)
        TS.transform.rotation = Quaternion(*rot)
        return TS

    def pub_tf(self, pos=[0, 0, 0], rot=[0, 0, 0, 1], point_name='', ref="map"):
        dinamic_ts = self._fillMsg(pos, rot, point_name, ref)
        self._broad.sendTransform(dinamic_ts)

    def pub_static_tf(self, pos=[0, 0, 0], rot=[0, 0, 0, 1], point_name='', ref="map"):
        static_ts = self._fillMsg(pos, rot, point_name, ref)
        self._tf_static_broad.sendTransform(static_ts)

    def change_ref_frame_tf(self, point_name='', rotational=[0, 0, 0, 1], new_frame='map'):
        try:
            traf = self._tfbuff.lookup_transform(
                new_frame, point_name, rospy.Time(0))
            translation, _ = self.tf2_obj_2_arr(traf)
            self.pub_static_tf(pos=translation, rot=rotational,
                               point_name=point_name, ref=new_frame)
            return True
        except:
            return False

    def getTF(self, target_frame='', ref_frame='map'):
        try:
            tf = self._tfbuff.lookup_transform(
                ref_frame, target_frame, rospy.Time(0), rospy.Duration(1.5))
            return self.tf2_obj_2_arr(tf)
        except:
            return [False, False]

    def tf2_obj_2_arr(self, transf):
        pos = []
        pos.append(transf.transform.translation.x)
        pos.append(transf.transform.translation.y)
        pos.append(transf.transform.translation.z)

        rot = []
        rot.append(transf.transform.rotation.x)
        rot.append(transf.transform.rotation.y)
        rot.append(transf.transform.rotation.z)
        rot.append(transf.transform.rotation.w)

        return [pos, rot]


class LineDetector:
    def __init__(self, laser_scan_topic = "/scan"):
        self.scan_sub = rospy.Subscriber(laser_scan_topic,
                                          LaserScan, self._scan_callback)
        self._result = False

    def _scan_callback(self, scan_msg):
        # Obtener las lecturas de los puntos del LIDAR
        ranges = scan_msg.ranges

        # Tomar solo las muestras centrales
        num_samples = len(ranges)
        num_central_samples = int(num_samples * 0.1)  # valor ajustable
        start_index = int((num_samples - num_central_samples) / 2)
        central_ranges = ranges[start_index: start_index + num_central_samples]

        # Calcular la media de las lecturas
        mean = sum(central_ranges) / len(central_ranges)

        # Verificar si las lecturas se aproximan a ser una línea
        if mean < 0.6:  # Distancia ajustable
            # rospy.loginfo("Posible línea enfrente")
            self._result = True
        else:
            # rospy.loginfo("No se encontró una línea")
            self._result = False

    def line_found(self):
        return self._result


class Talker:
    def __init__(self, talk_request_topic = '/robot_speech', speed_wpm = 150):
        """
        Initialize the talker with publisher to the given topic.
        Args:
            talk_request_topic: Topic to publish the sentence to.
            speed_wpm: Voice engine speed in words per minute (espeak -s)
        """
        self.speed_wpm = speed_wpm
        self.voice = rospy.Publisher('/robot_speech', String, queue_size=10)

    def _estimate_timeout(self, sentence: str) -> float:
        """
        Estimate the time needed to speak the sentence.
        Returns time in seconds
        """
        if not sentence:
            return 0.0
        chars_per_word = 5
        cps = (self.speed_wpm * chars_per_word) / 60.0
        pause_penalty = {
            ',': 0.2,
            '.': 0.4,
            '!': 0.3,
            '?': 0.3,
            '...': 0.5
        }

        pause_time = sum(sentence.count(p) * t for p, t in pause_penalty.items())
        time_speech = len(sentence) / cps
        return time_speech + pause_time
    

    def talk(self, sentence: str, wait: bool = True) -> bool:
        """
        Send a talk request

        Args:
            sentence: The sentence to say.
            wait: Whether to sleep for estimated duration after speaking.

        Returns:
            bool: True if published successfully.

        """
        #sentence = sentence.strip()
        if not sentence:
            return False
        
        try:
            #msg = String(data = sentence)
            msg = String(sentence)
            self.voice.publish(msg)
            rospy.loginfo(f"[Talker] Published: {sentence}")

            if wait: 
                timeout = self._estimate_timeout(sentence)
                rospy.sleep(timeout)
            
            return True

        except Exception as e:
            rospy.logerr(f"[Talker] Failed to send message: {e}")
            return False



def save_image(img,name='',dirName=''):
    rospack = rospkg.RosPack()
    file_path = rospack.get_path('images_repos')
    
    num_data = len(glob(path.join(file_path,"src",dirName,"*"))) if dirName else len(glob(path.join(file_path,"src","*")))
    
    num_data = str(num_data+1).zfill(4)

    name = "/" + name if (name and not(name.startswith("/"))) else name
    dirName = "/" + dirName if (dirName and not(dirName.startswith("/"))) else dirName

 
    if name and dirName:
        #print(file_path+"/src"+dirName+name+".jpg")
        cv2.imwrite(file_path+"/src"+dirName+name+num_data+".jpg",img)
    
    elif dirName and not(name):
        #print(file_path+"/src"+dirName+"/"+"image"+".jpg")
        cv2.imwrite(file_path+"/src"+dirName+"/"+"image"+num_data+".jpg",img)

    elif not(dirName) and name:
        #print(file_path+"/src"+name+".jpg")
        cv2.imwrite(file_path+"/src"+name+num_data+".jpg",img)
    
    else:
        #print(file_path+"/src"+"tmp"+".jpg")
        cv2.imwrite(file_path+"/src"+"image"+".jpg",img)
    
