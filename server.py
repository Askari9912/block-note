import json
import sqlite3
import asyncio
import tornado.web

db = sqlite3.connect("notes.db")
db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, titre TEXT, contenu TEXT)")
db.commit()


class AccueilHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"message": "Serveur bloc-note OK", "routes": ["/notes", "/notes/<id>"]})


class NotesHandler(tornado.web.RequestHandler):
    def get(self):
        rows = db.execute("SELECT id, titre, contenu FROM notes").fetchall()
        self.write({"notes": [{"id": r[0], "titre": r[1], "contenu": r[2]} for r in rows]})

    def post(self):
        try:
            data = json.loads(self.request.body)
            titre = data.get("titre", "")
            contenu = data.get("contenu", "")
        except json.JSONDecodeError:
            self.set_status(400)
            return self.write({"erreur": "JSON invalide"})
        cur = db.execute("INSERT INTO notes (titre, contenu) VALUES (?, ?)", (titre, contenu))
        db.commit()
        self.write({"id": cur.lastrowid})


class NoteHandler(tornado.web.RequestHandler):
    def put(self, note_id):
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.set_status(400)
            return self.write({"erreur": "JSON invalide"})
        db.execute(
            "UPDATE notes SET titre=?, contenu=? WHERE id=?",
            (data.get("titre", ""), data.get("contenu", ""), int(note_id)),
        )
        db.commit()
        self.write({"ok": True})

    def delete(self, note_id):
        db.execute("DELETE FROM notes WHERE id=?", (int(note_id),))
        db.commit()
        self.write({"ok": True})


app = tornado.web.Application([
    (r"/", AccueilHandler),
    (r"/notes", NotesHandler),
    (r"/notes/(\d+)", NoteHandler),
])


async def main():
    app.listen(8888)
    print("Serveur sur http://localhost:8888  (Ctrl+C pour arrêter)")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
        db.close()

