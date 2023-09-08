import win32gui
import pyautogui
import time

def get_all_windows(window_name_keywords):
    result = []
    def winEnumHandler(hwnd, ctx):
        for keyword in window_name_keywords:
            if win32gui.IsWindowVisible(hwnd) and 'Google Chrome' in win32gui.GetWindowText(hwnd) and win32gui.GetWindowText(hwnd) == keyword or keyword in win32gui.GetWindowText(hwnd):
                result.append(hwnd)
    win32gui.EnumWindows(winEnumHandler, None)
    return result

def bring_browser_to_front(window_name_keywords=['지식iN', 'Naver Sign in', 'Knowledge iN']):
    windows = get_all_windows(window_name_keywords)
    if windows:
        for hwnd in windows:
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pyautogui.press("alt")
                win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)