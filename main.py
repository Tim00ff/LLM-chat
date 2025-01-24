import FreeSimpleGUI as sg
import ollama

# Set a modern theme
sg.theme("DarkBlue3")

# Custom font and colors
FONT = ("Helvetica", 14)
INPUT_FONT = ("Helvetica", 16)
BUTTON_COLOR = ("#FFFFFF", "#4CAF50")  # White text on green background
EXIT_BUTTON_COLOR = ("#FFFFFF", "#FF5252")  # White text on red background

# Model for Ollama
model = "llama3.1"

# Initialize chat history
chat_history = []
# Function to generate a question based on chat history
def generate_question(chat_history):
    prompt = (
        "Ты играешь в игру 'Угадай фрукт или овощ'. "
        "Ты должен задавать вопросы, чтобы угадать, что загадал пользователь. "
        "На основе предыдущих ответов пользователя придумай следующий вопрос. "
        "Задавая вопросы пользователю, делай вид - что пользователь олицотворяет овощ "
        "Используй казуальную речь, упрощай ее будто для маленьких детей"
        "Используй юморитистические ремарки во время этой игры и добавляй шутки. Приветствуются шутки на тематику зеленого чая, майнкрафта, танцев в фортнайте. "
        "Когда задаешь вопросы - пиши их порядковый номер "
        "Задавай вопросы по одному и дожидайся ответа от пользователя"
        "НЕ ПИШИ БОЛЬШЕ ЧЕМ 1 ВОПРОС ЗА РАЗ И НЕ РАССМАТРИВАЙ ВОЗМОЖНЫЕ СЦЕНАРИИ ОТВЕТА ПОЛЬЗОВАТЕЛЯ ДО ТОГО КАК ОН ОТВЕТИТ"
        "Если номер вопроса есть в истории чата - ты уже его задал. "
        "После того как задашь 10 вопросов попытайся догадаться какой фрукт или овощ твой пользователь "
        "После этого на любой текст от пользователя реагируй ответом '...' "
        "Вот история чата:\n"
        + str(chat_history)
    )
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    return response

# Centered and scalable layout
layout = [
    [sg.Push(), sg.Text("Угадай фрукт или овощ!", font=("Helvetica", 20, "bold"), pad=(10, 20)), sg.Push()],  # Centered title
    [sg.Push(), sg.Input(key='-INPUT-', enable_events=True, font=INPUT_FONT, size=(40, 1), pad=(10, 10)), sg.Push()],  # Centered input
    [sg.Push(), sg.Button('Ответить', button_color=BUTTON_COLOR, font=FONT, size=(10, 1), pad=(10, 10)),
     sg.Button('Выйти', button_color=EXIT_BUTTON_COLOR, font=FONT, size=(10, 1), pad=(10, 10)), sg.Push()],  # Centered buttons
    [sg.Push(), sg.Multiline(size=(60, 20), key='-OUTPUT-', autoscroll=True, font=FONT, background_color="#2E3440", text_color="#FFFFFF", pad=(10, 10), expand_x=True, expand_y=True), sg.Push()],  # Scalable output
]

# Create the window with a title and icon
window = sg.Window(
    "Угадай фрукт или овощ",
    layout,
    finalize=True,
    resizable=True,
    margins=(10, 10),
    icon="icon.ico"  # Optional: Add an icon file
)

# Bind the Enter key to the Input element
window['-INPUT-'].bind("<Return>", "_Enter")

# Start the chat with the first question
window['-OUTPUT-'].print("Бот: Давай сыграем в игру! Загадай фрукт или овощ, а я попробую угадать. Начнем? Ответь 'Да' или 'Нет'.", text_color="#A3BE8C")

# Event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Выйти':
        break

    # Handle Ответить or Enter key
    if event == 'Ответить' or event == '-INPUT-_Enter':
        user_input = values['-INPUT-'].strip()  # Remove trailing newline if any
        if user_input:  # Проверка на пустой ввод
            # Add user input to chat history
            chat_history.append({"role": "user", "content": user_input})
            window['-OUTPUT-'].print(f"Вы: {user_input}", text_color="#88C0D0")

            # Generate a new question based on chat history
            question = generate_question(chat_history)
            chat_history.append({"role": "assistant", "content": question})
            for chunk in question:
                chat_history += chunk['message']['content']
                window['-OUTPUT-'].print(chunk['message']['content'], end='', text_color="#FFFFFF")
                window.refresh()  # Update the GUI in real-time
            window['-OUTPUT-'].print('\n')
            window['-INPUT-'].update('')
window.close()