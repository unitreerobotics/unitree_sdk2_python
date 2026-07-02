import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.r1.loco.r1_loco_client import LocoClient


def string_to_float_list(value: str):
    return [float(item) for item in value.replace(",", " ").split()]


def parse_args(argv):
    args = {"network_interface": "lo"}
    for arg in argv[1:]:
        if arg.startswith("--"):
            key_value = arg[2:].split("=", 1)
            key = key_value[0]
            value = key_value[1] if len(key_value) == 2 else ""
            args[key] = value.strip('"')
        elif args["network_interface"] == "lo":
            args["network_interface"] = arg
        else:
            raise ValueError(f"unexpected argument: {arg}")
    return args


def parse_bool(value: str):
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError(f"invalid bool argument: {value}")


def main():
    args = parse_args(sys.argv)
    ChannelFactoryInitialize(0, args["network_interface"])

    client = LocoClient()
    client.Init()
    client.SetTimeout(10.0)

    for key, value in args.items():
        if key == "network_interface":
            continue

        print(f"Processing command: [{key}] with param: [{value}] ...")

        if key == "get_fsm_id":
            code, fsm_id = client.GetFsmId()
            print(f"ret: {code}, current fsm_id: {fsm_id}")
        elif key == "get_fsm_mode":
            code, fsm_mode = client.GetFsmMode()
            print(f"ret: {code}, current fsm_mode: {fsm_mode}")
        elif key == "set_fsm_id":
            print(f"ret: {client.SetFsmId(int(value))}")
        elif key == "set_velocity":
            param = string_to_float_list(value)
            if len(param) == 3:
                param.append(1.0)
            if len(param) != 4:
                raise ValueError(f"invalid param size for set_velocity: {len(param)}")
            print(f"ret: {client.SetVelocity(param[0], param[1], param[2], param[3])}")
        elif key == "damp":
            print(f"ret: {client.Damp()}")
        elif key == "start":
            print(f"ret: {client.Start()}")
        elif key == "stand_up":
            print(f"ret: {client.StandUp()}")
        elif key == "zero_torque":
            print(f"ret: {client.ZeroTorque()}")
        elif key == "stop_move":
            print(f"ret: {client.StopMove()}")
        elif key == "switch_move_mode":
            print(f"ret: {client.SwitchMoveMode(parse_bool(value))}")
        elif key == "move":
            param = string_to_float_list(value)
            if len(param) != 3:
                raise ValueError(f"invalid param size for move: {len(param)}")
            print(f"ret: {client.Move(param[0], param[1], param[2])}")
        elif key == "set_speed_mode":
            print(f"ret: {client.SetSpeedMode(int(value))}")
        else:
            raise ValueError(f"unknown command: {key}")

        print("Done!")


if __name__ == "__main__":
    main()
