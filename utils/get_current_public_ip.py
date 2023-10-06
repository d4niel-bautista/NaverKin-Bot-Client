import subprocess

async def get_current_public_ip():
    public_ip = subprocess.call("curl ifconfig.me")
    return public_ip