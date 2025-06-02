import streamlit as st
import json
import os
from datetime import datetime, timedelta
from twilio.rest import Client

# Twilio podešavanja
account_sid = 'ACd807f2bde8af5db99312ffc4bae1551c'
auth_token = '41acd9fbdc365814a0a8b84d52cd2083'
client = Client(account_sid, auth_token)

# Putanja do fajla za čuvanje istorije
DATA_FILE = "bebini_prozori.json"

# Učitavanje istorije iz fajla
def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# Čuvanje istorije u fajl
def save_history(history):
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=2)

# Konvertovanje stringa u datetime
def str_to_dt(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

# Konvertovanje datetime u string
def dt_to_str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Maksimalni budni interval u minutima po uzrastu u nedeljama
def max_budnost_minutes(age_weeks):
    if age_weeks <= 4:
        return 60
    elif age_weeks <= 12:
        return 90
    elif age_weeks <= 16:
        return 120
    elif age_weeks <= 30:
        return 180
    elif age_weeks <= 40:
        return 210
    elif age_weeks <= 78:
        return 240
    else:
        return 360

st.title("Bebin Budni Prozor sa Istorijom i WhatsApp Podsetnikom")

age_weeks = st.number_input("Starost bebe (nedelje):", min_value=0, max_value=104, value=8)
wake_time = st.time_input("Vreme buđenja bebe:", value=datetime.now().time())
sleep_time = st.time_input("Vreme uspavljivanja bebe:", value=(datetime.now() + timedelta(minutes=30)).time())

now = datetime.now()
wake_dt = datetime.combine(now.date(), wake_time)
sleep_dt = datetime.combine(now.date(), sleep_time)
if sleep_dt <= wake_dt:
    sleep_dt += timedelta(days=1)

history = load_history()

# Dugme za dodavanje unosa u istoriju
if st.button("Sačuvaj unos budnog perioda"):
    new_entry = {
        "wake": dt_to_str(wake_dt),
        "sleep": dt_to_str(sleep_dt),
        "age_weeks": age_weeks
    }
    history.append(new_entry)
    save_history(history)
    st.success("Unos sačuvan!")

# Prikaz istorije unosa
if history:
    st.subheader("Istorija unosa budnih perioda:")
    for i, entry in enumerate(history[::-1], 1):
        st.write(f"{i}. Buđenje: {entry['wake']} | Spavanje: {entry['sleep']} | Starost: {entry['age_weeks']} nedelja")

# Računanje ukupne budnosti od poslednjeg unosa
if history:
    last = history[-1]
    last_wake = str_to_dt(last["wake"])
    last_sleep = str_to_dt(last["sleep"])
    last_age = last["age_weeks"]
    max_bud = max_budnost_minutes(last_age)
    elapsed = (datetime.now() - last_wake).total_seconds() / 60  # u minutima

    st.write(f"Poslednji budni prozor počeo je u {last_wake.strftime('%H:%M:%S')}")
    st.write(f"Trenutno beba je budna oko {int(elapsed)} minuta, maksimalno preporučeno: {max_bud} minuta")

    if elapsed >= max_bud:
        st.warning("Beba je premašila maksimalni preporučeni budni period. Preporučuje se uspavljivanje odmah.")
        reminder_time = datetime.now() + timedelta(seconds=10)
    else:
        reminder_time = last_wake + timedelta(minutes=max_bud)
        st.info(f"Podsetnik za uspavljivanje je zakazan za {reminder_time.strftime('%H:%M:%S')}")

    # Dugme za slanje WhatsApp podsetnika
    if st.button("Pošalji WhatsApp podsetnik sada"):
        try:
            msg_body = f"Podsetnik: Bebin maksimalni budni period je {max_bud} minuta. Vreme za uspavljivanje: {reminder_time.strftime('%H:%M')}."
            message = client.messages.create(
                from_='whatsapp:+14155238886',
                body=msg_body,
                to='whatsapp:+381642538013'  # ovde stavi svoj broj
            )
            st.success(f"Poruka poslata! SID: {message.sid}")
        except Exception as e:
            st.error(f"Greška pri slanju poruke: {e}")
else:
    st.info("Nema unosa u istoriji. Sačuvaj prvi budni period.")

