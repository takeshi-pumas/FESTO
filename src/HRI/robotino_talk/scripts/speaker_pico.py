#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import subprocess
import os

# install: sudo apt install libttspico-utils

class PicoTTSNode:
    def __init__(self):
        rospy.init_node('speaker_node')
        rospy.Subscriber('/robot_speech', String, self.say_callback)
        self.tmp_wav = "/tmp/pico_output.wav"
        self.language = "en-US"  # Cambia a 'es-ES' para español o en-US

    def say_callback(self, msg):
        text = msg.data
        rospy.loginfo("Speaking: %s", text)

        # Generar archivo de audio con pico2wave
        cmd_generate = ['pico2wave', '-l', self.language, '-w', self.tmp_wav, text]
        subprocess.call(cmd_generate)

        # Reproducir el archivo con aplay
        subprocess.call(['aplay', self.tmp_wav])

        # Eliminar el archivo temporal
        os.remove(self.tmp_wav)

    def run(self):
        rospy.loginfo("PicoTTS node is ready. Listening on /robot_speech...")
        rospy.spin()

if __name__ == '__main__':
    try:
        node = PicoTTSNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
