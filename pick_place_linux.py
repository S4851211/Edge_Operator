from pathlib import Path
import json
import sys
import time

SDK_ROOT = Path(__file__).resolve().parent / "fairino-python-sdk-main" / "linux"
sys.path.insert(0, str(SDK_ROOT))

from fairino import Robot

ROBOT_IP = "192.168.57.2"

POINTS_FILE = Path(__file__).resolve().with_name(
    "pick_place_points.json"
)

TOOL = 2
USER = 0

SPEED = 35
APPROACH_Z_MM = 150

# True = teach points
# False = run cycle
DRY_RUN = False

USE_GRIPPER = True

GRIPPER_INDEX = 1
OPEN_POS = 50
CLOSE_POS = 90

GRIPPER_VEL = 30
GRIPPER_FORCE = 40
MAX_TIME_MS = 30000

COMPANY = 6
DEVICE = 0
SOFT_VERSION = 0
BUS = 0


def require_ok(name, result):

    code = result[0] if isinstance(result, tuple) else result

    print(f"{name}: {result}")

    if code != 0:
        raise RuntimeError(
            f"{name} failed with code {code}"
        )

    return result


def connect():

    print("Connecting to robot...")

    robot = Robot.RPC(ROBOT_IP)

    if not getattr(robot, "is_connect", False):

        controller_ip = robot.robot.GetControllerIP()

        print(
            f"Controller IP: {controller_ip}"
        )

        Robot.RPC.is_connect = True

        print(
            "Using XML-RPC mode."
        )

    return robot


def prepare_robot(robot):

    reset = getattr(
        robot,
        "ResetAllError",
        None
    )

    if reset is not None:

        print(
            "ResetAllError:",
            reset()
        )

        time.sleep(1)

    require_ok(
        "RobotEnable",
        robot.RobotEnable(1)
    )

    mode_result = robot.Mode(0)

    print(
        "Mode Auto:",
        mode_result
    )

    if mode_result not in [0, 123]:

        raise RuntimeError(
            f"Mode failed: {mode_result}"
        )


def setup_gripper(robot):

    require_ok(
        "SetGripperConfig",
        robot.SetGripperConfig(
            company=COMPANY,
            device=DEVICE,
            softversion=SOFT_VERSION,
            bus=BUS,
        ),
    )

    require_ok(
        "ActGripper reset",
        robot.ActGripper(
            index=GRIPPER_INDEX,
            action=0,
        ),
    )

    time.sleep(1)

    require_ok(
        "ActGripper enable",
        robot.ActGripper(
            index=GRIPPER_INDEX,
            action=1,
        ),
    )

    time.sleep(2)


def move_gripper(
    robot,
    position,
    label
):

    require_ok(
        label,
        robot.MoveGripper(
            index=GRIPPER_INDEX,
            pos=position,
            vel=GRIPPER_VEL,
            force=GRIPPER_FORCE,
            maxtime=MAX_TIME_MS,
            block=0,
            type=0,
            rotNum=0,
            rotVel=0,
            rotTorque=0,
        ),
    )

    time.sleep(1)


def get_tcp(robot, label):

    input(
        f"\nMove robot to {label} "
        f"and press Enter..."
    )

    error, pose = robot.GetActualTCPPose()

    if error != 0:

        raise RuntimeError(
            f"GetActualTCPPose "
            f"failed: {error}"
        )

    print(
        f"{label}: {pose}"
    )

    return pose


def save_points(
    pick,
    place
):

    data = {
        "pick": pick,
        "place": place,
        "tool": TOOL,
        "user": USER,
        "approach_z_mm": APPROACH_Z_MM,
    }

    POINTS_FILE.write_text(
        json.dumps(
            data,
            indent=2
        ),
        encoding="utf-8",
    )

    print(
        f"\nSaved points:\n"
        f"{POINTS_FILE}"
    )


def load_points():

    if not POINTS_FILE.exists():

        raise FileNotFoundError(
            f"{POINTS_FILE} not found"
        )

    data = json.loads(
        POINTS_FILE.read_text(
            encoding="utf-8"
        )
    )

    return (
        data["pick"],
        data["place"]
    )


def above(pose):

    target = pose.copy()

    target[2] += APPROACH_Z_MM

    return target


def move_l(
    robot,
    pose,
    label
):

    print(
        f"\nMoveL -> {label}"
    )

    print(pose)

    result = robot.MoveL(
        desc_pos=pose,
        tool=TOOL,
        user=USER,
        vel=SPEED,
    )

    print(
        "MoveL result:",
        result
    )

    require_ok(
        label,
        result
    )


def teach_points(robot):

    print(
        "\n=== TEACH MODE ==="
    )

    pick = get_tcp(
        robot,
        "PICK"
    )

    place = get_tcp(
        robot,
        "PLACE"
    )

    save_points(
        pick,
        place
    )

    print(
        "\nTeaching complete."
    )


def run_cycle(robot):

    prepare_robot(robot)

    if USE_GRIPPER:
        setup_gripper(robot)

    pick, place = load_points()

    print("\nPick:", pick)
    print("Place:", place)

    input(
        "\nPress Enter to "
        "start cycle..."
    )

    if USE_GRIPPER:

        print(
            "\nOpening gripper..."
        )

        move_gripper(
            robot,
            OPEN_POS,
            "open gripper"
        )

    move_l(
        robot,
        above(pick),
        "above pick"
    )

    move_l(
        robot,
        pick,
        "pick"
    )

    if USE_GRIPPER:

        print(
            "\nClosing gripper..."
        )

        move_gripper(
            robot,
            CLOSE_POS,
            "close gripper"
        )

    move_l(
        robot,
        above(pick),
        "lift from pick"
    )

    move_l(
        robot,
        above(place),
        "above place"
    )

    move_l(
        robot,
        place,
        "place"
    )

    if USE_GRIPPER:

        print(
            "\nOpening gripper..."
        )

        move_gripper(
            robot,
            OPEN_POS,
            "release object"
        )

    move_l(
        robot,
        above(place),
        "lift from place"
    )

    print(
        "\nPick and place "
        "cycle completed."
    )


def main():

    robot = connect()

    if DRY_RUN:
        teach_points(robot)
    else:
        run_cycle(robot)


if __name__ == "__main__":
    main()