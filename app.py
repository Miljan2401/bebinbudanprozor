import streamlit as st
import datetime
import time
import threading
from twilio.rest import Client
import pytz

# Twilio kredencijali
account_sid = 'ACd807f2bde8af5db99312ffc4bae1551c'
auth_token = '41acd9fbdc365814a0a8b84d52cd2083'
client = Client(account_sid, auth_token)

# Lokalna vremenska zona
local_tz = pytz.timezone("Europe/Belgrade")

# Funkcija za minimalnu i maksimalnu budnost po uzrastu
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

# Funkcija za slanje WhatsApp poruke
def send_whatsapp_message(wake_time, sleep_time):
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
        content_variables=f'{{"1":"{wake_time.strftime("%H:%M")}","2":"{sleep_time.strftime("%H:%M")}"}}',
        to='whatsapp:+381642538013'
    )
    print(f"📤 WhatsApp poruka poslata! SID: {message.sid}")

# Funkcija za zakazivanje obaveštenja
def schedule_notification(wake_time, sleep_time):
    def notify():
        now = datetime.datetime.now(local_tz)
        seconds_to_wait = (sleep_time - now).total_seconds()

        print(f"[DEBUG] Trenutno vreme: {now.strftime('%H:%M:%S')}")
        print(f"[DEBUG] Zakazano vreme za uspavljivanje: {sleep_time.strftime('%H:%M:%S')}")
        print(f"[DEBUG] Čekanje {seconds_to_wait:.1f} sekundi...")

        if seconds_to_wait > 0:
            time.sleep(seconds_to_wait)
        send_whatsapp_message(wake_time, sleep_time)

    t = threading.Thread(target=notify)
    t.start()

# === Streamlit UI ===
st.set_page_config(page_title="Beba Tracker", page_icon="👶", layout="centered")
st.title("🍼 Baby Awake Tracker")

st.markdown("Unesi podatke da bi dobio preporučeni interval budnosti i vreme za spavanje + WhatsApp obaveštenje.")

age_months = st.number_input("Uzrast bebe (u mesecima)", min_value=0, max_value=36, value=2)
wake_time_input = st.time_input("Vreme buđenja bebe", value=datetime.datetime.now(local_tz).time())

# Prikaži interval budnosti
min_awake, max_awake = get_awake_window_range(age_months)
st.write(f"Preporučeni interval budnosti: **{min_awake} - {max_awake} minuta**")

# Korisnik bira koliko će beba biti budna (u okviru intervala)
awake_minutes = st.slider("Izaberi koliko dugo će beba biti budna (minuta)", min_awake, max_awake, value=min_awake)

start_button = st.button("📤 Započni praćenje")

if start_button:
    now = datetime.datetime.now(local_tz)
    wake_time = datetime.datetime.combine(now.date(), wake_time_input)
    wake_time = local_tz.localize(wake_time)

    sleep_time = wake_time + datetime.timedelta(minutes=awake_minutes)

    st.success(f"🕒 Preporučeno vreme za spavanje: **{sleep_time.strftime('%H:%M')}**")
    st.info("✅ Bićeš obavešten na WhatsApp kada dođe vreme za spavanje.")

    schedule_notification(wake_time, sleep_time)
