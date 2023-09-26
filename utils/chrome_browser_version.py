import subprocess

async def get_chrome_browser_version() -> int:
    version = subprocess.Popen('''powershell -command "&{(Get-Item 'C:\Program Files\Google\Chrome\Application\chrome.exe').VersionInfo.ProductVersion}"''', stdout=subprocess.PIPE).communicate()[0].decode().strip()
    print('Chrome browser version:', version)
    major_version = int(version.split('.')[0])
    return major_version