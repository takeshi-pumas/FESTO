#!/usr/bin/env python3

import tf
import cv2
import rospy  
import tf2_ros                                    
#from segmentation.srv import Segmentation, SegmentationResponse 
#from segmentation.msg import *
from cv_bridge import CvBridge
#from object_classification.srv import *
import numpy as np
import ros_numpy
import os
import matplotlib.pyplot as plt
import rospkg
import yaml
from sensor_msgs.msg import Image , LaserScan , PointCloud2
from geometry_msgs.msg import TransformStamped, Pose
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
#import seaborn as sns
import pandas as pd
#from sklearn.decomposition import PCA

rospy.init_node('festeshi')

points_msg=rospy.wait_for_message("camera/depth_registered/points",PointCloud2,timeout=5)
points_data = ros_numpy.numpify(points_msg) 
print(points_data)
image = points_data['rgb'].view((np.uint8, 4))[..., [2, 1, 0]]
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   
cv2.imshow(rgb_image)