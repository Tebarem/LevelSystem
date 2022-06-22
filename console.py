import curses,time
import curses.textpad
from datetime import datetime,date
import threading
import os
from typing import Counter

class Console:
    def __init__(self):
        self.running = False
        self.executing = True
        mainThread = threading.Thread(target=self.start_console,args=(),daemon=True)
        mainThread.start()
        
        while not self.running and self.executing:
            pass
    
    def start_console(self):
        curses.wrapper(self.run)
    
    def print(self,text, color=0):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        with open(self.file,"a") as f:
            if color == 1:
                f.write(f"[{current_time}] WARN {text}\n")
            elif color == 2:
                f.write(f"[{current_time}] ERROR {text}\n")
            else:
                f.write(f"[{current_time}] {text}\n")
            f.close()
        
        self.window.addstr(f"[{current_time}] {text}\n",curses.color_pair(color))
        self.window.refresh()
        self.inputWindow.refresh()
    
    def run(self, screen):
        try:
            self.screen = screen
            if curses.has_colors():
                curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
                curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
            self.h,self.w = screen.getmaxyx()
            self.window = curses.newwin(self.h-2,self.w,0,0)
            self.InputContainer = curses.newwin(1,self.w,self.h-1,0)
            self.window.scrollok(True)
            self.inputWindow = curses.newwin(1,self.w-2,self.h-1,2)
            self.inputField = curses.textpad.Textbox(self.inputWindow,insert_mode=True)
            self.InputContainer.addstr('> ')
            self.window.addstr(0,0,"Console Application started\n")
            today = date.today()
            today = today.strftime("%m%d%y")
            now = datetime.now()
            current_time = now.strftime("%H-%M-%S")
            self.file = f"logs/{today}-{current_time}.txt"
            screen.refresh()
            self.window.refresh()
            self.InputContainer.refresh()
            self.running = True
            self.print("Console Application started", 1)
            while self.running:
                rows, cols = self.screen.getmaxyx()
                userIn = self.inputField.edit()[:-1]
                if userIn!="":
                    # remove half of whatever userIn is
                    userIn = userIn
                    if str(userIn)=="stop":
                        self.inputWindow.refresh()
                        self.inputWindow.clear()
                        self.print("Stopping...",9)
                        time.sleep(1)
                        self.running = False
                        os._exit(1)
                    self.print(f"Comamnd: {userIn}")
                self.inputWindow.refresh()
                self.inputWindow.clear()
                self.window.refresh()
        except Exception as e:
            print(e)
            self.executing = False
    
if __name__ == "__main__":
    console = Console()
    
    while console.running:
        console.print("Hello World")
        time.sleep(1)