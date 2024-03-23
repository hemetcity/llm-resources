import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
from openai import OpenAI

# Initialize main window
root = tk.Tk()
root.title("BELTO AI")
root.geometry("800x600")

# Styling variables and setup
bg_color = "#2C3E50"
button_color = "#ABB2B9"
text_color = "#FFFFFF"

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Helvetica", 10), padding=5, background=button_color)
style.configure("TFrame", background=bg_color)
style.configure("TLabel", font=("Helvetica", 12), background=bg_color, foreground=text_color)

# Initialize OpenAI client
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

history = [
    {"role": "system",
     "content": 'You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful.'},
    {"role": "system", "content": "You are an Environmental Social Governance (ESG) Consultant"},
    {"role": "system", "content": "Give a detailed analysis and insight on how a company is performing in ESG"},
    {"role": "system", "content": "You always consider the Environmental implications of business scenarios"},
]


def get_chatbot_response(user_input, callback):
    history.append({"role": "user", "content": user_input})

    completion = client.chat.completions.create(
        model="huggingfaceh4_zephyr-7b-beta",
        messages=history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}

    for chunk in completion:
        if chunk.choices[0].delta.content:
            new_message["content"] += chunk.choices[0].delta.content

    history.append(new_message)
    root.after(0, callback, new_message["content"])


def send_message():
    user_input = user_text.get("1.0", tk.END).strip()
    if user_input:
        content_text.insert(tk.END, f"USER: {user_input}\n\n")
        content_text.insert(tk.END, "Assistant is typing...\n")
        user_text.delete("1.0", tk.END)

        # Run the API call in a separate thread to avoid blocking the UI
        thread = threading.Thread(target=get_chatbot_response, args=(user_input, update_chatbot_response))
        thread.start()


def update_chatbot_response(response):
    # Remove the loading message
    content_text.delete("end-2l", "end-1l")
    content_text.insert(tk.END, f"ASSISTANT: {response}\n\n")


# Define the attach_file function here
def attach_file():
    global attached_file_path
    attached_file_path = filedialog.askopenfilename()
    update_attachment_alert()

def remove_attachment():
    global attached_file_path
    attached_file_path = None
    update_attachment_alert()

def update_attachment_alert():
    # Update the attachment alert logic here
    if attached_file_path:
        # Show some indication that a file is attached
        print("File attached:", attached_file_path)  # Example action, replace with actual UI update
    else:
        # Hide or clear the file attached indication
        print("No file attached")  # Example action, replace with actual UI update


# Global variable to hold the path of the attached file
attached_file_path = None

# UI Layout
header_frame = ttk.Frame(root, height=50, style="TFrame")
header_frame.pack(side="top", fill="x")
ttk.Label(header_frame, text="How can I help you today?", style="TLabel").pack(side="left", padx=10)

content_text = tk.Text(root, wrap='word', bg="#333333", fg=text_color, insertbackground=text_color)
content_text.pack(expand=True, fill="both", padx=10, pady=10)

button_frame = ttk.Frame(root, style="TFrame")
button_frame.pack(side="top", fill="x", padx=10)
ttk.Button(button_frame, text="Database", style="TButton").grid(row=0, column=0, padx=5, sticky="ew")
ttk.Button(button_frame, text="CRM", style="TButton").grid(row=0, column=1, padx=5, sticky="ew")
ttk.Button(button_frame, text="Editor", style="TButton").grid(row=0, column=2, padx=5, sticky="ew")
ttk.Button(button_frame, text="Attach", style="TButton", command=attach_file).grid(row=0, column=3, padx=5, sticky="ew")
attachment_alert = ttk.Label(button_frame, text="", style="TLabel")
attachment_alert.grid(row=0, column=4, padx=(0, 5), sticky="ew")
ttk.Button(button_frame, text="Send", style="TButton", command=send_message).grid(row=0, column=5, padx=5, sticky="ew")

text_frame = ttk.Frame(root, style="TFrame")
text_frame.pack(side="bottom", fill="x", padx=10)
user_text = tk.Text(text_frame, height=3, bg="#555555", fg=text_color)
user_text.pack(side="left", fill="x", expand=True)
ttk.Scrollbar(text_frame, orient='vertical', command=user_text.yview).pack(side="right", fill='y')
user_text['yscrollcommand'] = lambda *args: args

root.mainloop()
