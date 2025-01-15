from query_data import query_rag
import threading
import customtkinter as ctk
from langchain_community.llms.ollama import Ollama
from PIL import Image
import pywinstyles


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


WIDTH = 800
HEIGHT = 600

DOCBOT_NAME = "MDN DocBot"
DOCBOT_MODEL = "smollm2:1.7b"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.model = Ollama(model=DOCBOT_MODEL)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.title(f"~ {DOCBOT_NAME} ~")
        self.resizable(False, False)
        self.applyBackground()
        self.applyOutput()
        self.applyInput()
        self.output.insert(
            ctk.END, f"\n{DOCBOT_NAME}:\nAsk me about HTML/CSS/JS/HTTP or the WEB-API!\n")

    def applyInput(self):
        self.input = ctk.CTkEntry(
            master=self, placeholder_text="question", width=WIDTH*0.5, )
        self.input.pack(pady=10, padx=10)
        pywinstyles.set_opacity(self.input, value=0.7, color="#000001")
        ctk.CTkButton(master=self, text="Send",
                      command=self.button_function).pack(pady=10, padx=10)

        self.bind('<Return>', self.button_function)

    def applyOutput(self):
        copy_button = ctk.CTkButton(
            master=self, text="Copy to clipboard", command=self.copy_to_clipboard)
        copy_button.pack(pady=10)
        self.output = ctk.CTkTextbox(
            master=self, width=WIDTH*0.65, height=HEIGHT*0.65)
        self.output.pack(padx=50)
        self.output.bind("<Key>", lambda e: "break")
        pywinstyles.set_opacity(self.output, value=0.7, color="#000001")

    def copy_to_clipboard(self):
        text = self.output.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def applyBackground(self):
        label = ctk.CTkLabel(self, text="", image=ctk.CTkImage(light_image=Image.open("./bg.webp"),
                                                               size=(WIDTH, HEIGHT)))
        label.place(x=0, y=0, relwidth=1, relheight=1)

    def button_function(self, event=None):
        self.output.insert(ctk.END, "\nUser:\n")
        inputQuery = self.input.get()
        self.input.delete(0, len(self.input.get()))
        self.output.insert(ctk.END, f"{inputQuery}\n")
        threading.Thread(target=self.query_model, args=(inputQuery,)).start()

    def query_model(self, inputQuery):
        (answer_stream, sources) = query_rag(self.model, inputQuery)
        threading.Thread(target=self.render_stream, args=(
            answer_stream, sources)).start()

    def render_stream(self, answer_stream, sources):
        self.output.insert(ctk.END, f"\n{DOCBOT_NAME}:\n")
        for chunk in answer_stream:
            self.output.insert(ctk.END, chunk)
        self.output.insert(ctk.END, "\n\n Sources:")
        for source in sources:
            self.output.insert(ctk.END, "\n"+source)
        self.output.insert(ctk.END, "\n\n")


app = App()
app.mainloop()
