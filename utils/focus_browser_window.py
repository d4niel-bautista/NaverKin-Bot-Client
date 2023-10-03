import win32gui, win32com.client
import asyncio

async def get_all_windows(window_name_keywords):
    result = []
    def winEnumHandler(hwnd, ctx):
        for keyword in window_name_keywords:
            if win32gui.IsWindowVisible(hwnd) and 'Google Chrome' in win32gui.GetWindowText(hwnd):
                if win32gui.GetWindowText(hwnd) == keyword or keyword in win32gui.GetWindowText(hwnd):
                    result.append(hwnd)
    win32gui.EnumWindows(winEnumHandler, None)
    return result

async def bring_browser_to_front(window_name_keywords=['지식iN', 'Naver Sign in', 'Knowledge iN']):
    windows = await get_all_windows(window_name_keywords)
    if windows:
        for hwnd in windows:
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                win32com.client.Dispatch("WScript.Shell").SendKeys('%')
                win32gui.SetForegroundWindow(hwnd)
            await asyncio.sleep(0.2)