from pathlib import Path
import sys

SDK_ROOT = (
    Path(__file__).resolve().parent.parent
    / "fairino-python-sdk-main"
    / "linux"
)

sys.path.insert(0, str(SDK_ROOT))

from fairino import Robot


def connect_robot(ip="192.168.57.2"):
    robot = Robot.RPC(ip)
    return robot
