import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

API = "http://localhost:8888"


class BlocNote(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=10, spacing=10, **kw)
        self.selected_id = None
        self.titre = TextInput(hint_text="Titre", size_hint_y=None, height=40)
        self.contenu = TextInput(hint_text="Écris ta note...")
        boutons = BoxLayout(size_hint_y=None, height=50, spacing=10)
        for txt, fn in [("Nouveau", self.nouveau), ("Enregistrer", self.enregistrer), ("Supprimer", self.supprimer)]:
            boutons.add_widget(Button(text=txt, on_press=fn))
        self.liste = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.liste.bind(minimum_height=self.liste.setter("height"))
        scroll = ScrollView(size_hint_y=0.4)
        scroll.add_widget(self.liste)
        for w in (self.titre, self.contenu, boutons, scroll):
            self.add_widget(w)
        self.charger()

    def charger(self):
        self.liste.clear_widgets()
        try:
            notes = requests.get(f"{API}/notes", timeout=3).json()["notes"]
        except requests.exceptions.RequestException:
            self.liste.add_widget(Button(
                text="Serveur introuvable : lance 'python server.py'",
                size_hint_y=None, height=40))
            return
        for n in notes:
            b = Button(text=n["titre"] or "(sans titre)", size_hint_y=None, height=40)
            b.bind(on_press=lambda _, n=n: self.ouvrir(n))
            self.liste.add_widget(b)

    def ouvrir(self, n):
        self.selected_id = n["id"]
        self.titre.text = n["titre"]
        self.contenu.text = n["contenu"]

    def nouveau(self, *_):
        self.selected_id = None
        self.titre.text = ""
        self.contenu.text = ""

    def enregistrer(self, *_):
        data = {"titre": self.titre.text, "contenu": self.contenu.text}
        try:
            if self.selected_id:
                requests.put(f"{API}/notes/{self.selected_id}", json=data, timeout=3)
            else:
                requests.post(f"{API}/notes", json=data, timeout=3)
        except requests.exceptions.RequestException:
            pass
        self.charger()

    def supprimer(self, *_):
        if self.selected_id:
            try:
                requests.delete(f"{API}/notes/{self.selected_id}", timeout=3)
            except requests.exceptions.RequestException:
                pass
            self.nouveau()
            self.charger()


class BlocNoteApp(App):
    def build(self):
        return BlocNote()


if __name__ == "__main__":
    BlocNoteApp().run()

