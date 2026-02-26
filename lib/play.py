#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝

import cv2
import time
import os
import sys
import shutil
import numpy as np
 
 


class Player:

    def __init__(self, run_duration=None):
        self.run_duration = run_duration

     
        self.ascii_chars = np.array(list(
            " .'`^\",:;Il!i~+_-?][}{1)(|\\/"
            "tfjrxnuvczXYUJCLQ0OZmwqpdbkhao"
            "*#MW&8%B@$"
        ))

        self.char_ratio = 0.3

 
    def frame_to_ascii_color(self, frame):

        term_size = shutil.get_terminal_size()
        canvas_width = term_size.columns
        canvas_height = int(term_size.lines * 0.95)

        h, w, _ = frame.shape
        aspect_ratio = h / w
        new_height = int(aspect_ratio * canvas_width * self.char_ratio)

        if new_height > canvas_height:
            new_height = canvas_height

        resized = cv2.resize(frame, (canvas_width, new_height))

        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        indices = (
            gray.astype(np.int32) * (len(self.ascii_chars) - 1) // 255
        )

        output_lines = []

        for y in range(new_height):
            line = []
            for x in range(canvas_width):

                r, g, b = resized[y, x][2], resized[y, x][1], resized[y, x][0]
                char = self.ascii_chars[indices[y, x]]
                line.append(f"\033[38;2;{r};{g};{b}m{char}")

            output_lines.append("".join(line))

        return "\n".join(output_lines) + "\033[0m"

 
    def play(self, rtsp='', title="RTSP Player",
             width=420, height=340, mode="origin"):

        if not rtsp:
          
            return False

        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = \
            "rtsp_transport;tcp|fflags;nobuffer|flags;low_delay"

        cap = cv2.VideoCapture(rtsp, cv2.CAP_FFMPEG)

        if not cap.isOpened():
          
            return False

        if mode == "origin":
            cv2.namedWindow(title, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(title, width, height)

        if mode == "ascii":
            print("\033[?25l", end="")   
            print("\033[2J", end="")     

        start_time = time.time()

        try:
            while True:

                if self.run_duration:
                    if time.time() - start_time >= self.run_duration:
                        break

                if mode == "origin":
                    if cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) < 1:
                        break

                ret, frame = cap.read()

                if not ret:
                    cap.release()
                    time.sleep(0.5)
                    cap = cv2.VideoCapture(rtsp, cv2.CAP_FFMPEG)
                    continue

                if mode == "origin":
                    cv2.imshow(title, frame)
                    cv2.waitKey(1)

                elif mode == "ascii":
                    ascii_frame = self.frame_to_ascii_color(frame)
                    print("\033[H", end="")    
                    print(ascii_frame)

        except KeyboardInterrupt:
            pass

        finally:
            cap.release()
            cv2.destroyAllWindows()

            if mode == "ascii":
                print("\033[?25h", end="")   
                print("\033[0m")

 


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage:")
        print("python play.py <rtsp_url> <title> [origin|ascii]")
        sys.exit(1)

    url = sys.argv[1]
    title = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "origin"

    p = Player()
    p.play(rtsp=url, title=title, mode=mode)