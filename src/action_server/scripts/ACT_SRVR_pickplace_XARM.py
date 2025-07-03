#!/usr/bin/env python3
import rospy
import sys
import tf2_ros
import tf2_geometry_msgs
import numpy as np
import smach
from smach_ros import ActionServerWrapper, IntrospectionServer
import moveit_commander
from geometry_msgs.msg import Pose, Point, Quaternion, PointStamped, PoseStamped, TransformStamped
from shape_msgs.msg import SolidPrimitive
from moveit_msgs.msg import CollisionObject, AttachedCollisionObject
from moveit_commander import Constraints
from moveit_msgs.msg import OrientationConstraint, MoveItErrorCodes
from visualization_msgs.msg import Marker
from action_server.msg import PickPlaceAction
from std_srvs.srv import Empty

from tf.transformations import euler_from_quaternion, quaternion_from_euler, quaternion_multiply

# Optional gripper interface placeholder for xArm
# Replace this with your real gripper interface
class FakeGripper:
    def open(self):
        rospy.loginfo("Gripper opened (fake).")

    def close(self):
        rospy.loginfo("Gripper closed (fake).")

class PlacingStateMachine:
    def __init__(self):
        self.gripper = FakeGripper()
        moveit_commander.roscpp_initialize(sys.argv)
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        self.arm = moveit_commander.MoveGroupCommander("xarm6")

        self.tf2_buffer = tf2_ros.Buffer()
        self.listener = tf2_ros.TransformListener(self.tf2_buffer)
        self.br = tf2_ros.StaticTransformBroadcaster()

        self.marker_pub = rospy.Publisher("/target_pose_marker", Marker, queue_size=1)

        self.eef_link = self.arm.get_end_effector_link()
        self.approach_limit = 10
        self.approach_count = 0

        self.arm.allow_replanning(True)
        self.arm.set_num_planning_attempts(10)
        self.arm.set_planning_time(15.0)
        self.planning_frame = self.arm.get_planning_frame()

        rospy.loginfo(f"🔧 Planning frame: {self.planning_frame}")

        self.sm = smach.StateMachine(outcomes=['succeeded', 'failure'], input_keys=["goal"])
        sis = IntrospectionServer('SMACH_VIEW_SERVER', self.sm, '/PLACE_ACTION')
        sis.start()

        with self.sm:
            smach.StateMachine.add('CREATE_BOUND', smach.CBState(self.create_bound, outcomes=['success', 'failed']),
                                   transitions={'success':'APPROACH', 'failed':'failure'})
            smach.StateMachine.add('APPROACH', smach.CBState(self.approach, outcomes=['success', 'failed', 'cancel'], input_keys=["goal"]),
                                   transitions={'success':'RETREAT', 'failed':'failure', 'cancel':'failure'})
            smach.StateMachine.add('RETREAT', smach.CBState(self.retreat, outcomes=['success', 'failed'], input_keys=["goal"]),
                                   transitions={'success':'succeeded', 'failed': 'failure'})

        self.wrapper = ActionServerWrapper("place_server", PickPlaceAction,
                                           wrapped_container=self.sm,
                                           succeeded_outcomes=["succeeded"],
                                           aborted_outcomes=["failure"],
                                           goal_key='goal',
                                           result_key="action_done")
        self.wrapper.run_server()

    def create_bound(self, userdata):
        self.arm.set_start_state_to_current_state()
        rospy.sleep(1.0)
        return 'success'

    def publish_marker(self, pose):
        marker = Marker()
        marker.header.frame_id = self.planning_frame
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose = pose
        marker.scale.x = marker.scale.y = marker.scale.z = 0.05
        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.lifetime = rospy.Duration(10.0)
        self.marker_pub.publish(marker)

    def approach(self, userdata):
        self.approach_count += 1
        if self.approach_count > self.approach_limit:
            return 'cancel'

        goal_pose = userdata.goal.target_pose

        rospy.loginfo(f"Incoming goal frame: {goal_pose.header.frame_id}")
        rospy.loginfo(f"Pose: x={goal_pose.pose.position.x}, y={goal_pose.pose.position.y}, z={goal_pose.pose.position.z}")

        if goal_pose.header.frame_id == "odom":
            rospy.logwarn("No mobile base present; replacing 'odom' frame with 'world'.")
            goal_pose.header.frame_id = "world"

        self.scene.remove_world_object()
        rospy.sleep(1.0)

        current_joints = self.arm.get_current_joint_values()
        rospy.loginfo(f" Current joint values: {current_joints}")

        try:
            if goal_pose.header.frame_id != self.planning_frame:
                tf_goal = self.tf2_buffer.transform(goal_pose, self.planning_frame, rospy.Duration(2.0))
                rospy.loginfo(f" Transformed to planning frame '{self.planning_frame}': x={tf_goal.pose.position.x}, y={tf_goal.pose.position.y}, z={tf_goal.pose.position.z}")
            else:
                tf_goal = goal_pose
                rospy.loginfo(f" Skipped TF transform, using pose directly in planning frame '{self.planning_frame}': x={tf_goal.pose.position.x}, y={tf_goal.pose.position.y}, z={tf_goal.pose.position.z}")
        except (tf2_ros.LookupException, tf2_ros.ExtrapolationException, tf2_ros.TransformException) as e:
            rospy.logerr(f" TF Transform failed: {e}")
            return 'failed'

        self.publish_marker(tf_goal.pose)

        self.arm.stop()
        self.arm.clear_pose_targets()
        self.arm.set_start_state_to_current_state()

        self.arm.set_goal_orientation_tolerance(0.5)
        self.arm.set_pose_target(tf_goal.pose)

        success, plan, planning_time, error_code = self.arm.plan()
        if success and hasattr(plan, 'joint_trajectory') and len(plan.joint_trajectory.points) > 0:
            rospy.loginfo(f" Planning succeeded with {len(plan.joint_trajectory.points)} points in {planning_time:.2f}s.")
            self.arm.execute(plan, wait=True)
        else:
            rospy.logwarn(f" Planning failed: {error_code}")
            return 'failed'

        self.arm.stop()
        self.arm.clear_pose_targets()
        return 'success'

    def retreat(self, userdata):
        self.gripper.open()
        rospy.sleep(1.0)
        self.arm.set_named_target("home")
        success = self.arm.go(wait=True)
        self.arm.stop()
        return 'success' if success else 'failed'

    def add_collision_object(self, name='object', position=[0, 0, 0], rotation=[0,0,0,1], dimensions=[0.3,0.3,0.3], frame='link_base'):
        object_pose = PoseStamped()
        object_pose.header.frame_id = frame
        object_pose.pose.position.x = position[0]
        object_pose.pose.position.y = position[1]
        object_pose.pose.position.z = position[2]
        object_pose.pose.orientation.x = rotation[0]
        object_pose.pose.orientation.y = rotation[1]
        object_pose.pose.orientation.z = rotation[2]
        object_pose.pose.orientation.w = rotation[3]
        self.scene.add_box(name, object_pose, size=dimensions)

if __name__ == '__main__':
    rospy.init_node('placing_action')
    placing_sm = PlacingStateMachine()
    rospy.spin()
