# generated from genmsg/cmake/pkg-genmsg.cmake.em

message(STATUS "face_recog: 3 messages, 1 services")

set(MSG_I_FLAGS "-Iface_recog:/home/robotino/FESTO/src/HRI/face_recog/msg;-Istd_msgs:/opt/ros/noetic/share/std_msgs/cmake/../msg;-Isensor_msgs:/opt/ros/noetic/share/sensor_msgs/cmake/../msg;-Igeometry_msgs:/opt/ros/noetic/share/geometry_msgs/cmake/../msg")

# Find all generators
find_package(gencpp REQUIRED)
find_package(geneus REQUIRED)
find_package(genlisp REQUIRED)
find_package(gennodejs REQUIRED)
find_package(genpy REQUIRED)

add_custom_target(face_recog_generate_messages ALL)

# verify that message/service dependencies have not changed since configure



get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg" NAME_WE)
add_custom_target(_face_recog_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "face_recog" "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg" ""
)

get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg" NAME_WE)
add_custom_target(_face_recog_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "face_recog" "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg" "sensor_msgs/Image:std_msgs/Header"
)

get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg" NAME_WE)
add_custom_target(_face_recog_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "face_recog" "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg" "std_msgs/String"
)

get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv" NAME_WE)
add_custom_target(_face_recog_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "face_recog" "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv" "face_recog/Floats:std_msgs/Header:face_recog/Image:face_recog/Strings:sensor_msgs/Image:std_msgs/String"
)

#
#  langs = gencpp;geneus;genlisp;gennodejs;genpy
#

### Section generating for lang: gencpp
### Generating Messages
_generate_msg_cpp(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/face_recog
)
_generate_msg_cpp(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/face_recog
)
_generate_msg_cpp(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/face_recog
)

### Generating Services
_generate_srv_cpp(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv"
  "${MSG_I_FLAGS}"
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg;/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/face_recog
)

### Generating Module File
_generate_module_cpp(face_recog
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/face_recog
  "${ALL_GEN_OUTPUT_FILES_cpp}"
)

add_custom_target(face_recog_generate_messages_cpp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)
add_dependencies(face_recog_generate_messages face_recog_generate_messages_cpp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_cpp _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_cpp _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_cpp _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv" NAME_WE)
add_dependencies(face_recog_generate_messages_cpp _face_recog_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(face_recog_gencpp)
add_dependencies(face_recog_gencpp face_recog_generate_messages_cpp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS face_recog_generate_messages_cpp)

### Section generating for lang: geneus
### Generating Messages
_generate_msg_eus(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/face_recog
)
_generate_msg_eus(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/face_recog
)
_generate_msg_eus(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/face_recog
)

### Generating Services
_generate_srv_eus(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv"
  "${MSG_I_FLAGS}"
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg;/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/face_recog
)

### Generating Module File
_generate_module_eus(face_recog
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/face_recog
  "${ALL_GEN_OUTPUT_FILES_eus}"
)

add_custom_target(face_recog_generate_messages_eus
  DEPENDS ${ALL_GEN_OUTPUT_FILES_eus}
)
add_dependencies(face_recog_generate_messages face_recog_generate_messages_eus)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_eus _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_eus _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_eus _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv" NAME_WE)
add_dependencies(face_recog_generate_messages_eus _face_recog_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(face_recog_geneus)
add_dependencies(face_recog_geneus face_recog_generate_messages_eus)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS face_recog_generate_messages_eus)

### Section generating for lang: genlisp
### Generating Messages
_generate_msg_lisp(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/face_recog
)
_generate_msg_lisp(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/face_recog
)
_generate_msg_lisp(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/face_recog
)

### Generating Services
_generate_srv_lisp(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv"
  "${MSG_I_FLAGS}"
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg;/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/face_recog
)

### Generating Module File
_generate_module_lisp(face_recog
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/face_recog
  "${ALL_GEN_OUTPUT_FILES_lisp}"
)

add_custom_target(face_recog_generate_messages_lisp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_lisp}
)
add_dependencies(face_recog_generate_messages face_recog_generate_messages_lisp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_lisp _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_lisp _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_lisp _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv" NAME_WE)
add_dependencies(face_recog_generate_messages_lisp _face_recog_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(face_recog_genlisp)
add_dependencies(face_recog_genlisp face_recog_generate_messages_lisp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS face_recog_generate_messages_lisp)

### Section generating for lang: gennodejs
### Generating Messages
_generate_msg_nodejs(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/face_recog
)
_generate_msg_nodejs(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/face_recog
)
_generate_msg_nodejs(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/face_recog
)

### Generating Services
_generate_srv_nodejs(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv"
  "${MSG_I_FLAGS}"
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg;/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/face_recog
)

### Generating Module File
_generate_module_nodejs(face_recog
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/face_recog
  "${ALL_GEN_OUTPUT_FILES_nodejs}"
)

add_custom_target(face_recog_generate_messages_nodejs
  DEPENDS ${ALL_GEN_OUTPUT_FILES_nodejs}
)
add_dependencies(face_recog_generate_messages face_recog_generate_messages_nodejs)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_nodejs _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_nodejs _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_nodejs _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv" NAME_WE)
add_dependencies(face_recog_generate_messages_nodejs _face_recog_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(face_recog_gennodejs)
add_dependencies(face_recog_gennodejs face_recog_generate_messages_nodejs)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS face_recog_generate_messages_nodejs)

### Section generating for lang: genpy
### Generating Messages
_generate_msg_py(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/face_recog
)
_generate_msg_py(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/face_recog
)
_generate_msg_py(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/face_recog
)

### Generating Services
_generate_srv_py(face_recog
  "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv"
  "${MSG_I_FLAGS}"
  "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg;/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg;/opt/ros/noetic/share/sensor_msgs/cmake/../msg/Image.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/String.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/face_recog
)

### Generating Module File
_generate_module_py(face_recog
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/face_recog
  "${ALL_GEN_OUTPUT_FILES_py}"
)

add_custom_target(face_recog_generate_messages_py
  DEPENDS ${ALL_GEN_OUTPUT_FILES_py}
)
add_dependencies(face_recog_generate_messages face_recog_generate_messages_py)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Floats.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_py _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Image.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_py _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/msg/Strings.msg" NAME_WE)
add_dependencies(face_recog_generate_messages_py _face_recog_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/robotino/FESTO/src/HRI/face_recog/srv/RecognizeFace.srv" NAME_WE)
add_dependencies(face_recog_generate_messages_py _face_recog_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(face_recog_genpy)
add_dependencies(face_recog_genpy face_recog_generate_messages_py)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS face_recog_generate_messages_py)



if(gencpp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/face_recog)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/face_recog
    DESTINATION ${gencpp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_cpp)
  add_dependencies(face_recog_generate_messages_cpp std_msgs_generate_messages_cpp)
endif()
if(TARGET sensor_msgs_generate_messages_cpp)
  add_dependencies(face_recog_generate_messages_cpp sensor_msgs_generate_messages_cpp)
endif()

if(geneus_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/face_recog)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/face_recog
    DESTINATION ${geneus_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_eus)
  add_dependencies(face_recog_generate_messages_eus std_msgs_generate_messages_eus)
endif()
if(TARGET sensor_msgs_generate_messages_eus)
  add_dependencies(face_recog_generate_messages_eus sensor_msgs_generate_messages_eus)
endif()

if(genlisp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/face_recog)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/face_recog
    DESTINATION ${genlisp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_lisp)
  add_dependencies(face_recog_generate_messages_lisp std_msgs_generate_messages_lisp)
endif()
if(TARGET sensor_msgs_generate_messages_lisp)
  add_dependencies(face_recog_generate_messages_lisp sensor_msgs_generate_messages_lisp)
endif()

if(gennodejs_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/face_recog)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/face_recog
    DESTINATION ${gennodejs_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_nodejs)
  add_dependencies(face_recog_generate_messages_nodejs std_msgs_generate_messages_nodejs)
endif()
if(TARGET sensor_msgs_generate_messages_nodejs)
  add_dependencies(face_recog_generate_messages_nodejs sensor_msgs_generate_messages_nodejs)
endif()

if(genpy_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/face_recog)
  install(CODE "execute_process(COMMAND \"/usr/bin/python3\" -m compileall \"${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/face_recog\")")
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/face_recog
    DESTINATION ${genpy_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_py)
  add_dependencies(face_recog_generate_messages_py std_msgs_generate_messages_py)
endif()
if(TARGET sensor_msgs_generate_messages_py)
  add_dependencies(face_recog_generate_messages_py sensor_msgs_generate_messages_py)
endif()
