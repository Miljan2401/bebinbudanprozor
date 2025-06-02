import streamlit as st
from datetime import datetime, timedelta
from twilio.rest import Client

# Twilio podešavanja (unesi svoje podatke ovde)
ACCOUNT_SID = "ACd807f2bde8af5db99312ffc4bae1551c"
AUTH_TOKEN = "41acd9fbdc365814a0a8b84d52cd2083"
FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+381642538013"

st.set_page_config(page_title="Bebin San WhatsApp", layout="centered")
st.title("🍼 Praćenje bebinih budnih prozora sa WhatsApp obaveštenjem")

# Opcije za budni prozor po uzrastu
uzrast_opcije = {
    "0–3 meseca (45 min)": 45,
    "4–6 meseci (90 min)": 90,
    "6–9 meseci (120 min)": 120,
    "9–12 meseci (150 min)": 150,
    "12+ meseci (180 min)": 180
}

uzrast = st.selectbox("Uzrast bebe:", list(uzrast_opcije.keys()))
budno_minuta = uzrast_opcije[uzrast]

# Lista vremena buđenja
if "buđenja" not in st.session_state:
    st.session_state.buđenja = []

novo_budjenje = st.time_input("Unesi vreme kada se beba probudila:", key="budjenje_input")
if st.button("Dodaj vreme buđenja"):
    danas = datetime.now().date()
    vreme_obj = datetime.combine(danas, novo_budjenje)
    st.session_state.buđenja.append(vreme_obj)
    st.success(f"Vreme buđenja dodato: {vreme_obj.strftime('%H:%M')}")

# Prikaz svih unosa
if st.session_state.buđenja:
    st.subheader("🕓 Zabeležena buđenja:")
    for i, b in enumerate(st.session_state.buđenja):
        st.write(f"{i+1}. {b.strftime('%H:%M')}")

    poslednje = st.session_state.buđenja[-1]
    sledece_spavanje = poslednje + timedelta(minutes=budno_minuta)
    poruka = f"📣 Sledeće spavanje bi trebalo da bude oko {sledece_spavanje.strftime('%H:%M')}"

    st.info(poruka)

    if st.button("📲 Pošalji poruku na WhatsApp"):
        try:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            client.messages.create(
                from_=FROM_WHATSAPP,
                to=TO_WHATSAPP,
                body=f"Beba se probudila u {poslednje.strftime('%H:%M')}. {poruka}"
            )
            st.success("Poruka poslata na WhatsApp! ✅")
        except Exception as e:
            st.error(f"Greška pri slanju poruke: {e}")
else:
    st.info("Dodaj prvo vreme buđenja da bi se izračunalo sledeće spavanje.")
