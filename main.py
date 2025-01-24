import FreeSimpleGUI as sg
import ollama

# Set a modern theme
sg.theme("DarkBlue3")

# Custom font and colors
FONT = ("Helvetica", 14)
INPUT_FONT = ("Helvetica", 16)
BUTTON_COLOR = ("#FFFFFF", "#4CAF50")  # White text on green background
EXIT_BUTTON_COLOR = ("#FFFFFF", "#FF5252")  # White text on red background
FILE_BUTTON_COLOR = ("#FFFFFF", "#2196F3")  # White text on blue background

# Model for Ollama
model = "deepseek-coder-v2"

# Initialize chat history
chat_history = []

def chat_with_ollama(messages):
    response = ollama.chat(
        model=model,
        messages=messages,
        stream=True
    )
    return response

# Centered and scalable layout
layout = [
    [sg.Push(), sg.Text("Chat with AI", font=("Helvetica", 20, "bold"), pad=(10, 20)), sg.Push()],  # Centered title
    [sg.Push(), sg.Input(key='-INPUT-', enable_events=True, font=INPUT_FONT, size=(40, 1), pad=(10, 10)), sg.Push()],  # Centered input
    [sg.Push(), sg.Button('Send', button_color=BUTTON_COLOR, font=FONT, size=(10, 1), pad=(10, 10)),
     sg.Button('Exit', button_color=EXIT_BUTTON_COLOR, font=FONT, size=(10, 1), pad=(10, 10)), sg.Push()],  # Centered buttons
    [sg.Push(), sg.Multiline(size=(60, 20), key='-OUTPUT-', autoscroll=True, font=FONT, background_color="#2E3440", text_color="#FFFFFF", pad=(10, 10), expand_x=True, expand_y=True), sg.Push()],  # Scalable output
    [sg.Push(), sg.Button('Save Chat', button_color=FILE_BUTTON_COLOR, font=FONT, size=(10, 1), pad=(10, 10)),
     sg.Button('Load Chat', button_color=FILE_BUTTON_COLOR, font=FONT, size=(10, 1), pad=(10, 10)), sg.Push()]  # File I/O buttons
]

# Create the window with a title and icon
window = sg.Window(
    "AI Chat",
    layout,
    finalize=True,
    resizable=True,
    margins=(10, 10),
    icon="icon.ico"  # Optional: Add an icon file
)

# Bind the Enter key to the Input element
window['-INPUT-'].bind("<Return>", "_Enter")

# Event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    # Handle Send or Enter key
    if event == 'Send' or event == '-INPUT-_Enter':
        user_input = values['-INPUT-'].strip()  # Remove trailing newline if any
        if user_input:  # Проверка на пустой ввод
            # Add user input to chat history
            chat_history.append({"role": "user", "content": user_input})
            window['-OUTPUT-'].print(f"User: {user_input}", text_color="#88C0D0")

            # Get AI response with full chat history as context
            stream = chat_with_ollama(chat_history)
            window['-OUTPUT-'].print(f"Assistant:", text_color="#FFFFFF", end="")
            ai_response = ""
            for chunk in stream:
                ai_response += chunk['message']['content']
                window['-OUTPUT-'].print(chunk['message']['content'], end='', text_color="#FFFFFF")
                window.refresh()  # Update the GUI in real-time

            # Add AI response to chat history
            chat_history.append({"role": "assistant", "content": ai_response})
            window['-OUTPUT-'].print("\n")  # New line after response
            window['-INPUT-'].update('')  # Очистка поля ввода

    # Handle Save Chat button
    if event == 'Save Chat':
        save_path = sg.popup_get_file("Save Chat History", save_as=True, default_extension=".txt", file_types=(("Text Files", "*.txt"),))
        if save_path:
            # Convert chat history to text format
            chat_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
            with open(save_path, "w", encoding="utf-8") as file:
                file.write(chat_text)
            sg.popup("Chat History Saved!", f"Saved to: {save_path}")

    # Handle Load Chat button
    if event == 'Load Chat':
        load_path = sg.popup_get_file("Load Chat History", file_types=(("Text Files", "*.txt"),))
        if load_path:
            with open(load_path, "r", encoding="utf-8") as file:
                loaded_history = file.read().splitlines()
                # Convert loaded text back to chat history format
                chat_history = []
                for line in loaded_history:
                    if line.startswith("User:"):
                        chat_history.append({"role": "user", "content": line[len("User: "):]})
                    elif line.startswith("Assistant:"):
                        chat_history.append({"role": "assistant", "content": line[len("Assistant: "):]})
                # Display loaded history with newline
                window['-OUTPUT-'].update("\n".join(loaded_history) + "\n")
            sg.popup("Chat History Loaded!", f"Loaded from: {load_path}")

window.close()