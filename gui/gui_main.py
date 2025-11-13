# gui/gui_main.py
import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import csv
from collections import deque
import cv2
from PIL import Image, ImageTk

class ParkingGUI:
    def __init__(self, system):
        self.system = system
        self.root = tk.Tk()
        self.root.title("🚗 Parking Management System")
        self.root.geometry("1000x720")

        # Modernize ttk theme and styles
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self._configure_styles()

        # Layout: header, content
        self.header = ttk.Frame(self.root, style="Header.TFrame")
        self.header.pack(fill=tk.X)
        self._build_header(self.header)

        # Layout: left video, right sidebar for info/logs
        self.container = ttk.Frame(self.root, style="Body.TFrame")
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = ttk.Frame(self.container)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = ttk.Frame(self.container, width=320)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Video area
        self.video_label = ttk.Label(self.left_frame, style="Video.TLabel")
        self.video_label.pack(pady=10, fill=tk.BOTH, expand=True)

        # Controls and status
        self.status_label = ttk.Label(self.right_frame, text="[SYSTEM] Waiting for Arduino response...", style="Subtle.TLabel")
        self.status_label.pack(pady=(0,8))

        self.price_label = ttk.Label(self.right_frame, text=f"Price: ₹{self.system.price_per_min}/min", style="Accent.TLabel")
        self.price_label.pack(pady=(0,8))

        self.refresh_btn = ttk.Button(self.right_frame, text="Manual Capture", style="Primary.TButton", command=self.manual_capture)
        self.refresh_btn.pack(pady=(0,10), fill=tk.X)

        # Logs table
        ttk.Label(self.right_frame, text="Recent Logs", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.log_frame = ttk.Frame(self.right_frame)
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("Plate", "Entry", "Exit", "Minutes", "Cost")
        self.log_table = ttk.Treeview(self.log_frame, columns=columns, show="headings", height=18, style="Logs.Treeview")
        for col in columns:
            self.log_table.heading(col, text=col)
            self.log_table.column(col, width=110 if col == "Plate" else 160, anchor=tk.CENTER)
        vsb = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.log_table.yview)
        self.log_table.configure(yscrollcommand=vsb.set)
        self.log_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview row tags for animation
        self.log_table.tag_configure("highlight", background="#FFF3CD")  # soft amber
        self.log_table.tag_configure("normal", background="")

        # Track shown logs for incremental updates
        self._displayed_log_keys = set()

        self.stop_flag = False

        # Start background serial listener
        threading.Thread(target=self.listen_serial, daemon=True).start()

        # Start UI-driven loops (avoid cross-thread UI updates)
        self.update_video()
        self.refresh_logs()

    def update_video(self):
        """Show live camera feed in GUI without flicker using Tk after()"""
        if self.stop_flag:
            return
        ret, frame = self.system.camera.read()
        if ret and frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            # Keep a reference to avoid garbage collection
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
        # schedule next frame on main thread
        self.root.after(33, self.update_video)  # ~30 FPS

    def listen_serial(self):
        """Continuously listen for Arduino signals"""
        while not self.stop_flag:
            self.system.process_serial_input()
            time.sleep(0.1)

    def refresh_logs(self):
        """Incrementally append new rows from parking_log.csv into the table with highlight."""
        if self.stop_flag:
            return
        try:
            if os.path.exists("parking_log.csv"):
                new_rows = []
                with open("parking_log.csv", newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    for row in reader:
                        if not row:
                            continue
                        key = tuple(row)
                        if key not in self._displayed_log_keys:
                            self._displayed_log_keys.add(key)
                            new_rows.append(row)
                for row in new_rows:
                    item_id = self.log_table.insert("", tk.END, values=row, tags=("highlight",))
                    # animate highlight fade-out
                    self._animate_log_row(item_id)
                # Keep only last 100 rows visible
                children = self.log_table.get_children()
                if len(children) > 100:
                    for iid in children[:len(children)-100]:
                        self.log_table.delete(iid)
        except Exception as e:
            # Update status but do not crash GUI
            self.status_label.config(text=f"[LOG ERROR] {e}")
        finally:
            self.root.after(800, self.refresh_logs)

    def _animate_log_row(self, item_id):
        """Simple pulse effect: transition highlight bg to normal over short steps."""
        # Sequence of colors from highlight to normal
        pulse_colors = [
            "#FFF3CD",  # start
            "#FFF7DA",
            "#FFFBE8",
            "#FFFFFF"   # end
        ]
        def step(i=0):
            if i < len(pulse_colors):
                self.log_table.tag_configure("highlight", background=pulse_colors[i])
                self.root.after(120, lambda: step(i+1))
            else:
                # reset to normal
                self.log_table.item(item_id, tags=("normal",))
        step()

    def _build_header(self, parent):
        icon = ttk.Label(parent, text="🚗", style="HeaderIcon.TLabel")
        icon.pack(side=tk.LEFT, padx=(12,6), pady=8)
        title = ttk.Label(parent, text="Parking Management System", style="HeaderTitle.TLabel")
        title.pack(side=tk.LEFT, pady=8)
        # Spacer
        ttk.Label(parent, text="", style="Header.TFrame").pack(side=tk.LEFT, expand=True)
        # Live price on header too
        self.header_price = ttk.Label(parent, text=f"₹{self.system.price_per_min}/min", style="HeaderPrice.TLabel")
        self.header_price.pack(side=tk.RIGHT, padx=12, pady=8)

    def _configure_styles(self):
        bg = "#0f172a"        # slate-900
        panel = "#111827"     # gray-900
        card = "#1f2937"      # gray-800
        accent = "#22c55e"    # green-500
        subtle = "#9ca3af"    # gray-400

        self.root.configure(bg=bg)
        self.style.configure("Header.TFrame", background=panel)
        self.style.configure("Body.TFrame", background=bg)

        self.style.configure("HeaderIcon.TLabel", background=panel, foreground="#f8fafc")
        self.style.configure("HeaderTitle.TLabel", background=panel, foreground="#f8fafc", font=("Segoe UI", 14, "bold"))
        self.style.configure("HeaderPrice.TLabel", background=panel, foreground=accent, font=("Segoe UI", 12, "bold"))

        self.style.configure("Video.TLabel", background=card)
        self.style.configure("Subtle.TLabel", background=bg, foreground=subtle, font=("Segoe UI", 10))
        self.style.configure("Accent.TLabel", background=bg, foreground=accent, font=("Segoe UI", 11, "bold"))
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))
        # Treeview styling
        self.style.configure("Logs.Treeview",
                             background=card,
                             fieldbackground=card,
                             foreground="#e5e7eb",
                             rowheight=22)
        self.style.configure("Vertical.TScrollbar", troughcolor=panel)
        self.style.map("Primary.TButton",
                       background=[("!disabled", accent)],
                       foreground=[("!disabled", "#062e0f")])

    def manual_capture(self):
        """Manually trigger plate recognition"""
        plate = self.system.capture_and_recognize()
        if plate:
            self.status_label.config(text=f"[MANUAL] Detected plate: {plate}")
        else:
            self.status_label.config(text="[MANUAL] No plate detected")

    def run(self):
        self.root.mainloop()
        self.stop_flag = True
