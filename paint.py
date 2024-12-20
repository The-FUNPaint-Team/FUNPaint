import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, simpledialog
from PIL import Image, ImageTk

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
        self.current_stroke = []
        self.drawn_objects = []
        self.undo_stack = []
        self.redo_stack = []

        self.mode = "draw"  # "draw" or "erase" or "text"
        self.selected_item = None
        self.drag_data = {"item": None, "x": 0, "y": 0}

        # Create frame for controls
        control_frame = tk.Frame(root, bg="#e6e6e6")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # Create custom buttons
        ttk.Button(control_frame, text="Clear", command=self.clear_screen).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Insert Image", command=self.insert_image).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Color", command=self.change_color).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Size", command=self.select_size).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Shape", command=self.select_shape).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Eraser", command=lambda: self.set_mode("erase")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Text", command=lambda: self.set_mode("text")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Brush", command=self.switch_to_brush).pack(side=tk.LEFT, padx=5, pady=5)

        # Create canvas for drawing
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind drawing functions to canvas events
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.continue_drawing)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        self.canvas.bind("<Alt-Button-1>", self.select_item)
        self.canvas.bind("<Alt-B1-Motion>", self.drag_item)
        self.canvas.bind("<Alt-ButtonRelease-1>", self.release_item)

    def start_drawing(self, event):
        if event.state & 0x008:  # Check if Alt key is pressed
            self.select_item(event)
            return
        if self.mode == "draw" or self.mode == "erase":
            self.is_drawing = True
            self.last_x, self.last_y = event.x, event.y
            self.current_stroke = []
        elif self.mode == "text":
            text = simpledialog.askstring("Input", "Enter text:", parent=self.root)
            if text:
                obj = self.canvas.create_text(event.x, event.y, text=text, fill=self.brush_color,
                                              font=("Arial", self.brush_size), tags="draggable")
                self.drawn_objects.append(obj)
                self.undo_stack.append(('create', [obj]))
                if len(self.undo_stack) > 20:
                    self.undo_stack.pop(0)
                self.redo_stack.clear()

    def continue_drawing(self, event):
        if event.state & 0x008:  # Check if Alt key is pressed
            self.drag_item(event)
            return
        if self.is_drawing:
            if self.last_x is not None and self.last_y is not None:
                if self.mode == "draw" or self.mode == "erase":
                    color = self.brush_color if self.mode == "draw" else "white"
                    obj = self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                                  fill=color, width=self.brush_size,
                                                  capstyle=self.brush_shape, smooth=True)
                    self.current_stroke.append(obj)
            self.last_x, self.last_y = event.x, event.y

    def stop_drawing(self, event):
        if self.is_drawing:
            self.is_drawing = False
            self.last_x, self.last_y = None, None
            if self.current_stroke:
                self.drawn_objects.extend(self.current_stroke)
                self.undo_stack.append(('create', self.current_stroke))
                if len(self.undo_stack) > 20:
                    self.undo_stack.pop(0)
                self.redo_stack.clear()
                self.current_stroke = []

    def change_color(self):
        color = colorchooser.askcolor()
        if color[1]:
            self.brush_color = color[1]

    def select_size(self):
        new_size = simpledialog.askinteger("Size", "Enter brush size:")
        if new_size:
            self.brush_size = new_size

    def select_shape(self):
        shape = simpledialog.askstring("Shape", "Enter brush shape (ROUND, BUTT, PROJECTING):")
        if shape in ['ROUND', 'BUTT', 'PROJECTING']:
            self.brush_shape = getattr(tk, shape)

    def clear_screen(self):
        for obj in self.drawn_objects:
            self.canvas.delete(obj)
        self.drawn_objects.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            action, objects = self.undo_stack.pop()
            if action == 'create':
                for obj in objects:
                    self.canvas.delete(obj)
            self.drawn_objects = [obj for obj in self.drawn_objects if obj not in objects]

    def insert_image(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
            if file_path:
                image = Image.open(file_path)
                image.thumbnail((100, 100))  # Resize image to fit canvas
                photo = ImageTk.PhotoImage(image)
                obj = self.canvas.create_image(10, 10, anchor=tk.NW, image=photo, tags="draggable")
                self.drawn_objects.append(obj)
                self.undo_stack.append(('create', [obj]))
                if len(self.undo_stack) > 20:
                    self.undo_stack.pop(0)
                self.redo_stack.clear()
                self.root.image = photo  # Keep a reference to the image to prevent garbage collection

        except Exception as e:
            print("An error occurred while inserting the image:", str(e))

    def switch_to_brush(self):
        self.mode = "draw"
        self.brush_color = "black"

    def set_mode(self, mode):
        self.mode = mode
        if mode == "erase":
            self.brush_color = "white"
        elif mode == "draw":
            self.brush_color = "black"

    def select_item(self, event):
        self.selected_item = self.canvas.find_closest(event.x, event.y)
        self.drag_data["item"] = self.selected_item
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def drag_item(self, event):
        if self.selected_item:
            delta_x = event.x - self.drag_data["x"]
            delta_y = event.y - self.drag_data["y"]
            self.canvas.move(self.selected_item, delta_x, delta_y)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def release_item(self, event):
        self.selected_item = None
        self.drag_data["item"] = None
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0


def main():
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()