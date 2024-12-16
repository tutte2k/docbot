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


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.model = Ollama(model="mistral")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.title("~ MDN DocBot ~")
        self.resizable(False, False)
        self.applyBackground()
        self.applyOutput()
        self.applyInput()
        self.output.insert(
            ctk.END, "MDN DocBot:\n Ask me about HTML/CSS/JS/HTTP or the Web Api")

    def applyInput(self):
        self.input = ctk.CTkEntry(
            master=self, placeholder_text="question", width=WIDTH*0.5, )
        self.input.pack(pady=10, padx=10)
        pywinstyles.set_opacity(self.input, value=0.7, color="#000001")
        ctk.CTkButton(master=self, text="Send",
                      command=self.button_function).pack(pady=10, padx=10)

        self.bind('<Return>', self.button_function)

    def applyOutput(self):
        self.output = ctk.CTkTextbox(
            master=self, width=WIDTH*0.65, height=HEIGHT*0.65)
        self.output.pack(pady=50, padx=50)
        self.output.bind("<Key>", lambda e: "break")
        pywinstyles.set_opacity(self.output, value=0.7, color="#000001")

    def applyBackground(self):
        label = ctk.CTkLabel(self, text="", image=ctk.CTkImage(light_image=Image.open("./bg.webp"),
                                                               size=(WIDTH, HEIGHT)))
        label.place(x=0, y=0, relwidth=1, relheight=1)

    def button_function(self, event=None):
        self.output.insert(ctk.END, "User:\n")
        inputQuery = self.input.get()
        self.input.delete(0, len(self.input.get()))
        self.output.insert(ctk.END, f"{inputQuery}\n")
        threading.Thread(target=self.query_model, args=(inputQuery,)).start()

    def query_model(self, inputQuery):
        (answer_stream, sources) = query_rag(self.model, inputQuery)
        threading.Thread(target=self.render_stream, args=(
            answer_stream, sources)).start()

    def render_stream(self, answer_stream, sources):
        self.output.insert(ctk.END, "\nVall-E:\n")
        for chunk in answer_stream:
            self.output.insert(ctk.END, chunk)
        self.output.insert(ctk.END, "\n\n Sources:")
        for source in sources:
            self.output.insert(ctk.END, "\n"+source)
        self.output.insert(ctk.END, "\n\n")


app = App()
app.mainloop()
