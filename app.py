import streamlit as st
from datetime import datetime, timedelta
from threading import Timer
from twilio.rest import Client

# Twilio konfiguracija - popuni sa svojim podacima
ACCOUNT_SID = "tvoj_sid"
AUTH_TOKEN = "tvoj_auth_token"
FROM_WHATSAPP = "whatsapp:+14155238886"  # Twilio sandbox broj
TO_WHATSAPP = "whatsapp:+381642538013"  # Tvoj broj sa +381 prefiksom

client = Client(ACCOUNT_SID, AUTH_TOKEN)

st.title("Praćenje budnih prozora bebe sa automatskim WhatsApp podsetnikom")

# Definisani intervali maksimalne budnosti po uzrastu (u minutima)
budni_prozori = {
    "0-4 nedelje": (45, 60),
    "4-12 nedelja": (60, 90),
    "3-4 meseca": (75, 120),
    "5-7 meseci": (120, 180),
    "7-10 meseci": (150, 210),
    "11-18 meseci": (180, 240),
    "18+ meseci": (240, 360)
}

uzrast = st.selectbox("Izaberi uzrast bebe:", list(budni_prozori.keys()))

# Unos koliko je beba bila budna od poslednjeg sna (u minutima)
trenutno_budna = st.number_input(
    "Unesi koliko je beba bila budna od poslednjeg sna (u minutima):",
    min_value=0,
    max_value=600,
    value=0,
    step=1
)

if st.button("Izračunaj i zakaži podsetnik"):

    min_budni, max_budni = budni_prozori[uzrast]

    # Računamo preostalo vreme do kraja maksimalnog budnog prozora (max_budni - trenutno_budna)
    preostalo = max_budni - trenutno_budna

    if preostalo <= 0:
        st.error("Beba je verovatno već predugo budna. Vreme za spavanje je odmah!")
    else:
        sada = datetime.now()
        vreme_podsetnika = sada + timedelta(minutes=preostalo - 10)  # 10 min pre kraja budnog prozora
        vreme_do_podsetnika = (vreme_podsetnika - sada).total_seconds()

        if vreme_do_podsetnika <= 0:
            # Ako je ostalo manje od 10 minuta, šaljemo odmah
            vreme_do_podsetnika = 5  # pošalji za 5 sekundi

        def send_whatsapp():
            poruka = (f"Beba je budna već {trenutno_budna} minuta.\n"
                      f"Maksimalni budni prozor za uzrast {uzrast} je do {max_budni} minuta.\n"
                      f"Preporučeno vreme za spavanje je uskoro.\n"
                      f"Podsetnik stiže 10 minuta pre kraja budnog prozora.")
            try:
                client.messages.create(
                    from_=FROM_WHATSAPP,
                    to=TO_WHATSAPP,
                    body=poruka
                )
                st.success("WhatsApp podsetnik je uspešno poslat!")
            except Exception as e:
                st.error(f"Greška pri slanju WhatsApp poruke: {e}")

        t = Timer(vreme_do_podsetnika, send_whatsapp)
        t.start()

        st.info(f"Podsetnik je zakazan za {vreme_podsetnika.strftime('%H:%M:%S')}, "
                f"što je za {int(vreme_do_podsetnika)} sekundi od sada.")
