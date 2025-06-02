from datetime import datetime, timedelta
from twilio.rest import Client

# Twilio podaci
account_sid = 'ACd807f2bde8af5db99312ffc4bae1551c'
auth_token = '41acd9fbdc365814a0a8b84d52cd2083'
client = Client(account_sid, auth_token)

# Funkcija za odredjivanje maksimalnog perioda budnosti na osnovu uzrasta
def dohvati_maksimum_budnosti(uzrast_mjeseci):
    if uzrast_mjeseci <= 0.5:
        return 45, 60
    elif uzrast_mjeseci <= 3:
        return 60, 90
    elif uzrast_mjeseci <= 4:
        return 75, 120
    elif uzrast_mjeseci <= 7:
        return 120, 180
    elif uzrast_mjeseci <= 10:
        return 150, 210
    elif uzrast_mjeseci <= 18:
        return 180, 240
    else:
        return 240, 360

# Inputi
uzrast_mjeseci = float(input("Unesite uzrast bebe u mesecima: "))
vreme_budenja_input = input("Unesite vreme buđenja (format HH:MM, 24h): ")
vreme_uspavljivanja_input = input("Unesite vreme uspavljivanja (format HH:MM, 24h): ")

# Konvertovanje u datetime objekte
vreme_budenja = datetime.strptime(vreme_budenja_input, "%H:%M")
vreme_uspavljivanja = datetime.strptime(vreme_uspavljivanja_input, "%H:%M")

# Dohvatanje maksimuma budnosti
max_budnost_min, max_budnost_max = dohvati_maksimum_budnosti(uzrast_mjeseci)
print(f"Maksimalna budnost za uzrast {uzrast_mjeseci} meseci je između {max_budnost_min} i {max_budnost_max} minuta.")

# Izračun sledećeg vremena buđenja
sledece_budjenje_min = vreme_uspavljivanja + timedelta(minutes=max_budnost_min)
sledece_budjenje_max = vreme_uspavljivanja + timedelta(minutes=max_budnost_max)

print(f"Sledeće vreme buđenja će biti između: {sledece_budjenje_min.strftime('%H:%M')} i {sledece_budjenje_max.strftime('%H:%M')}.")

# Slanje WhatsApp poruke
poruka = f"Planirano sledeće buđenje vaše bebe je između {sledece_budjenje_min.strftime('%H:%M')} i {sledece_budjenje_max.strftime('%H:%M')}."

message = client.messages.create(
    from_='whatsapp:+14155238886',
    content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
    content_variables='{"1":"' + datetime.now().strftime('%m/%d') + '", "2":"' + message + '"}',
    to='whatsapp:+381642538013'
)

print(f"Poruka poslata, SID: {message.sid}")
