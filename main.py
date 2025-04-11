import subprocess
import time
import pyautogui
from pynput import mouse
from pynput import keyboard
import math
import threading

click_event = threading.Event()
exit_event = threading.Event()

threads = []


def on_click(x, y, button, pressed):
    if pressed:
        print(f"Clicked at ({x}, {y})")
        click_event.set()
        
        time.sleep(0.5)  # Small delay to ensure the click is registered
        activeWindow = pyautogui.getActiveWindow()
        
        if activeWindow is None:
            print("No active window found.")
        else:
            threads.append(spiralThread(activeWindow, resizeSpeed=1, radiusRate=5, angleRate=40, timeStep=0.01))
            print(f"Active window title: {activeWindow.title}")

            
    
def on_press(key):
    try:
        if key.char.lower() == 'q' or key.char.lower() == 'c' or key.esc:
            print("Exiting...")
            exit_event.set()
            return False
    except AttributeError:
        pass

def getActiveWindow():
    activeWindow = pyautogui.getActiveWindow()
    if activeWindow is not None:
        print(f"Active window title: {activeWindow.title}")
        return activeWindow
    else:
        print("No active window found.")
        return None

def cartesian_to_polar(x, y):
    r = (x**2 + y**2) ** 0.5
    theta = math.atan2(y, x)  # Angle in radians
    return r, theta

def archimedian_spiral(r, theta):
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y

def expand(activeWindow, resizeRate : int, resizeRateMultiplier : int):
    screenWidth, screenHeight = pyautogui.size()
    #screenCenter = (screenWidth // 2, screenHeight // 2 - activeWindow.size[1])

    activeWindow.moveTo(0, 0)
    while activeWindow.size[0] < screenWidth:
        activeWindow.resize(resizeRate*resizeRateMultiplier, resizeRate*resizeRateMultiplier)

    time.sleep(0.01)
    activeWindow.close()

def draw_spiral(activeWindow, resizeSpeed : int, radiusRate : int, angleRate : int, timeStep : float):
    screenWidth, screenHeight = pyautogui.size()
    screenCenter = (screenWidth // 2, screenHeight // 2)
    r = 1000
    theta = 0
    while(r > 1):
        screenWindowCenter = (screenCenter[0] - activeWindow.size[0] // 2, screenCenter[1] - activeWindow.size[1] // 2)
        x, y = archimedian_spiral(r, theta)

        activeWindow.moveTo(screenWindowCenter[0] + int(x), screenWindowCenter[1] + int(y))  # Scale the coordinates
        if activeWindow.size[0] > 1 and activeWindow.size[1] > 1:
            activeWindow.resize(-resizeSpeed,-resizeSpeed)  # Decrement the window size with each iteration
            
            
        
        if r <= radiusRate:
            r = 1
        else:
            r -= radiusRate

        theta += math.pi / angleRate  # Decrement the angle

        time.sleep(timeStep)    

    expand(activeWindow, resizeRate=resizeSpeed, resizeRateMultiplier=100)

def spiralThread(activeWindow, resizeSpeed : int, radiusRate : int, angleRate : int, timeStep : float):
    spiral_thread = threading.Thread(target=draw_spiral, args=(activeWindow, resizeSpeed, radiusRate, angleRate, timeStep), daemon=True)
    spiral_thread.start()
    return spiral_thread

def print_info():
    print("Click the window to collapse")
    print("Press Q, Esc or C to exit")

def main():

    print_info()
    
    running = True

    keyboardListener = keyboard.Listener(on_press=on_press)
    keyboardListener.start()

    mouseListener = mouse.Listener(on_click=on_click)
    mouseListener.start()

    while running:
        time.sleep(1)
        if exit_event.is_set():
            mouseListener.stop()
            keyboardListener.stop()
            running = False
            break
        
        if click_event.is_set():
           print_info()
           click_event.clear()

        
        
            

if __name__ == "__main__":
    main()