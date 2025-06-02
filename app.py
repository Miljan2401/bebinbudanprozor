import streamlit as st
from datetime import datetime, timedelta
from threading import Timer
from twilio.rest import Client

# Twilio konfiguracija
ACCOUNT_SID = "tvoj_sid"
AUTH_TOKEN = "tvoj_auth_token"
FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+381642538013"
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Uzrast i budni prozori (u minutima)
uzrast_podaci = {
    "0–3 meseca": 45,
    "4–6 meseci": 90,
    "6–9 meseci": 120,
    "9–12 meseci": 150,
    "12+ meseci": 180
}

st.title("Bebin budni prozor i obaveštenje za spavanje")

uzrast = st.selectbox("Izaberi uzrast bebe:", list(uzrast_podaci.keys()))
budni_prozor = uzrast_podaci[uzrast]

# Unos kada se beba probudila (sat i minut)
col1, col2 = st.columns(2)
with col1:
    sat = st.number_input("Sat (0-23)", min_value=0, max_value=23, value=datetime.now().hour)
with col2:
    minut = st.number_input("Minut (0-59)", min_value=0, max_value=59, value=datetime.now().minute)

# Unos trajanja poslednjeg sna (u minutima)
poslednji_san = st.number_input("Koliko je trajao poslednji san (minuta)?", min_value=10, max_value=300, value=60)

if st.button("Izračunaj i zakaži obaveštenje"):

    # Vreme kada se beba probudila
    danas = datetime.now().date()
    vreme_budjenja = datetime.combine(danas, datetime.min.time()).replace(hour=sat, minute=minut)
    sada = datetime.now()

    if vreme_budjenja < sada:
        vreme_budjenja += timedelta(days=1)  # ako je uneto vreme prošlo danas, prebaci na sutra

    # Izračunaj kada bi trebalo da beba ide na spavanje
    # Uzimamo minimalni budni prozor od uzrasta, i prilagođavamo na osnovu trajanja poslednjeg sna
    # Ovde možeš dodati složeniju logiku, ovo je jednostavan primer:
    
    # Na primer, ako je san bio kraći od idealnog, smanjujemo budni prozor za 10 minuta
    korekcija = 0
    if poslednji_san < 45:
        korekcija = -10
    elif poslednji_san > 90:
        korekcija = 10
    
    prilagodjeni_budni_prozor = max(15, budni_prozor + korekcija)

    vreme_za_spavanje = vreme_budjenja + timedelta(minutes=prilagodjeni_budni_prozor)

    # Obaveštenje treba da stigne 10 minuta pre
    vreme_podsetnika = vreme_za_spavanje - timedelta(minutes=10)

    vreme_do_podsetnika = (vreme_podsetnika - sada).total_seconds()

    if vreme_do_podsetnika <= 0:
        st.warning("Već je prošlo vreme za podsetnik ili je beba predugo budna.")
    else:
        def send_whatsapp():
            poruka = (f"Beba se probudila u {vreme_budjenja.strftime('%H:%M')}.\n"
                      f"Preporučeno vreme za spavanje je oko {vreme_za_spavanje.strftime('%H:%M')}.\n"
                      f"Podsetnik stiže 10 minuta ranije.")
            try:
                client.messages.create(from_=FROM_WHATSAPP, to=TO_WHATSAPP, body=poruka)
                st.success("Automatski WhatsApp podsetnik poslat!")
            except Exception as e:
                st.error(f"Greška pri slanju poruke: {e}")

        t = Timer(vreme_do_podsetnika, send_whatsapp)
        t.start()

        st.info(f"Podsetnik će biti poslat u {vreme_podsetnika.strftime('%H:%M')} (za {int(vreme_do_podsetnika)} sekundi).")
