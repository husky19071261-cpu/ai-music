import sys
sys.stdout.reconfigure(encoding='utf-8')
import tkinter as tk
import subprocess
import threading

def run_generator():
    status_label.config(text="Generating...")
    
    def task():
        try:
            result = subprocess.run(
                ["python", "main.py"],
                capture_output=True,
                text=True
            )
            output = result.stdout + result.stderr
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, output)
            status_label.config(text="Done")
        except Exception as e:
            status_label.config(text="Error")
            output_text.insert(tk.END, str(e))

    threading.Thread(target=task).start()

# GUI setup
root = tk.Tk()
root.title("AI Music Generator")
root.geometry("500x400")

title = tk.Label(root, text="AI Music Generator", font=("Arial", 16))
title.pack(pady=10)

generate_button = tk.Button(root, text="Generate Music", command=run_generator)
generate_button.pack(pady=10)

status_label = tk.Label(root, text="Idle")
status_label.pack(pady=5)

output_text = tk.Text(root, height=10)
output_text.pack(pady=10, fill="both", expand=True)

root.mainloop()
