from tkinter import Tk, Label
from cv2 import VideoCapture, cvtColor, COLOR_BGR2RGB
from ctypes import windll, create_unicode_buffer, WINFUNCTYPE, wintypes
from PIL import Image, ImageTk
from keyboard import on_press_key, unhook_all
from os import getenv, path, listdir, mkdir
from json import loads
from playsound import playsound
from shutil import move
from threading import Thread
from time import sleep

import sys

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)

class OBS(Tk):

    def __init__(self) -> None:
        super().__init__()
        self.wm_title("OBS Tools")
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(bg="white")
        self.wm_attributes("-transparentcolor", "white")
        self.path: str = getenv("APPDATA") + "\\obs-studio"
        self.display: Label = None
        self.cap: VideoCapture = None
        self.recording: bool = False
        self.recording_window: str = None
        self.events: list = []
        self.loop()

    def resetKeybinds(self) -> None:
        unhook_all()
        profile = None
        replay_buffer = []
        start_recording = []
        stop_recording = []
        start_stop_mutual = []
        try:
            with open(self.path + "\\global.ini", "r") as f:
                for line in f.readlines():
                    if line.startswith("Profile="):
                        profile = line.split("=", 1)[1].strip()
                        break
        except:
            pass
        if profile:
            try:
                with open(self.path + "\\basic\\profiles\\" + profile + "\\basic.ini", "r") as f:
                    for line in f.readlines():
                        if line.startswith("ReplayBuffer={\"ReplayBuffer.Save\":") and len(replay_buffer) == 0:
                            try:
                                for bind in loads(line.split("={\"ReplayBuffer.Save\":", 1)[1].strip()[:-1]):
                                    key = ""
                                    if "control" in bind.keys():
                                        if bind["control"]:
                                            key += "CTRL+"
                                    if "alt" in bind.keys():
                                        if bind["alt"]:
                                            key += "ALT+"
                                    if "shift" in bind.keys():
                                        if bind["shift"]:
                                            key += "SHIFT+"
                                    key += bind["key"].replace("OBS_KEY_", "")
                                    replay_buffer.append(key)
                            except:
                                continue
                        elif line.startswith("OBSBasic.StartRecording={\"bindings\":") and len(start_recording) == 0:
                            try:
                                for bind in loads(line.split("={\"bindings\":", 1)[1].strip()[:-1]):
                                    key = ""
                                    if "control" in bind.keys():
                                        if bind["control"]:
                                            key += "CTRL+"
                                    if "alt" in bind.keys():
                                        if bind["alt"]:
                                            key += "ALT+"
                                    if "shift" in bind.keys():
                                        if bind["shift"]:
                                            key += "SHIFT+"
                                    key += bind["key"].replace("OBS_KEY_", "")
                                    start_recording.append(key)
                            except:
                                continue
                        elif line.startswith("OBSBasic.StopRecording={\"bindings\":") and len(stop_recording) == 0:
                            try:
                                for bind in loads(line.split("={\"bindings\":", 1)[1].strip()[:-1]):
                                    key = ""
                                    if "control" in bind.keys():
                                        if bind["control"]:
                                            key += "CTRL+"
                                    if "alt" in bind.keys():
                                        if bind["alt"]:
                                            key += "ALT+"
                                    if "shift" in bind.keys():
                                        if bind["shift"]:
                                            key += "SHIFT+"
                                    key += bind["key"].replace("OBS_KEY_", "")
                                    stop_recording.append(key)
                            except:
                                continue
            except:
                pass
        for key in start_recording:
            if key in stop_recording:
                start_recording.remove(key)
                stop_recording.remove(key)
                start_stop_mutual.append(key)
        for key in replay_buffer:
            on_press_key(key, self.replayBuffer)
        for key in start_recording:
            on_press_key(key,  self.startRecording)
        for key in stop_recording:
            on_press_key(key, self.stopRecording)
        for key in start_stop_mutual:
            on_press_key(key, self.toggleRecording)

    def replayBuffer(self, key: str) -> None:
        hwnd = windll.user32.GetForegroundWindow()
        length = windll.user32.GetWindowTextLengthW(hwnd)
        buf = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        thread = Thread(target=self.saveRecording, args=[buf.value if buf.value else "Desktop"])
        thread.daemon = True
        thread.start()
        self.events.append("saved.gif")

    def startRecording(self, key: str) -> None:
        if not self.recording:
            self.recording = True
            hwnd = windll.user32.GetForegroundWindow()
            length = windll.user32.GetWindowTextLengthW(hwnd)
            buf = create_unicode_buffer(length + 1)
            windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            self.recording_window = buf.value if buf.value else "Desktop"
            self.events.append("started.gif")

    def stopRecording(self, key: str) -> None:
        if self.recording:
            self.recording = False
            thread = Thread(target=self.saveRecording, args=[self.recording_window])
            thread.daemon = True
            thread.start()
            self.recording_window = None
            self.events.append("saved.gif")

    def toggleRecording(self, key: str) -> None:
        if self.recording:
            thread = Thread(target=self.saveRecording, args=[self.recording_window])
            thread.daemon = True
            thread.start()
            self.recording_window = None
            self.events.append("saved.gif")
        else:
            hwnd = windll.user32.GetForegroundWindow()
            length = windll.user32.GetWindowTextLengthW(hwnd)
            buf = create_unicode_buffer(length + 1)
            windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            self.recording_window = buf.value if buf.value else "Desktop"
            self.events.append("started.gif")
            playsound("started.mp3")
        self.recording = not self.recording

    def saveRecording(self, title: str) -> None:
        profile = None
        recording_path = None
        try:
            with open(self.path + "\\global.ini", "r") as f:
                for line in f.readlines():
                    if line.startswith("Profile="):
                        profile = line.split("=", 1)[1].strip()
                        break
        except:
            pass
        if profile:
            try:
                with open(self.path + "\\basic\\profiles\\" + profile + "\\basic.ini", "r") as f:
                    for line in f.readlines():
                        if line.startswith("RecFilePath="):
                            recording_path = line.split("=", 1)[1].strip().replace("/", "\\")
                            break
            except:
                pass
            if recording_path:
                try:
                    attempts = 0
                    count = listdir(recording_path)
                    while count == listdir(recording_path):
                        if attempts > 60:
                            return
                        attempts += 1
                        sleep(1)
                    absolute_path = recording_path + "\\" + title
                    latest_file = max([path.join(recording_path, recording) for recording in listdir(recording_path)], key=path.getctime)
                    new_path = absolute_path + "\\" + path.basename(latest_file)
                    if not path.exists(absolute_path):
                        mkdir(absolute_path)
                    move(latest_file, new_path)
                except:
                    pass

    def shouldRun(self) -> bool:
        hwnd = windll.user32.GetForegroundWindow()
        length = windll.user32.GetWindowTextLengthW(hwnd)
        buf = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        obs_active = False
        @WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def enum_proc(hWnd, lParam):
            nonlocal obs_active
            length = windll.user32.GetWindowTextLengthW(hWnd)
            buf = create_unicode_buffer(length + 1)
            windll.user32.GetWindowTextW(hWnd, buf, length + 1)
            if "obs" in buf.value.lower():
                obs_active = True
            return True
        windll.user32.EnumWindows(enum_proc, 0)
        return buf.value != "Settings" and obs_active

    def checkDisplay(self) -> None:
        self.geometry(f"-0+{int(windll.user32.GetSystemMetrics(1) / 6)}")
        if not self.display:
            self.display = Label(self, bd=0)
            self.display.pack()
            self.resetKeybinds()

    def destroyDisplay(self) -> None:
        self.display.destroy()
        self.display = None
        self.cap = None

    def loop(self) -> None:
        if self.shouldRun():
            self.checkDisplay()
            if not self.cap and len(self.events) > 0:
                self.cap = VideoCapture(resource_path("assets/" + self.events.pop(0)))
            if self.cap:
                ret, frame = self.cap.read()
                if ret:
                    img = Image.fromarray(cvtColor(frame, COLOR_BGR2RGB)).convert("RGBA")
                    imgtk = ImageTk.PhotoImage(master=self.display, image=img)
                    self.display.imgtk = imgtk
                    self.display.configure(image=imgtk)
                else:
                    self.destroyDisplay()
        self.after(10, self.loop)

if __name__ == "__main__":
    OBS().mainloop()