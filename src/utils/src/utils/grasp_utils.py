# -*- coding: utf-8 -*-
import std_msgs.msg
from utils.misc_utils import *
import tf2_ros
#from utils.nav_utils import OMNIBASE

class ARM:
    def __init__(self, joint_names = ["arm_lift_joint", "arm_flex_joint", "arm_roll_joint", "wrist_flex_joint", "wrist_roll_joint"],
                 arm_controller_action_client = '/hsrb/arm_trajectory_controller/follow_joint_trajectory'):
        # import tf2_ros
        self._joint_names = joint_names
        self._cli = actionlib.SimpleActionClient(arm_controller_action_client,
            control_msgs.msg.FollowJointTrajectoryAction)
        self._tf_man = TF_MANAGER()
        #self._grasp_base = OMNIBASE()

    def set_joint_values(self, joint_values = [0.0, 0.0, -1.6, -1.6, 0.0], duration = 5.0):
        goal = control_msgs.msg.FollowJointTrajectoryGoal()
        traj = trajectory_msgs.msg.JointTrajectory()
        traj.joint_names = self._joint_names
        p = trajectory_msgs.msg.JointTrajectoryPoint()
        p.positions = joint_values
        p.velocities = [0.1, 0.1, 0.1, 0.1, 0.1]
        p.time_from_start = rospy.Duration(duration)
        traj.points = [p]
        goal.trajectory = traj

        # send message to the action server
        #print('message sent')
        self._cli.send_goal(goal)

        # wait for the action server to complete the order
        return self._cli.wait_for_result()
    
    def get_joint_values(self):
        states = rospy.wait_for_message('/xarm/joint_states', JointState)
        st = states.position
        return [st[0], st[1],st[2], st[3], st[4], st[5]]

    def set_named_target(self, pose = 'go', duration = 5):

        if pose == 'face':
            joint_values = [1.01, -0.03, -2.98, 0, 1.49]
        elif pose == 'navigation':
            joint_values = [1.01, -0.31, 0.03, 0, -0.51]
        elif pose == 'pointing':
            joint_values = [1.01, 0.23, -1.22, 0, -0.53]
        elif pose == 'table':
            joint_values = [1.01, -0.65, -0.64, 0.0, 0.1]
        elif pose == 'head':
            joint_values = [1.01, -0.965, -0.489, 0.0, -0.131]
        #go case
        else:   
            joint_values = [0.0, 0.0, -1.6, -1.6, 0.0]
        self.set_joint_values(joint_values, duration=duration)

    def check_grasp(self, weight = 1.0):
        
        force = self._wrist.get_force()
        force = np.linalg.norm(np.array(force))
        if force > weight:
            return True
        else:
            l_finger = 'hand_l_finger_tip_frame'
            r_finger = 'hand_r_finger_tip_frame'
            dist,_ = self._tf_man.getTF(target_frame=r_finger, ref_frame=l_finger)
            np.array(dist)
            dist = np.linalg.norm(dist)
            if dist > 0.02:
                return True
            else:
                return False
            
    def move_hand_to_target(self, target_frame = 'target', offset=[0,0,0], THRESHOLD = 0.05):
        succ = False
        #THRESHOLD = 0.05
        #THRESHOLD_T = 0.1

        hand = 'hand_palm_link'
        base = 'base_link'

        while not succ and not rospy.is_shutdown():
            try:
                target_base, _ = self._tf_man.getTF(target_frame = hand, ref_frame=base)
                dist, _ = self._tf_man.getTF(target_frame = target_frame, ref_frame=base)
                e = np.array(dist) - np.array(target_base) - np.array(offset)
                e[2] = 0
                
                rospy.loginfo("Distance to goal: {:.2f}, {:.2f}".format(e[0], e[1]))
                if abs(e[0]) < THRESHOLD:
                    e[0] = 0
                if abs(e[1]) < THRESHOLD:
                    e[1] = 0
                #if abs(eT) < THRESHOLD_T:
                #    eT = 0
                e_norm = np.linalg.norm(e)
                succ = e_norm < THRESHOLD #and abs(eT) < THRESHOLD_T
                #grasp_base.tiny_move(velX=0.4*e[0], velY=0.6*e[1], velT=0.7*eT,  std_time=0.2, MAX_VEL=0.3, MAX_VEL_THETA=0.9)
                #self._grasp_base.tiny_move(velX=0.4*e[0], velY=0.6*e[1], std_time=0.2, MAX_VEL=0.3)
            except (tf2.LookupException, tf2.ConnectivityException, tf2.ExtrapolationException) as e:
                rospy.logwarn("Failed to get transform: {}".format(str(e)))
                continue
        return succ
    
class GAZE:
    def __init__(self, 
                 arm: ARM,
                 pan_joint_idx=0, tilt_joint_idx=4,
                 pan_limits=(-3.14, 3.14), tilt_limits=(-1.2, 1.2),
                 tf_timeout=0.5,
                 camera_frame = 'camera_link',
                 base_frame='base_link',
                 reference_frame='map'
                 ):
        if not isinstance(arm, ARM):
            raise TypeError("Expected 'arm' to be an instance of ARM class.")

        self._arm = arm
        self._tf_buffer = tf2_ros.Buffer()
        self._tf_listener = tf2_ros.TransformListener(self._tf_buffer)

        self._camera_frame = camera_frame
        self._base_frame = base_frame
        self._reference_frame = reference_frame
        self._tf_timeout = tf_timeout

        self._target_point = np.zeros(3)
        self.pan_offset = 1.01
        self._pan_limits = (pan_limits[0] + self.pan_offset, pan_limits[1] - self.pan_offset) 
        self._tilt_limits = tilt_limits
        self._pan_joint_idx = pan_joint_idx
        self._tilt_joint_idx = tilt_joint_idx


    def _get_transform(self, target_frame, source_frame):
        try:
            trans = self._tf_buffer.lookup_transform(
                target_frame,
                source_frame,
                rospy.Time(0),
                rospy.Duration(self._tf_timeout)
            )
            t = trans.transform.translation
            r = trans.transform.rotation
            translation = [t.x, t.y, t.z]
            rotation = [r.x, r.y, r.z, r.w]
            return translation, rotation
        except Exception as e:
            rospy.logwarn(f"[GazeArm] TF Error: {e}")
            return None

    def _calculate_pan_tilt(self):
        camera_pose = self._get_transform(self._reference_frame, self._camera_frame)
        base_pose = self._get_transform(self._reference_frame, self._base_frame)
        if not camera_pose or not base_pose:
            return 0.0, 0.0

        camera_pos = np.array(camera_pose[0])
        base_pos = np.array(base_pose[0])
        _, _, base_yaw = tf.transformations.euler_from_quaternion(base_pose[1])
        target_vector = self._target_point - base_pos

        target_yaw = np.arctan2(target_vector[1], target_vector[0])
        pan = target_yaw - base_yaw
        pan = np.arctan2(np.sin(pan), np.cos(pan))

        dz = camera_pos[2] - self._target_point[2]
        dx = np.linalg.norm(target_vector[:2])
        tilt = np.arctan2(dz, dx)
        tilt += -0.1  # compensación si hay inclinación de montaje

        return pan, tilt

    def move_head(self, pan, tilt, duration=1.0):
        current_joints = self._arm.get_joint_values()
        if current_joints is None:
            rospy.logwarn("[GazeArm] No se pudo obtener el estado actual de las articulaciones.")
            return False

        joint_values = list(current_joints)
        joint_values[self._pan_joint_idx] = np.clip(pan + self.pan_offset, *self._pan_limits)
        joint_values[self._tilt_joint_idx] = np.clip(tilt, *self._tilt_limits)

        print("Joint state goal: ",joint_values)
        return self._arm.set_joint_values(joint_values[:5], duration)

    def look_at(self, x, y, z, frame='map'):
        self._target_point = np.array([x, y, z])
        self._reference_frame = frame
        self._arm.set_named_target('head', duration=2.0)

        try:
            pan, tilt = self._calculate_pan_tilt()
            return self.move_head(pan, tilt)
        except Exception as e:
            rospy.logerr(f"[GazeArm] Error en look_at: {e}")
            return False

    def look_at_frame(self, frame_id):
        transform = self._get_transform(self._reference_frame, frame_id)
        if not transform:
            return False
        return self.look_at(*transform[0], frame=self._reference_frame)
    
    def enter_head_mode(self):
        self.set_named_target('head')
        rospy.sleep(1.0)

    def set_named_target(self, pose='neutral'):
        poses = {
            'neutral': [self.pan_offset, 0.0],
            'left': [-1.0 + self.pan_offset, 0.0],
            'right': [1.0 - self.pan_offset, 0.0],
            'up': [self.pan_offset, 0.8],
            'down': [self.pan_offset, -0.8]
        }
        pan, tilt = poses.get(pose, poses['neutral'])
        return self.move_head(pan, tilt)




from geometry_msgs.msg import Twist
import math

class BASE:
    def __init__(self, cmd_vel_topic='/hsrb/command_velocity'):
        self._base_vel_pub = rospy.Publisher(cmd_vel_topic, Twist, queue_size=10)
        self.velX = 0
        self.velY = 0
        self.velT = 0
        self.timeout = 0.5
        self.MAX_VEL = 0.03
        self.MAX_VEL_THETA = 0.5

    def _move_base_vel(self):
        twist = Twist()
        twist.linear.x = self.velX
        twist.linear.y = self.velY
        twist.angular.z = self.velT
        self._base_vel_pub.publish(twist)

    def _move_base_time(self):
        start_time = rospy.Time.now().to_sec()
        end_time = start_time + self.timeout
        while rospy.Time.now().to_sec() < end_time and not rospy.is_shutdown():
            self._move_base_vel()

    def _limit_velocity(self, velocity, max_velocity):
        return max_velocity * math.copysign(1, velocity) if abs(velocity) > max_velocity else velocity
    
    def tiny_move(self, velX=0, velY=0, velT=0, std_time=0.5, MAX_VEL=0.03, MAX_VEL_THETA=0.5):
        self.MAX_VEL = MAX_VEL
        self.MAX_VEL_THETA = MAX_VEL_THETA
        self.timeout = std_time
        
        # Limit velocities
        self.velX = self._limit_velocity(velX, MAX_VEL)
        self.velY = self._limit_velocity(velY, MAX_VEL)
        self.velT = self._limit_velocity(velT, MAX_VEL_THETA)
        
        self._move_base_time()
    
    
    def turn_radians(self, time, radians):
        vel_theta = radians / time
        self.tiny_move(velT= vel_theta, std_time= time, MAX_VEL_THETA= vel_theta)
