import requests, streamlit as st

API = "http://localhost:8888"
st.title("📒 Tableau de bord des notes")

notes = requests.get(f"{API}/notes").json()["notes"]
st.metric("Nombre de notes", len(notes))

with st.form("ajout"):
    t = st.text_input("Titre")
    c = st.text_area("Contenu")
    if st.form_submit_button("Ajouter"):
        requests.post(f"{API}/notes", json={"titre": t, "contenu": c})
        st.rerun()

for n in notes:
    with st.expander(n["titre"]):
        st.write(n["contenu"])
        if st.button("Supprimer", key=n["id"]):
            requests.delete(f"{API}/notes/{n['id']}")
            st.rerun()
