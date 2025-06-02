import streamlit as st
from datetime import datetime, timedelta
from threading import Timer
from twilio.rest import Client

# Twilio podaci
ACCOUNT_SID = "ACd807f2bde8af5db99312ffc4bae1551c"
AUTH_TOKEN = "41acd9fbdc365814a0a8b84d52cd2083"
FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+381642538013"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

st.title("🍼 Bebin san sa automatskim WhatsApp podsetnikom")

# Padajući meni za uzrast bebe
uzrast_opcije = {
    "0–3 meseca (45 min)": 45,
    "4–6 meseci (90 min)": 90,
    "6–9 meseci (120 min)": 120,
    "9–12 meseci (150 min)": 150,
    "12+ meseci (180 min)": 180
}

uzrast = st.selectbox("Izaberi uzrast bebe:", list(uzrast_opcije.keys()))
budno_minuta = uzrast_opcije[uzrast]

if "buđenja" not in st.session_state:
    st.session_state.buđenja = []

def send_whatsapp_notification(budjenje_vreme, spavanje_vreme):
    poruka = (
        f"Beba se probudila u {budjenje_vreme.strftime('%H:%M')}. "
        f"Sledeće spavanje je oko {spavanje_vreme.strftime('%H:%M')} (podsetnik 10 minuta ranije)."
    )
    try:
        client.messages.create(
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP,
            body=poruka
        )
        st.success("Automatski podsetnik poslat na WhatsApp!")
    except Exception as e:
        st.error(f"Greška pri slanju poruke: {e}")

def schedule_notification(budjenje_vreme, budno_minuta):
    spavanje_vreme = budjenje_vreme + timedelta(minutes=budno_minuta)
    podsetnik_vreme = spavanje_vreme - timedelta(minutes=10)
    sada = datetime.now()

    vreme_do_podsetnika = (podsetnik_vreme - sada).total_seconds()

    if vreme_do_podsetnika <= 0:
        st.warning("Već je prošlo vreme za podsetnik ili je beba predugo budna.")
        return

    t = Timer(vreme_do_podsetnika, send_whatsapp_notification, args=(budjenje_vreme, spavanje_vreme))
    t.start()
    st.info(f"Podsetnik će biti poslat u {podsetnik_vreme.strftime('%H:%M')} (za {int(vreme_do_podsetnika)} sekundi).")

# Novi deo: padajući meni za sat i minut
sat = st.selectbox("Izaberi sat (1-24):", list(range(1, 25)))
minut = st.selectbox("Izaberi minut (1-60):", list(range(1, 61)))

if st.button("Dodaj buđenje i zakaži podsetnik"):
    danas = datetime.now().date()
    vreme_obj = datetime.combine(danas, datetime.min.time()).replace(hour=sat, minute=minut)
    st.session_state.buđenja.append(vreme_obj)
    st.success(f"Dodato vreme buđenja: {vreme_obj.strftime('%H:%M')}")
    schedule_notification(vreme_obj, budno_minuta)

if st.session_state.buđenja:
    st.subheader("Zabeležena buđenja:")
    for i, b in enumerate(st.session_state.buđenja):
        st.write(f"{i+1}. {b.strftime('%H:%M')}")
