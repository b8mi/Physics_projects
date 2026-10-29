import tkinter as tk
from math import radians, sin, cos, sqrt, atan2, degrees

def center_windows(window, width, height, x_pos, y_pos):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = x_pos
    y_coordinate = screen_height - height - y_pos
    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = (screen_width - width) // 2
    y_coordinate = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

def r_result(r, rangle, last_mod):
    wind = tk.Tk()
    wind.title("RESULT")

    r_formatted = "{:.3f}".format(r)
    rangle_formatted = "{:.3f}".format(rangle)
    last_mod_formatted = "{:.3f}".format(last_mod)

    error_label = tk.Label(wind, text=f"The total = {r_formatted}", font=("Arial", 12))
    error_label.pack()

    error_label = tk.Label(wind, text=f"Theta Θ = {rangle_formatted}", font=("Arial", 12))
    error_label.pack()

    error_label = tk.Label(wind, text=f"fixed theta Θ = {last_mod_formatted}", font=("Arial", 12))
    error_label.pack()

    ok_button = tk.Button(wind, text="Done", command=wind.destroy, font=("Arial", 12))
    ok_button.pack()
    
    wind.mainloop()

def show_error_window(message):
    error_window = tk.Tk()
    error_window.title("Error")

    error_label = tk.Label(error_window, text=message, font=("Arial", 12))
    error_label.pack()

    ok_button = tk.Button(error_window, text="UNDERSTOOD", command=error_window.destroy, font=("Arial", 12))
    ok_button.pack()

    error_window.mainloop()

def clear_data():
    angle.clear()
    speed.clear()
    cos_vector.clear()
    sin_vector.clear()
    ry.clear()
    rx.clear()


    canvas.delete("all")
    for i in range(0, canvas_height, 20):
        color = "black" if i == canvas_height // 2 else "lightgray"  
        canvas.create_line(0, i, canvas_width, i, fill=color)

    for i in range(0, canvas_width, 20):
        color = "black" if i == canvas_width // 2 else "lightgray"  
        canvas.create_line(i, 0, i, canvas_height, fill=color)


def submit_num_vectors():
    num_vectors_input = entry.get()

    if not num_vectors_input:
        show_error_window("Please don't leave the number of vectors empty.")
        return

    if not num_vectors_input.isdigit():
        show_error_window("Please enter a valid number for the number of vectors.")
        return

    num_vectors = int(num_vectors_input)
    vector_properties_frame.pack(side="left", fill="both", expand=True)
    coordinate_grid_frame.pack(side="right", fill="both", expand=True)
    root.update()
    create_vector_name_window(num_vectors)

def create_vector_name_window(num_vectors):
    vector_index = [1]  
    angle_index = [1]   

    def submit_vector_name(angle, speed, cos_vector, sin_vector, ry, rx):
        speed_value = vector_entry.get()
        angle_value = angle_entry.get()
        
        if not speed_value.strip() or not angle_value.strip():
            show_warning_window("Please don't leave vector properties empty.")
            return
        
        if not speed_value.strip().isdigit() or not angle_value.strip().isdigit():
            show_warning_window("Please enter a valid number for the property.")
            return

        speed.append(speed_value)
        angle.append(angle_value)

        vector_entry.delete(0, tk.END)  
        angle_entry.delete(0, tk.END)
        vector_index[0] += 1
        angle_index[0] = 1  
        vector_label.config(text="Enter speed of Vector " + str(vector_index[0]) + ":", font=("Arial", 12))
        angle_label.config(text="Enter angle of Vector " + str(vector_index[0]) + ":", font=("Arial", 12))
        
        draw_lines_from_center(angle, speed)

        if vector_index[0] > num_vectors:
            print("Angles:", angle)
            print("Speeds:", speed)
            
            for i in range(len(speed)):
                cos_value = float(speed[i]) * cos(radians(float(angle[i])))
                sin_value = float(speed[i]) * sin(radians(float(angle[i])))
                cos_vector.append(cos_value)
                sin_vector.append(sin_value)

            print("Cosine Vector:", cos_vector)
            print("Sine Vector:", sin_vector)
            
            rys = sum(sin_vector)
            rxs = sum(cos_vector)
            ry.append(0)  
            rx.append(0)  
            
            for i in range(len(ry)):
                if i != len(ry):
                    ry[i] += rys
                    rx[i] += rxs
                elif i == len(ry):
                    ry.append(rys)
                    rx.append(rxs)

            total_rx = sum(rx)
            total_ry = sum(ry)
            print("total_rx:", total_rx)
            print("total_ry:", total_ry)

            r = sqrt(total_ry ** 2 + total_rx ** 2)
  

            r_angle = degrees(atan2(total_ry, total_rx))
            print("\nR:", r)
            print("Mod r_angle:", r_angle)

            last_r = r_angle+180
            draw_vector_r(r, last_r)

            print("Fixed r_angle:", last_r)
            last_mod = last_r - 360
            
            vector_name_window.destroy() 
            r_result(r, last_r, r_angle)


    def show_warning_window(message):
        warning_window = tk.Tk()
        warning_window.title("Warning")

        warning_label = tk.Label(warning_window, text=message, font=("Arial", 12))
        warning_label.pack()

        ok_button = tk.Button(warning_window, text="UNDERSTOOD", command=warning_window.destroy, font=("Arial", 12))
        ok_button.pack()

        warning_window.mainloop()

    def draw_lines_from_center(angle, speed):
        print("\n\n\n\n\n\n\n")
        for ang, spd in zip(angle, speed):
            spd_float = float(spd)
            x = (spd_float * cos(radians(float(ang))))
            y = (spd_float * sin(radians(float(ang)))) 
            
            x_end = x
            y_end = -y
            
            print(f"x{float(x_end):.3f}, y{float(y_end):.3f}")


            x_end += canvas_width // 2
            y_end += canvas_height // 2
            

            canvas.create_line(canvas_width // 2, canvas_height // 2, x_end, y_end, fill="blue")

    def draw_vector_r(length, angle):
        x_end = length * cos(radians(angle))
        y_end = -length * sin(radians(angle))

        x_end += canvas_width // 2
        y_end += canvas_height // 2

        canvas.create_line(canvas_width // 2, canvas_height // 2, x_end, y_end, fill="red")
        
        opposite_angle = angle + 180 
        x_end_opposite = length * cos(radians(opposite_angle))
        y_end_opposite = -length * sin(radians(opposite_angle))
        
        x_end_opposite += canvas_width // 2
        y_end_opposite += canvas_height // 2
        
        canvas.create_line(canvas_width // 2, canvas_height // 2, x_end_opposite, y_end_opposite, fill="green")

    vector_name_window = tk.Tk()
    vector_name_window.title("Properties")

    widthr = 300  
    heightr = 200  
    center_windows(vector_name_window, widthr, heightr, 250, 230)

    vector_label = tk.Label(vector_name_window, text="Enter speed of Vector " + str(vector_index[0]) + ":", font=("Arial", 12))
    vector_label.pack()

    vector_entry = tk.Entry(vector_name_window, font=("Arial", 12))
    vector_entry.pack()

    angle_label = tk.Label(vector_name_window, text="Enter angle of Vector " + str(vector_index[0]) + ":", font=("Arial", 12))
    angle_label.pack()

    angle_entry = tk.Entry(vector_name_window, font=("Arial", 12))
    angle_entry.pack()

    submit_button = tk.Button(vector_name_window, text="Submit", command=lambda: submit_vector_name(angle, speed, cos_vector, sin_vector, ry, rx), font=("Arial", 12))
    submit_button.pack()

    vector_name_window.mainloop()

root = tk.Tk()
root.title("Vectors Grapher") 

width = 800  
height = 400  
center_window(root, width, height)

vector_properties_frame = tk.Frame(root)
coordinate_grid_frame = tk.Frame(root)

label = tk.Label(vector_properties_frame, text="Enter the number of vectors:", font=("Arial", 14))
label.pack()

entry = tk.Entry(vector_properties_frame, font=("Arial", 14))
entry.pack()

submit_button = tk.Button(vector_properties_frame, text="Submit", command=submit_num_vectors, font=("Arial", 14))
submit_button.pack(side="top", pady=(0, 5))

button_frame = tk.Frame(vector_properties_frame)
button_frame.pack(side="top")

clear_button = tk.Button(button_frame, text="Clear", command=clear_data, font=("Arial", 14))
clear_button.pack(side="left", padx=(0, 5))

canvas_width = width // 2
canvas_height = height
canvas = tk.Canvas(coordinate_grid_frame, bg="white", width=canvas_width, height=canvas_height)
canvas.pack()

for i in range(0, canvas_height, 20):
    color = "black" if i == canvas_height // 2 else "lightgray"  
    canvas.create_line(0, i, canvas_width, i, fill=color)

for i in range(0, canvas_width, 20):
    color = "black" if i == canvas_width // 2 else "lightgray"  
    canvas.create_line(i, 0, i, canvas_height, fill=color)

vector_properties_frame.pack(side="left", fill="both", expand=True)
coordinate_grid_frame.pack(side="right", fill="both", expand=True)

angle = []
speed = []
cos_vector = []
sin_vector = []
ry = []
rx = []

root.mainloop()
