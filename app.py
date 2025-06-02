from datetime import datetime, timedelta
from twilio.rest import Client

# Twilio podaci
account_sid = 'ACd807f2bde8af5db99312ffc4bae1551c'
auth_token = '41acd9fbdc365814a0a8b84d52cd2083'
client = Client(account_sid, auth_token)

# Funkcija za unos vremena
def unesi_vreme(prompt):
    while True:
        try:
            vreme_str = input(prompt + " (format HH:MM): ")
            return datetime.strptime(vreme_str, "%H:%M")
        except ValueError:
            print("Neispravan format, pokušajte ponovo.")

# Funkcija za odredjivanje maksimalnog budnog prozora prema uzrastu
def max_budnost_za_uzrast(uzrast_mjeseci):
    if uzrast_mjeseci <= 0.25:  # 0-4 nedelje
        return timedelta(minutes=45)
    elif uzrast_mjeseci <= 0.75:  # 4-12 nedelja
        return timedelta(minutes=90)
    elif uzrast_mjeseci <= 4/12:  # 3-4 Meseca
        return timedelta(minutes=120)
    elif uzrast_mjeseci <= 7/12:  # 5-7 meseci
        return timedelta(hours=3)
    elif uzrast_mjeseci <= 10/12:  # 7-10 meseci
        return timedelta(hours=3.5)
    elif uzrast_mjeseci <= 18/12:  # 11-18 meseci
        return timedelta(hours=4)
    else:  # 18+ meseci
        return timedelta(hours=6)

# Unos uzrasta bebe u mesecima
uzrast_mjeseci = float(input("Unesite uzrast bebe u mesecima: "))
max_budnost = max_budnost_za_uzrast(uzrast_mjeseci)

# Unos vremena buđenja i uspavljivanja
vreme_budjenja = unesi_vreme("Unesite vreme buđenja")
vreme_uspu = unesi_vreme("Unesite vreme uspavljivanja")

# Pretvaranje u datetime objekat za istu danu
danas = datetime.today()
vreme_budjenja = vreme_budjenja.replace(year=danas.year, month=danas.month, day=danas.day)
vreme_uspu = vreme_uspu.replace(year=danas.year, month=danas.month, day=danas.day)

# Ako je vreme uspavljivanja manje od vremena buđenja, pretpostavljamo da je prešlo u sledeći dan
if vreme_uspu <= vreme_budjenja:
    vreme_uspu += timedelta(days=1)

# Računanje trajanja budnosti
trajanje_budnosti = vreme_uspu - vreme_budjenja

# Provera da li je trajanje duže od maksimuma
if trajanje_budnosti > max_budnost:
    print("Upozorenje: trajanje budnosti je duže od preporučenog!")
    # Slanje WhatsApp poruke
    poruka = client.messages.create(
        from_='whatsapp:+14155238886',
        body='Upozorenje: trajanje budnosti vaše bebe je duže od preporučenog.',
        to='whatsapp:+381642538013'
    )
    print(f"Poruka poslata, SID: {poruka.sid}")
else:
    print("Trajanje budnosti je unutar preporučenih granica.")

print(f"Trajanje budnosti: {trajanje_budnosti}")
