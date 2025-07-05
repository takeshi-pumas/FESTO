import rospy
import numpy as np
import cv2
import os
import rospkg
import tf2_ros
from cv_bridge import CvBridge
import ros_numpy
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import TransformStamped
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud
from human_detector.srv import Point_detectorResponse, Human_detectorResponse

class BaseDetector:
    def __init__(self):
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        self.tf_broadcaster = tf2_ros.StaticTransformBroadcaster()
        self.bridge = CvBridge()
        self.net = self._load_openpose_model()

    def _load_openpose_model(self):
        usr_url = os.path.expanduser('~')
        proto = usr_url + "/openpose/models/pose/body_25/pose_deploy.prototxt"
        weights = usr_url + "/openpose/models/pose/body_25/pose_iter_584000.caffemodel"
        return cv2.dnn.readNetFromCaffe(proto, weights)

    def write_tf(self, position, orientation, child_frame, parent_frame='map'):
        t = TransformStamped()
        t.header.stamp = rospy.Time.now()
        t.header.frame_id = parent_frame
        t.child_frame_id = child_frame
        t.transform.translation.x = position[0]
        t.transform.translation.y = position[1]
        t.transform.translation.z = position[2]
        t.transform.rotation.x = orientation[0]
        t.transform.rotation.y = orientation[1]
        t.transform.rotation.z = orientation[2]
        t.transform.rotation.w = orientation[3]
        return t

    def publish_tf(self, tf):
        self.tf_broadcaster.sendTransform(tf)

    def remove_background(self, points_msg, distance):
        data = ros_numpy.numpify(points_msg)
        image = data['rgb'].view((np.uint8, 4))[..., [2, 1, 0]]
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        zs = np.where(~np.isnan(data['z']), data['z'], 10)
        mask = np.where((zs < distance + 0.3), 1, 0).astype(np.uint8)
        masked = cv2.bitwise_and(rgb_image, rgb_image, mask=mask)
        return rgb_image, masked

    def run_openpose(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (w, h), (0, 0, 0), swapRB=False, crop=False)
        self.net.setInput(blob)
        return self.net.forward(), w, h

    def save_image(self, img, name='', dir_name=''):
        rospack = rospkg.RosPack()
        base_path = os.path.join(rospack.get_path('config_files'), 'src')
        if dir_name:
            full_dir = os.path.join(base_path, dir_name)
            os.makedirs(full_dir, exist_ok=True)
        else:
            full_dir = base_path

        num_files = len(os.listdir(full_dir))
        filename = name + str(num_files + 1).zfill(4) + '.jpg'
        cv2.imwrite(os.path.join(full_dir, filename), img)

class HumanDetector(BaseDetector):
    def detect(self, points_msg, dist, remove_bkg):
        data = ros_numpy.numpify(points_msg)
        frame = None
        if remove_bkg:
            _, frame = self.remove_background(points_msg, dist)
        else:
            rgb = data['rgb'].view((np.uint8, 4))[..., [2, 1, 0]]
            frame = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)

        output, w, h = self.run_openpose(frame)
        prob_map = cv2.resize(output[0, 0], (w, h))
        mask = prob_map > 0.3
        coords = np.argwhere(mask)
        xyz = [
            (data['x'][y, x], data['y'][y, x], data['z'][y, x])
            for y, x in coords
            if not np.isnan(data['x'][y, x]) and not np.isnan(data['y'][y, x]) and not np.isnan(data['z'][y, x])
        ]

        res = Human_detectorResponse()
        if xyz:
            xyz = np.array(xyz)
            centroid = xyz.mean(axis=0)
            res.x, res.y, res.z = centroid.tolist()
        else:
            res.x = res.y = res.z = 0.0

        return res

class PointingDetector(BaseDetector):
    def detect(self, points_msg, dist, remove_bkg):
        data = ros_numpy.numpify(points_msg)
        frame = None
        if remove_bkg:
            _, frame = self.remove_background(points_msg, dist)
            self.save_image(frame, name="maskedImage")
        else:
            rgb = data['rgb'].view((np.uint8, 4))[..., [2, 1, 0]]
            frame = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
            self.save_image(frame, name="noMaskedImage")

        output, w, h = self.run_openpose(frame)
        joints = {}
        res = Point_detectorResponse()
        for i, name in zip([3, 4, 6, 7], ['right_elbow', 'right_wrist', 'left_elbow', 'left_wrist']):
            prob_map = cv2.resize(output[0, i], (w, h))
            mask = prob_map > 0.45
            x, y, z = 0.0, 0.0, 0.0
            if np.any(mask):
                x = np.nanmean(data['x'][mask])
                y = np.nanmean(data['y'][mask])
                z = np.nanmean(data['z'][mask])
            if not np.isnan(x) and not np.isnan(y) and not np.isnan(z):
                joints[name] = [x, y, z]

        for side in ['right', 'left']:
            wrist = joints.get(f'{side}_wrist')
            elbow = joints.get(f'{side}_elbow')
            if wrist and elbow:
                vec = np.subtract(wrist, elbow)
                alfa = -wrist[2] / vec[2] if vec[2] != 0 else 0
                point = wrist[0] + alfa * vec[0], wrist[1] + alfa * vec[1], 0.0
                tf = self.write_tf(point, (0, 0, 0, 1), f'pointing_{side}')
                self.publish_tf(tf)
                setattr(res, f'x_{side[0]}', point[0])
                setattr(res, f'y_{side[0]}', point[1])
                setattr(res, f'z_{side[0]}', point[2])
            else:
                setattr(res, f'x_{side[0]}', 0.0)
                setattr(res, f'y_{side[0]}', 0.0)
                setattr(res, f'z_{side[0]}', 0.0)
                tf = self.write_tf((0, 0, 0), (0, 0, 0, 1), f'pointing_{side}')
                self.publish_tf(tf)

        return res
