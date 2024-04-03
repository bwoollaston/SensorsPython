"""Example for reading singals for every n samples."""

import re
import nidaqmx
import ttkthemes
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import TerminalConfiguration
from nidaqmx.system.physical_channel import PhysicalChannel, _PhysicalChannelAlternateConstructor
from nidaqmx.utils import unflatten_channel_string, flatten_channel_string
import tkinter as tk
from tkinter import ttk
from Tooltip import Tooltip
from ttkthemes import ThemedTk
from tkinter import messagebox

def average(lst):
    if not lst:  # Handle empty list
        return 0
    return sum(lst) / float(len(lst))

def ai_continuous_start(sample_rate, sample_interval):
    app.task.stop() #stop task, doesnt need to be running but this makes sure it isn't
    if(len(app.task.ai_channels)<1):
        app.task.ai_channels.add_ai_voltage_chan(f"{app.cboDevice.get()}/{app.cboAIChannels.get()}", max_val=10, min_val=-10, terminal_config=TerminalConfiguration.DIFF)
    app.task.register_every_n_samples_acquired_into_buffer_event(sample_interval, None) #unregister callback by passing null reference
    app.task.timing.cfg_samp_clk_timing(sample_rate, sample_mode=AcquisitionType.CONTINUOUS)
    app.task.register_every_n_samples_acquired_into_buffer_event(sample_interval, ai_callback)
    app.task.start()
    return

def ai_callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data):
    try:
        samples = []
        samples = app.task.read(int(number_of_samples))
        app.current_voltage.set(f"{average(samples): .3f} {app.MEASUREMENT_UNITS}")
        return 0
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        app.end_handler()
# class encapsulating a control and its label
class Label_ctrl_item(ttk.Frame):
    def __init__(self, parent, control, label_text):
        super().__init__(parent)
        self.columns = 1
        self.rows = 3
        self.parent = parent
        self.columnconfigure(0, minsize=80)
        self.columnconfigure(1, minsize=100)
        self.label = ttk.Label(self, text=label_text)
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.control = control
        self.control.grid(row=parent.row_count, column=1, padx=5, pady=5)
        self.control.bind("<FocusIn>", self.update_values)
    def update_values(self, event=None):
        parent_values = self.control.cget("values")  # Get the values from the parent control
        self.control["values"] = parent_values  # Set the values of the child control

# main application view
class MainApplication(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Define class constants
        self.MEASUREMENT_UNITS = "V"

        # Define class variables
        self.row_count = 1
        self.current_voltage = tk.StringVar()
        self.current_voltage.set( "0.00 V")
        # Instantiate class objects
        self.samples = []
        self.task = nidaqmx.Task("task_ai_continuous")

        self.label_ = ttk.Label(self, text="Application")

        self.AIChannels = []
        self.cboAIChannels = ttk.Combobox(self, values=self.AIChannels)
        self.labeled_control_AIChannels = Label_ctrl_item(self, self.cboAIChannels, "Analog In Channel")

        self.Devices = []
        self.get_devices(self.Devices)
        self.cboDevice = ttk.Combobox(self, values=self.Devices)
        self.cboDevice.current(0)
        self.cboDevice.bind("<<ComboboxSelected>>", self.device_changed(event=None,sender=self))
        self.labeled_control_devices = Label_ctrl_item(self, self.cboDevice, "Device Name")

        self.txtMeasurement = ttk.Label(self, textvariable=self.current_voltage)
        self.labeled_control_measurement = Label_ctrl_item(self, self.txtMeasurement, "Voltage [V]")

        self.btnStart = ttk.Button(self, text="Start Measurement", command=self.start_handler, style='Start.TButton')
        self.btnEnd = ttk.Button(self, text="End Measurement", command=self.end_handler, state=tk.DISABLED)

        # Add objects to the frame
        self.apply_grid(self, [1,1,1,1,1], [1,1])
        self.label_.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
        self.grid_pack(self.labeled_control_devices)
        self.grid_pack(self.labeled_control_AIChannels)
        self.grid_pack(self.labeled_control_measurement)
        self.btnStart.grid(row=self.row_count,column=0, padx=5, pady=5)
        self.btnEnd.grid(row=self.row_count,column=1, padx=5, pady=5)

        self.ttDevice = Tooltip(self.cboDevice, "Select DAQ device")

    # method to apply item to grid
    def grid_pack(self, item):
        self.grid_rowconfigure(self.row_count, weight=1)
        item.grid(row=self.row_count, column=0, padx=5, pady=5)
        item.control.grid(row=self.row_count, column=1, padx=5, pady=5)
        # item.control.grid(row=self.row_count,column=1, padx=5, pady=5)
        self.row_count += 1

    # method to apply a grid to frame
    def apply_grid(self, widget, rows, columns):
        for row_index, row_weight in enumerate(rows):
            widget.grid_rowconfigure(row_index, weight=row_weight)
        for col_index, col_weight in enumerate(columns):
            widget.grid_columnconfigure(col_index, weight=col_weight)

    def start_handler(self):
        self.cboDevice.config(state=tk.DISABLED)
        self.cboAIChannels.config(state=tk.DISABLED)
        self.btnStart.config(state=tk.DISABLED)
        self.btnEnd.config(state=tk.NORMAL)
        ai_continuous_start(1000,1000)
    # invoked on end button click
    def end_handler(self):
        self.cboDevice.config(state=tk.NORMAL)
        self.cboAIChannels.config(state=tk.NORMAL)
        self.btnStart.config(state=tk.NORMAL)
        self.btnEnd.config(state=tk.DISABLED)
        self.task.stop()

    def device_changed(self, event, sender):
        selected_item = sender.cboDevice.get()
        sender.cboAIChannels.values = []
        if selected_item is not None:
            index = sender.cboDevice.current()
            d = devices[index]
            for c in d.ai_physical_chans:
                sender.AIChannels.append(re.sub(f"{selected_item}/","",c.name))  # list of channels in selected device d
            sender.cboAIChannels["values"] = sender.AIChannels
            sender.cboAIChannels.current(0)
        return

    def get_devices(self,list):
        devs = system.System.local()
        for d in devs.devices:
            devices.append(d)
            list.append(d.name)

def on_closing():
    app.task.close()
    print("Task destroyed")
    root.destroy()

if __name__ == "__main__":
    system = nidaqmx.system
    devices = []
    root = ThemedTk(theme="arc")

    # IMPOTANT: close your tasks when leaving the program with a closing event handler
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.geometry("400x300")
    app = MainApplication(root)
    app.grid(row=0, column=0, padx=5, pady=5)
    root.mainloop()