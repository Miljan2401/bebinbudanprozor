import streamlit as st
import datetime
import time
import threading
from twilio.rest import Client

# Twilio kredencijali
account_sid = 'ACd807f2bde8af5db99312ffc4bae1551c'
auth_token = '41acd9fbdc365814a0a8b84d52cd2083'
client = Client(account_sid, auth_token)

# Funkcija za maksimalnu budnost po uzrastu
def get_awake_window(age_months):
    if age_months < 1:
        return 60
    elif 1 <= age_months < 3:
        return 90
    elif 3 <= age_months < 5:
        return 120
    elif 5 <= age_months < 8:
        return 180
    elif 8 <= age_months < 11:
        return 210
    elif 11 <= age_months < 18:
        return 240
    else:
        return 360

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
        seconds_to_wait = (sleep_time - datetime.datetime.now()).total_seconds()
        if seconds_to_wait > 0:
            time.sleep(seconds_to_wait)
        send_whatsapp_message(wake_time, sleep_time)

    t = threading.Thread(target=notify)
    t.start()

# === Streamlit UI ===
st.set_page_config(page_title="Beba Tracker", page_icon="👶", layout="centered")
st.title("🍼 Baby Awake Tracker")

st.markdown("Unesi podatke da bi dobio predlog kada da bebu uspavaš + WhatsApp obaveštenje.")

age_months = st.number_input("Uzrast bebe (u mesecima)", min_value=0, max_value=36, value=4)
wake_time_input = st.time_input("Vreme buđenja bebe", value=datetime.datetime.now().time())
start_button = st.button("📤 Započni praćenje")

if start_button:
    now = datetime.datetime.now()
    wake_time = datetime.datetime.combine(now.date(), wake_time_input)
    awake_minutes = get_awake_window(age_months)
    sleep_time = wake_time + datetime.timedelta(minutes=awake_minutes)

    st.success(f"🕒 Preporučeno vreme za spavanje: **{sleep_time.strftime('%H:%M')}**")
    st.info("✅ Bićeš obavešten na WhatsApp kada dođe vreme za spavanje.")

    schedule_notification(wake_time, sleep_time)
