import subprocess

def get_device_id():
    """获取设备ID"""
    try:
        command = "wmic csproduct get uuid"   # Windows 获取主板id
        # command = "sudo dmidecode -s system-uuid"   # Linux 获取主板id
        result = subprocess.check_output(command, shell=True).decode().strip()

        device_id = result.split("\n")[1].strip()
        return device_id
    except Exception as e:
        print(f"Error: {e}")
    return None


import socket
def get_device_id_new():
    """获取设备ID"""
    return socket.gethostname()


def get_device_id_old():
    """获取设备ID"""
    try:
        # command = "dmidecode -s baseboard-serial-number"
        command = "ifconfig | grep 'ether' | awk '{print $2}'"
        result = subprocess.check_output(command, shell=True).decode().strip()
        return result
    except Exception as e:
        print(f"Error: {e}")
    return None


if __name__ == "__main__":
    # print(get_device_id())
    # print(get_device_id_new())
    print(get_device_id_old())