import tkinter as tk
from tkinter import font, scrolledtext, ttk
import sys


class FontViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Font Viewer - 'improv show'")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable text widget
        self.text_widget = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.NONE,
            width=100,
            height=40,
            font=("Courier", 10)
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Get all available fonts
        self.available_fonts = sorted(font.families())
        
        # Display fonts
        self.display_fonts()
        
    def display_fonts(self):
        """Display 'improv show' in each available font"""
        self.text_widget.delete(1.0, tk.END)
        
        # Add header
        header = f"Font Viewer - Displaying 'improv show' in {len(self.available_fonts)} fonts\n"
        header += "=" * 80 + "\n\n"
        self.text_widget.insert(tk.END, header)
        
        # Counter for successful font displays
        successful_fonts = 0
        
        for font_name in self.available_fonts:
            try:
                # Create a tag for this font
                tag_name = f"font_{successful_fonts}"
                
                # Configure the tag with the font
                self.text_widget.tag_configure(
                    tag_name,
                    font=(font_name, 14, "normal")
                )
                
                # Insert the text with font name and sample
                text_line = f"{font_name:<40} -> improv show\n"
                
                # Insert font name in regular font
                self.text_widget.insert(tk.END, f"{font_name:<40} -> ")
                
                # Insert "improv show" in the actual font
                start_pos = self.text_widget.index(tk.INSERT)
                self.text_widget.insert(tk.END, "improv show\n")
                end_pos = self.text_widget.index(tk.INSERT)
                
                # Apply the font tag to just the "improv show" part
                self.text_widget.tag_add(tag_name, f"{start_pos} -11c", f"{start_pos} lineend")
                
                successful_fonts += 1
                
            except tk.TclError as e:
                # If font fails to load, show error
                error_text = f"{font_name:<40} -> [Font Error: {str(e)}]\n"
                self.text_widget.insert(tk.END, error_text)
        
        # Add footer
        footer = f"\n" + "=" * 80 + "\n"
        footer += f"Total fonts found: {len(self.available_fonts)}\n"
        footer += f"Successfully displayed: {successful_fonts}\n"
        self.text_widget.insert(tk.END, footer)
        
        # Scroll to top
        self.text_widget.see(1.0)
    
    def run(self):
        """Start the font viewer application"""
        self.root.mainloop()


class FontViewerLarge:
    """Alternative font viewer with larger text display"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Large Font Viewer - 'improv show'")
        self.root.geometry("1000x700")
        
        # Get all available fonts
        self.available_fonts = sorted(font.families())
        self.current_font_index = 0
        
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Font info label
        self.info_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 12),
            wraplength=900
        )
        self.info_label.pack(pady=(0, 10))
        
        # Main display label for the font sample
        self.display_label = tk.Label(
            main_frame,
            text="improv show",
            font=("Arial", 24),
            bg="white",
            relief="sunken",
            bd=2,
            height=3
        )
        self.display_label.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Navigation frame
        nav_frame = tk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        # Navigation buttons
        self.prev_button = tk.Button(
            nav_frame,
            text="← Previous Font",
            command=self.previous_font,
            font=("Arial", 12)
        )
        self.prev_button.pack(side=tk.LEFT)
        
        self.next_button = tk.Button(
            nav_frame,
            text="Next Font →",
            command=self.next_font,
            font=("Arial", 12)
        )
        self.next_button.pack(side=tk.RIGHT)
        
        # Font selection frame
        select_frame = tk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(select_frame, text="Jump to font:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.font_var = tk.StringVar()
        self.font_combobox = tk.ttk.Combobox(
            select_frame,
            textvariable=self.font_var,
            values=self.available_fonts,
            state="readonly",
            width=30
        )
        self.font_combobox.pack(side=tk.LEFT, padx=(5, 0))
        self.font_combobox.bind("<<ComboboxSelected>>", self.on_font_selected)
        
        # Initialize display
        self.update_display()
    
    def update_display(self):
        """Update the display with current font"""
        if not self.available_fonts:
            return
            
        current_font = self.available_fonts[self.current_font_index]
        
        try:
            # Update the main display
            self.display_label.config(font=(current_font, 32, "normal"))
            
            # Update info
            info_text = f"Font {self.current_font_index + 1} of {len(self.available_fonts)}: {current_font}"
            self.info_label.config(text=info_text)
            
            # Update combobox
            self.font_var.set(current_font)
            
            # Update button states
            self.prev_button.config(state=tk.NORMAL if self.current_font_index > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.current_font_index < len(self.available_fonts) - 1 else tk.DISABLED)
            
        except tk.TclError as e:
            # If font fails, show error and skip to next
            self.display_label.config(font=("Arial", 20), text=f"Font Error: {current_font}")
            self.info_label.config(text=f"Error loading font: {current_font} - {str(e)}")
    
    def next_font(self):
        """Go to next font"""
        if self.current_font_index < len(self.available_fonts) - 1:
            self.current_font_index += 1
            self.update_display()
    
    def previous_font(self):
        """Go to previous font"""
        if self.current_font_index > 0:
            self.current_font_index -= 1
            self.update_display()
    
    def on_font_selected(self, event=None):
        """Handle font selection from combobox"""
        selected_font = self.font_var.get()
        if selected_font in self.available_fonts:
            self.current_font_index = self.available_fonts.index(selected_font)
            self.update_display()
    
    def run(self):
        """Start the large font viewer application"""
        self.root.mainloop()


def main():
    """Main function to run the font viewer"""
    print("Font Viewer Options:")
    print("1. List view (all fonts in scrollable list)")
    print("2. Large view (one font at a time, larger display)")
    
    choice = input("Enter choice (1 or 2), or press Enter for large view: ").strip()
    
    if choice == "1":
        print("Starting List Font Viewer...")
        app = FontViewer()
    else:
        print("Starting Large Font Viewer...")
        app = FontViewerLarge()
    
    app.run()


if __name__ == "__main__":
    main()
