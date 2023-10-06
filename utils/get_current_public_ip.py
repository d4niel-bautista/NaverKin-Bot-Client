import subprocess

async def get_current_public_ip():
    public_ip = subprocess.Popen('''powershell -command "Invoke-RestMethod -Uri 'https://ifconfig.me' -UseBasicParsing"''', stdout=subprocess.PIPE).communicate()[0].decode().strip()
    return public_ip