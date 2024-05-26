import tkinter as tk
from tkinter import ttk, colorchooser, filedialog

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paint App")

        # Define variables for brush color, size, and shape
        self.brush_color = "black"
        self.brush_size = 2
        self.brush_shape = tk.ROUND
        self.is_drawing = False
        self.last_x, self.last_y = None, None
        self.drawn_objects = []

        # Function to handle drawing on canvas
        def start_drawing(event):
            self.is_drawing = True
            self.last_x, self.last_y = event.x, event.y

        def continue_drawing(event):
            if self.is_drawing:
                if self.last_x is not None and self.last_y is not None:
                    self.drawn_objects.append(self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                                                  fill=self.brush_color, width=self.brush_size,
                                                                  capstyle=self.brush_shape, smooth=True))
                self.last_x, self.last_y = event.x, event.y

        def stop_drawing(event):
            self.is_drawing = False
            self.last_x, self.last_y = None, None

        # Function to change the brush color
        def change_color():
            color = colorchooser.askcolor()
            if color[1]:
                self.brush_color = color[1]

        # Function to change the brush size
        def change_size(new_size):
            self.brush_size = new_size

        # Function to change the brush shape
        def change_shape(new_shape):
            self.brush_shape = new_shape

        # Function to clear the screen
        def clear_screen():
            for obj in self.drawn_objects:
                self.canvas.delete(obj)

        # Function to save the drawing
        def save_drawing():
            filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if filename:
                self.canvas.postscript(file=filename + ".eps", colormode='color')
                img = tk.PhotoImage(master=self.root, width=800, height=600)
                self.canvas.postscript(file=filename + ".eps", colormode='color')
                img.write(filename + ".png", format="png")
                self.canvas.delete("all")

        # Function to load a saved drawing
        def load_drawing():
            filename = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
            if filename:
                img = tk.PhotoImage(file=filename)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)

        # Create frame for controls
        control_frame = tk.Frame(root, bg="#e6e6e6", padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Create gradient background
        gradient_canvas = tk.Canvas(control_frame, width=200, height=600, highlightthickness=0)
        gradient_canvas.pack(fill=tk.BOTH, expand=True)
        self.create_gradient(gradient_canvas, (204, 255, 255), (153, 204, 255))

        # Create custom buttons
        style = ttk.Style()
        style.configure("TButton", background="#99ccff", foreground="black", font=("Arial", 10, "bold"))
        color_button = ttk.Button(control_frame, text="Pick Color", command=change_color)
        color_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        size_frame = tk.Frame(control_frame, bg="#e6e6e6")
        size_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        size_label = tk.Label(size_frame, text="Brush Size:", bg="#e6e6e6", font=("Arial", 10, "bold"))
        size_label.pack(side=tk.LEFT, padx=5)
        sizes = [1, 3, 5, 7, 10]
        for size in sizes:
            size_button = ttk.Button(size_frame, text=str(size), width=3, command=lambda s=size: change_size(s))
            size_button.pack(side=tk.LEFT, padx=5)
        shape_frame = tk.Frame(control_frame, bg="#e6e6e6")
        shape_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        shape_label = tk.Label(shape_frame, text="Brush Shape:", bg="#e6e6e6", font=("Arial", 10, "bold"))
        shape_label.pack(side=tk.LEFT, padx=5)
        shapes = [tk.ROUND, tk.BUTT, tk.PROJECTING]
        shape_names = ["Round", "Square", "Projecting"]
        for shape, name in zip(shapes, shape_names):
            shape_button = ttk.Button(shape_frame, text=name, width=7, command=lambda s=shape: change_shape(s))
            shape_button.pack(side=tk.LEFT, padx=5)
        clear_button = ttk.Button(control_frame, text="Clear", command=clear_screen)
        clear_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        save_button = ttk.Button(control_frame, text="Save", command=save_drawing)
        save_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        load_button = ttk.Button(control_frame, text="Load", command=load_drawing)
        load_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

        # Create canvas for drawing
        canvas_frame = tk.Frame(root, bg="white", padx=10, pady=10)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_frame, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind drawing functions to canvas events
        self.canvas.bind("<Button-1>", start_drawing)
        self.canvas.bind("<B1-Motion>", continue_drawing)
        self.canvas.bind("<ButtonRelease-1>", stop_drawing)

    def create_gradient(self, canvas, color1, color2):
        width = canvas.winfo_reqwidth()
        height = canvas.winfo_reqheight()
        for i in range(height):
            r = int(color1[0] + (color2[0] - color1[0]) * (i / height))
            g = int(color1[1] + (color2[1] - color1[1]) * (i / height))
            b = int(color1[2] + (color2[2] - color1[2]) * (i / height))
            color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            canvas.create_line(0, i, width, i, fill=color, width=1)

def main():
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

