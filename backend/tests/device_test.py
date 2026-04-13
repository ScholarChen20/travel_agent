import subprocess
import platform

def get_device_id():
    """获取设备ID"""
    try:
        system = platform.system()
        
        if system == "Windows":
            command = "wmic csproduct get uuid"
            result = subprocess.check_output(command, shell=True).decode().strip()
            device_id = result.split("\n")[1].strip()
        elif system == "Linux":
            command = "sudo dmidecode -s system-uuid"
            result = subprocess.check_output(command, shell=True).decode().strip()
            device_id = result.strip()
        else:
            print(f"不支持的操作系统: {system}")
            return None
        
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
    print(get_device_id())
    # print(get_device_id_new())
    # print(get_device_id_old())