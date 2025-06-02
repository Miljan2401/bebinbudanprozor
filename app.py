import streamlit as st
import datetime
import pandas as pd
import altair as alt
from twilio.rest import Client
import threading
import time
import pytz

# Twilio setup (popuni sa tvojim podacima)
account_sid = 'ACd807f2bde8af5db99312ffc4bae1551c'
auth_token = '41acd9fbdc365814a0a8b84d52cd2083'
client = Client(account_sid, auth_token)
twilio_from = 'whatsapp:+14155238886'
twilio_to = 'whatsapp:+381642538013'

local_tz = pytz.timezone("Europe/Belgrade")

def get_awake_window_range(age_months):
    if age_months < 1:
        return 45, 60
    elif 1 <= age_months < 3:
        return 60, 90
    elif 3 <= age_months < 5:
        return 75, 120
    elif 5 <= age_months < 8:
        return 120, 180
    elif 8 <= age_months < 11:
        return 150, 210
    elif 11 <= age_months < 18:
        return 180, 240
    else:
        return 240, 360

def send_whatsapp_message(message_text):
    message = client.messages.create(
        from_=twilio_from,
        body=message_text,
        to=twilio_to
    )
    print(f"WhatsApp poruka poslata SID: {message.sid}")

def schedule_message(delay_seconds, message_text):
    def task():
        time.sleep(delay_seconds)
        send_whatsapp_message(message_text)
    threading.Thread(target=task).start()

st.title("👶 Baby Sleep & Awake Tracker")

# Podaci o bebi
age_months = st.number_input("Uzrast bebe (meseci)", min_value=0, max_value=36, value=2)

min_awake, max_awake = get_awake_window_range(age_months)
st.write(f"Preporučeni interval budnosti: {min_awake} - {max_awake} minuta")

# Unos ciklusa budnosti (više unosa)
st.markdown("## Unesi cikluse budnosti bebe")
num_cycles = st.number_input("Broj budnih perioda danas", min_value=1, max_value=6, value=2)

cycles = []
now = datetime.datetime.now(local_tz)

for i in range(num_cycles):
    st.markdown(f"### Ciklus {i+1}")
    wake_time = st.time_input(f"Vreme buđenja za ciklus {i+1}", value=(now + datetime.timedelta(minutes=60*i)).time(), key=f"wake{i}")
    awake_length = st.slider(f"Dužina budnosti u minutima (min {min_awake}, max {max_awake})", min_awake, max_awake, min_awake, key=f"awake{i}")
    wake_dt = datetime.datetime.combine(now.date(), wake_time)
    wake_dt = local_tz.localize(wake_dt)
    sleep_dt = wake_dt + datetime.timedelta(minutes=awake_length)
    cycles.append({"wake": wake_dt, "sleep": sleep_dt, "awake_length": awake_length})

# Prikaz grafikona ciklusa
if cycles:
    df = pd.DataFrame([
        {"Period": f"Ciklus {i+1} - Budna", "Start": c["wake"], "End": c["sleep"], "State": "Budna"}
        for i, c in enumerate(cycles)
    ] + [
        {"Period": f"Ciklus {i+1} - Spavanje", "Start": c["sleep"], "End": cycles[i+1]["wake"] if i+1 < len(cycles) else c["sleep"] + datetime.timedelta(minutes=60), "State": "Spavanje"}
        for i, c in enumerate(cycles)
    ])

    base = alt.Chart(df).encode(
        x='Start:T',
        x2='End:T',
        y=alt.Y('Period:N', sort=None),
        color=alt.Color('State:N', scale=alt.Scale(domain=["Budna", "Spavanje"], range=["green", "blue"]))
    )

    bars = base.mark_bar()
    st.altair_chart(bars, use_container_width=True)

# Dugme za zakazivanje podsetnika za prvi ciklus
if st.button("Zakaži WhatsApp podsetnik za prvi spavanje"):
    now = datetime.datetime.now(local_tz)
    sleep_time = cycles[0]["sleep"]
    delay = (sleep_time - now).total_seconds()
    if delay > 0:
        msg = f"⏰ Beba treba da ide na spavanje u {sleep_time.strftime('%H:%M')}."
        schedule_message(delay, msg)
        st.success(f"Podsetnik zakazan za {sleep_time.strftime('%H:%M')}")
    else:
        st.error("Vreme za spavanje je već prošlo.")

