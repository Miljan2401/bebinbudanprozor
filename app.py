import streamlit as st
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="Bebini budni prozori", layout="centered")

st.title("🍼 Praćenje bebinih budnih prozora")

# Inputi
uzrast_opcije = {
    "0–3 meseca (45 min)": 45,
    "4–6 meseci (90 min)": 90,
    "6–9 meseci (120 min)": 120,
    "9–12 meseci (150 min)": 150,
    "12+ meseci (180 min)": 180
}

uzrast = st.selectbox("Uzrast bebe:", list(uzrast_opcije.keys()))
vreme_budjenja = st.time_input("Vreme buđenja:")
email = st.text_input("Tvoj email za podsetnik:")

if st.button("Izračunaj i pošalji podsetnik"):
    if not email:
        st.error("Unesi validan email.")
    else:
        # Izračunavanje sledećeg spavanja
        minutes_awake = uzrast_opcije[uzrast]
        danas = datetime.now().date()
        buđenje = datetime.combine(danas, vreme_budjenja)
        spavanje = buđenje + timedelta(minutes=minutes_awake)

        poruka = f"Beba bi trebalo da ide na spavanje oko {spavanje.strftime('%H:%M')}."

        st.success(poruka)

        # Slanje emaila
        try:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_user = "tvoj.email@gmail.com"
            smtp_pass = "tvoja_lozinka_ili_app_lozinka"

            msg = MIMEText(poruka)
            msg['Subject'] = "Podsetnik za bebin san"
            msg['From'] = smtp_user
            msg['To'] = email

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()

            st.info(f"📧 Podsetnik je poslat na {email}")
        except Exception as e:
            st.error(f"Greška pri slanju emaila: {e}")
