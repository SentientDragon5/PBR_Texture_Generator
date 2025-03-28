import tkinter as tk
from tkinter import filedialog, ttk
import os
import pbr_gen
import subprocess  # For opening folders

def select_images():
    """Opens a file dialog to select multiple image files and displays them."""
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")])
    if file_paths:
        image_list.delete(0, tk.END)  # Clear the list
        for file_path in file_paths:
            image_list.insert(tk.END, file_path)

def generate_textures():
    """Generates textures for all selected images and opens the output folder."""
    selected_albedo = albedo_var.get()
    selected_normal = normal_var.get()
    selected_roughness = roughness_var.get()
    selected_metallic = metallic_var.get()

    output_folders = [] # Keep track of output folders to open later

    for i in range(image_list.size()):
        image_path = image_list.get(i)
        output_folder = os.path.splitext(os.path.basename(image_path))[0] + "_textures"
        pbr_gen.generate_pbr_textures(image_path, output_folder, selected_albedo, selected_normal, selected_roughness, selected_metallic)
        output_folders.append(output_folder)

    if output_folders:
        open_output_folders(output_folders)

def open_output_folders(folders):
    """Opens the specified folders using the default file explorer."""
    for folder in folders:
        if os.path.exists(folder):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder)
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.Popen(['open', folder])  # macOS
                    # subprocess.Popen(['xdg-open', folder])  # Linux (use this if 'open' doesn't work)
            except OSError as e:
                print(f"Error opening folder {folder}: {e}")
        else:
            print(f"Folder {folder} does not exist.")

# Create the main window
root = tk.Tk()
root.title("PBR Texture Generator")

# Listbox to display selected images
image_list = tk.Listbox(root, selectmode=tk.SINGLE, width=60)
image_list.pack(pady=10)

# Button to select images
select_button = tk.Button(root, text="Select Images", command=select_images)
select_button.pack(pady=5)

# Albedo selection
albedo_var = tk.StringVar(value="copy")
albedo_label = tk.Label(root, text="Albedo:")
albedo_label.pack()
albedo_menu = ttk.Combobox(root, textvariable=albedo_var, values=["none", "copy"], state="readonly")
albedo_menu.pack()

# Normal selection
normal_var = tk.StringVar(value="sobel")
normal_label = tk.Label(root, text="Normal:")
normal_label.pack()
normal_menu = ttk.Combobox(root, textvariable=normal_var, values=["none", "sobel"], state="readonly")
normal_menu.pack()

# Roughness selection
roughness_var = tk.StringVar(value="gaussian")
roughness_label = tk.Label(root, text="Roughness:")
roughness_label.pack()
roughness_menu = ttk.Combobox(root, textvariable=roughness_var, values=["none", "gaussian"], state="readonly")
roughness_menu.pack()

# Metallic selection
metallic_var = tk.StringVar(value="hsv")
metallic_label = tk.Label(root, text="Metallic:")
metallic_label.pack()
metallic_menu = ttk.Combobox(root, textvariable=metallic_var, values=["none", "hsv"], state="readonly")
metallic_menu.pack()

# Generate textures button
generate_button = tk.Button(root, text="Generate Textures", command=generate_textures)
generate_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()