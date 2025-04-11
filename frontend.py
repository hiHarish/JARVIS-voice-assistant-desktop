import tkinter as tk
from tkinter import scrolledtext

def dummy_response(user_input):
    # Temporary dummy response until backend is integrated
    return f"Received command: {user_input}"

def send_command():
    user_input = entry.get()
    if user_input.strip() == "":
        return

    chat_box.config(state=tk.NORMAL)  # Enable editing
    chat_box.insert(tk.END, f"You: {user_input}\n")

    response = dummy_response(user_input)
    chat_box.insert(tk.END, f"Jarvis: {response}\n\n")
    chat_box.config(state=tk.DISABLED)  # Lock again
    chat_box.see(tk.END)  # Scroll to bottom
    entry.delete(0, tk.END)

# Main window
root = tk.Tk()
root.title("Jarvis Desktop Assistant")
root.geometry("600x400")
root.resizable(False, False)

# Chat display area
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12))
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_box.config(state=tk.DISABLED)  # Start as read-only

# Input field
entry = tk.Entry(root, font=("Arial", 14))
entry.pack(padx=10, pady=5, fill=tk.X)
entry.bind("<Return>", lambda event: send_command())

# Send button
send_btn = tk.Button(root, text="Send", font=("Arial", 12), command=send_command)
send_btn.pack(pady=5)

root.mainloop()
