from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import speech_recognition as sr
from gtts import gTTS as g
import os
from playsound import playsound
import sys

def rozpoznaj(tekst):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        powiedz(tekst)
        audio = r.listen(source)
    try:
        zdanie = r.recognize_google(audio, language='pl-PL')

    except sr.UnknownValueError:
        zdanie = "Nie rozumiem"
    except sr.RequestError as e:
        zdanie = "Błąd; {0}".format(e)
    print(zdanie)
    return zdanie


def powiedz(tekst):
    tts = g(tekst, lang='pl', )
    tts.save('tts_example.mp3')
    playsound('tts_example.mp3')
    os.remove('tts_example.mp3')


def str_to_num(s):
    with open('slownik.pkl', 'rb') as f:
        slownik = pickle.load(f)

    for i in slownik.items():
        if any(s in j for j in i[1]):
            s = i[0]
        if len(s) == 1:
            s = "0" + s
    return s


def dni_tygodnia(odpowiedz, rozpoczecie=0):
    today = datetime.datetime.now().date()
    today_index = today.weekday()

    if rozpoczecie > odpowiedz:
        start = today + datetime.timedelta(days=(7 - today_index))
    elif odpowiedz < today_index:
        start = today + datetime.timedelta(days=(7 - today_index))
    else:
        start = today - datetime.timedelta(days=today.weekday())
    start = (str(start))[-2:]
    rok = (str(today))[0:4]
    miesiac = (str(today))[5:7]
    dict = {
        start: ['0'],
        str("{:0>2d}".format(int(start) + 1)): ['1'],
        str("{:0>2d}".format(int(start) + 2)): ['2'],
        str("{:0>2d}".format(int(start) + 3)): ['3'],
        str("{:0>2d}".format(int(start) + 4)): ['4'],
        str("{:0>2d}".format(int(start) + 5)): ['5'],
        str("{:0>2d}".format(int(start) + 6)): ['6']}
    odpowiedz = str(odpowiedz)
    for i in dict.items():
        if any(odpowiedz in j for j in i[1]):
            odpowiedz = i[0]
            return rok, miesiac, odpowiedz

    powiedz("Źle podany dzień tygodnia")
    return False


def godziny(odpowiedz):

    podzialka = odpowiedz.split()
    for i in podzialka:
        if ":" in i and len(i) <= 5:
            return i
    return False


def minuty(odpowiedz):
    odpowiedz = str_to_num(odpowiedz)
    if odpowiedz.isnumeric():
        if int(odpowiedz) >= 0 and int(odpowiedz) <= 59:
            return odpowiedz
        else:
            return False
    else:
        return False


def czestosc(jak_czesto):
    if jak_czesto.lower() == "ignoruj":
        return jak_czesto
    with open('slownik.pkl', 'rb') as f:
        slownik = pickle.load(f)

    for i in slownik.items():
        if any(jak_czesto in j for j in i[1]):
            jak_czesto = i[0]

    powtorz = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']
    if any(jak_czesto in i for i in powtorz):
        return jak_czesto
    else:
        return False


def ilosc(ile_razy):
    ile_razy = str_to_num(ile_razy)
    if ile_razy.isnumeric():
        if int(ile_razy) > 0:
            return ile_razy
    else:
        return False


def metoda(sposob):
    if sposob.lower() == "ignoruj":
        return sposob
    with open('slownik.pkl', 'rb') as f:
        slownik = pickle.load(f)

    for i in slownik.items():
        if any(sposob in j for j in i[1]):
            sposob = i[0]
    opcje = ['email', 'popup']
    if any(sposob in i for i in opcje):
        return sposob
    else:
        return False


def data(odpowiedz, rozpoczecie=0):

    with open('slownik.pkl', 'rb') as f:
        slownik = pickle.load(f)

    odpowiedz = odpowiedz.lower()
    podzialka = odpowiedz.split()
    lista_dni = ['pon', 'wt', 'śr', 'czw', 'piąt', 'sob', 'niedz']
    today = datetime.datetime.now().date()
    rok = (str(today))[0:4]
    miesiac = 'coś'
    dzien = 'coś innego'

    if odpowiedz.find("dzisiaj") != -1:
        today = str(today)
        list = today.split("-")
        rok = list[0]
        miesiac = list[1]
        dzien = list[2]
        odpowiedz = datetime.datetime(int(rok), int(miesiac), int(dzien)).weekday()
        return rok, miesiac, dzien, odpowiedz
    elif odpowiedz.find("jutro") != -1:
        today = str(today)
        list = today.split("-")
        rok = list[0]
        miesiac = list[1]
        dzien = list[2]
        dzien = str("{:0>2d}".format(int(dzien) + 1))
        odpowiedz = datetime.datetime(int(rok), int(miesiac), int(dzien)).weekday()
        return rok, miesiac, dzien, odpowiedz
    elif odpowiedz.find("pojutrze") != -1:
        today = str(today)
        list = today.split("-")
        rok = list[0]
        miesiac = list[1]
        dzien = list[2]
        dzien = str("{:0>2d}".format(int(dzien) + 2))
        odpowiedz = datetime.datetime(int(rok), int(miesiac), int(dzien)).weekday()
        return rok, miesiac, dzien, odpowiedz
    elif 'przyszł' in odpowiedz.lower():
        for i in lista_dni:
            if i in odpowiedz.lower():
                odpowiedz = lista_dni.index(i)
                rok, miesiac, dzien = dni_tygodnia(odpowiedz, 10)
                return rok, miesiac, dzien, odpowiedz
    else:
        if ":" not in odpowiedz:
            for i in lista_dni:
                if odpowiedz.find(i) != -1:
                    odpowiedz = lista_dni.index(i)
                    rok, miesiac, dzien = dni_tygodnia(odpowiedz, rozpoczecie)
                    return rok, miesiac, dzien, odpowiedz
            for k in podzialka:
                if k.isnumeric() and (len(k) == 2 or len(k)==1):
                    dzien = k
                if k.isnumeric() and len(k) == 4 and k>rok:
                    rok = k
                for i in slownik.items():
                    if any(k == j for j in i[1]) and k.isnumeric() == False:
                        miesiac = i[0]
                        odpowiedz = datetime.datetime(int(rok), int(miesiac), int(dzien)).weekday()
                        return rok, miesiac, dzien, odpowiedz
        rok = False
        miesiac = False
        dzien = False
        return rok, miesiac, dzien


def poprawa(odp, rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1,
                                        nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki):
    if "data rozpoczęci" in odp or "początek" in odp:
        rok, miesiac, dzien, *id= data(rozpoznaj("Kiedy ma się rozpocząć wydarzenie?"))
        while rok == False:
            rok, miesiac, dzien, *id = data(rozpoznaj("Źle podana data. Spróbuj ponownie"))

    elif "godzina rozpoczęcia" in odp or "czas rozpoczęcia" in odp or "godzinę rozpoczęcia" in odp:
        godzina = godziny(rozpoznaj("Podaj godzinę rozpoczęcia"))
        while godzina == False:
            godzina = godziny(rozpoznaj("Źle podana godzina. Spróbuj ponownie"))

    elif "data zakończ" in odp or "koniec" in odp:
        rok1, miesiac1, dzien1, *id = data(rozpoznaj("Kiedy ma się zakończyć wydarzenie?"))
        while rok1 == False:
            rok1, miesiac1, dzien1, *id = data(rozpoznaj("Źle podana data. Spróbuj ponownie"))

    elif "godzina zakończ" in odp or "czas zakończ" in odp or "godzinę zakończ" in odp:
        godzina1 = godziny(rozpoznaj("Podaj godzinę zakończenia"))
        while godzina1 == False:
            godzina1 = godziny(rozpoznaj("Źle podana godzina. Spróbuj ponownie"))

    elif "nazw" in odp or "tytuł" in odp:
        nazwa = rozpoznaj("Podaj nazwę wydarzenia")

    elif "opis" in odp:
        opis = rozpoznaj("Podaj opis lub powiedz 'ignoruj'")
        if opis.lower() == "ignoruj":
            opis = False

    elif "lokali" in odp or "miejsc" in odp:
        lokalizacja = rozpoznaj("Podaj lokalizację lub powiedz 'ignoruj'")
        if lokalizacja.lower() == "ignoruj":
            lokalizacja = False

    elif "częstość powtarz" in odp or "powtarz" in odp:
        jak_czesto = czestosc(rozpoznaj(
            "Jak często ma się powtarzać wydarzenie? (Jeśli wydarzenie ma być jednorazowe powiedz 'ignoruj')"))
        while jak_czesto == False:
            jak_czesto = czestosc(rozpoznaj("Nie ma takiej opcji. Wybierz: codziennie, co tydzień, co miesiąc, co rok. Spróbuj ponownie"))

    elif "liczb" in odp:
        liczba = ilosc(rozpoznaj("Ile razy ma się powtórzyć wydarzenie?"))
        while liczba == False:
            liczba = ilosc(rozpoznaj("Podaj samą liczbę."))

    elif "sposób" in odp or "metoda" in odp or "powiadomieni" in odp or 'email' in odp or "rodzaj" in odp or "przypomnieni" in odp:
        sposob = metoda(rozpoznaj("Podaj sposób przypomnienia lub powiedz 'ignoruj'"))
        while sposob == False:
            sposob = metoda(rozpoznaj("Nie ma takiej opcji. Wybierz: powiadomienie lub email. Spróbuj ponownie"))

    elif "czas przyp" in odp or "czas powiadomieni" in odp:
        minutki = minuty(rozpoznaj("Ile minut przed ma być przypomnienie?")) #fajnie by bylo dodać godiznowe przypomnienia
        while minutki == False:
            minutki = ilosc(rozpoznaj("Źle podane minuty. Spróbuj ponownie"))

    else:
        powiedz("Nie ma takiej opcji! Spróbuj ponownie")
        rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa(rozpoznaj("powiedz ponownie, co chcesz poprawić"), rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)
    return rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki


def dodaj_do_kalendarza(rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja,
                        czest_powtarzania, ilosc_powtorzen, metoda_przypomnienia, czas_przypomnienia):
    startTime = rok + "-" + miesiac + "-" + dzien + "T" + godzina + ":00+01:00"
    endTime = rok1 + "-" + miesiac1 + "-" + dzien1 + "T" + godzina1 + ":00+01:00"
    event = {
        'summary': nazwa,
        'start': {
            'dateTime': startTime,
            'timeZone': 'Europe/Warsaw',
        },
        'end': {
            'dateTime': endTime,
            'timeZone': 'Europe/Warsaw',
        },
    }
    if lokalizacja != False:
        event["location"] = lokalizacja
    if opis != False:
        event["description"] = opis
    if czest_powtarzania.lower() != "ignoruj":
        event["recurrence"] = ['RRULE:FREQ=' + czest_powtarzania + ';COUNT=' + str(ilosc_powtorzen)]
    if metoda_przypomnienia.lower() != "ignoruj":
        event["reminders"] = {'useDefault': False,
            'overrides': [{'method': metoda_przypomnienia, 'minutes': czas_przypomnienia}]}
    return event


def dodaj_wydarzenie(service):

    rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o'

    rok, miesiac, dzien, *id = data(rozpoznaj("W jaki dzień ma się rozpocząć wydarzenie?"))
    while rok == False:
        rok, miesiac, dzien, *id = data(rozpoznaj("Źle podana data. Spróbuj ponownie"))

    godzina = godziny(rozpoznaj("Podaj godzinę rozpoczęcia"))
    while godzina == False:
        godzina = godziny(rozpoznaj("Źle podana godzina. Spróbuj ponownie"))

    odp = rozpoznaj("W jaki dzień ma się zakończyć wydarzenie?")
    if 'sam' in odp:
        rok1, miesiac1, dzien1 = rok, miesiac, dzien
    else:
        rok1, miesiac1, dzien1, *id1 = data(odp, id[0])

    while rok1 == False:
        odp1 = rozpoznaj("Źle podana data. Spróbuj ponownie")
        if 'sam' in odp:
            rok1, miesiac1, dzien1 = rok, miesiac, dzien
        else:
            rok1, miesiac1, dzien1, *id1 = data(odp1, id[0])

    godzina1 = godziny(rozpoznaj("Podaj godzinę zakończenia"))
    while godzina1 == False:
        godzina1 = godziny(rozpoznaj("Źle podana godzina. Spróbuj ponownie"))

    if rok1 == rok:
        if miesiac1 == miesiac:
            if dzien1 == dzien:
                if godzina1 < godzina:
                    powiedz("Niepoprawne godziny")
                    rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa("godzina rozpoczęcia",rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)
                    rok, miesiac, dzien, godzinka, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa("godzina zakończenia", rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)
            elif dzien1 < dzien:
                powiedz("Niepoprawne dni")
                roczek, mies, dzien, godzinka, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa("data rozpoczęcia", rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)
                rok, miesiac, dzien, godzina, roczek1, mies1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa("data zakończenia", rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)
        elif miesiac1 < miesiac:
            powiedz("Niepoprawne miesiące")
            roczek, miesiac, dzionek, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa("data rozpoczęcia", rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)
            rok, miesiac, dzien, godzina, roczek1, miesiac1, dzionek1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa("data zakończenia", rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)
    elif rok1 < rok:
        powiedz("Niepoprawne lata. Spróbuj ponownie")
        rok, mies, dzionek, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa("data rozpoczęcia", rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)
        rok, miesiac, dzien, godzina, rok1, mies1, dzionek1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa("data zakończenia", rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)

    nazwa = rozpoznaj("Podaj nazwę wydarzenia")
    nazwa = nazwa.capitalize()

    opis = rozpoznaj("Podaj opis lub powiedz 'ignoruj'")
    if "ignor" in opis.lower() :
        opis = False

    lokalizacja = rozpoznaj("Podaj lokalizację lub powiedz 'ignoruj'")
    if "ignor" in lokalizacja.lower() :
        lokalizacja = False

    jak_czesto = czestosc(rozpoznaj("Jak często ma się powtarzać wydarzenie? (Jeśli wydarzenie ma być jednorazowe powiedz 'ignoruj'"))
    while jak_czesto == False:
        jak_czesto = czestosc(rozpoznaj("Nie ma takiej opcji. Wybierz: codziennie, co tydzień, co miesiąc, co rok. Spróbuj ponownie"))

    if "ignor" not in jak_czesto.lower():
        liczba = ilosc(rozpoznaj("Ile razy ma się powtórzyć wydarzenie?"))
        while liczba == False:
            liczba = ilosc(rozpoznaj("Podaj samą liczbę. Spróbuj ponownie"))
    else:
        liczba = 0

    sposob = metoda(rozpoznaj("Podaj sposób przypomnienia lub powiedz 'ignoruj'"))
    while sposob == False:
        sposob = metoda(rozpoznaj("Nie ma takiej opcji. Wybierz: powiadomienie lub email. Spróbuj ponownie"))

    if "ignor" not in sposob.lower():
        minutki = minuty(rozpoznaj("Ile minut przed ma być przypomnienie?"))
        while minutki == False:
            minutki = ilosc(rozpoznaj("Źle podane minuty. Spróbuj ponownie"))
    else:
        minutki = 0

    print("Twoje wydarzenie: \nPoczątek wydarzenia:\n" + str(dzien) +"-"+ str(miesiac) +"-"+ str(rok) + "\nGodzina rozpoczęcia: " + str(godzina) + "\nKoniec wydarzenia:\n" + str(dzien1) +"-"+ str(miesiac1) +"-"+ str(rok1) + "\nGodzina zakończenia: " + str(godzina1) + "\nNazwa wydarzenia: " + str(nazwa))
    powiedz("Twoje wydarzenie: \nPoczątek wydarzenia:\n" + str(dzien) +"-"+ str(miesiac) +"-"+ str(rok) + "\nGodzina rozpoczęcia: " + str(godzina) + "\nKoniec wydarzenia:\n" + str(dzien1) +"-"+ str(miesiac1) +"-"+ str(rok1) + "\nGodzina zakończenia: " + str(godzina1) + "\nNazwa wydarzenia: " + str(nazwa))

    if opis!=False:
        powiedz("Opis wydarzenia: "+str(opis))
        print("Opis wydarzenia: " + str(opis))
    if lokalizacja != False:
        powiedz("Lokalizacja: "+str(lokalizacja))
        print("Lokalizacja: " + str(lokalizacja))
    if jak_czesto == "DAILY":
        if liczba[0]=='0':
            powiedz("Powtarzanie - " + str(liczba[1]) + " razy codziennie")
            print("Powtarzanie " + str(liczba[1]) + " razy codziennie")
    if jak_czesto == "WEEKLY":
        if liczba[0] == '0':
            powiedz("Powtarzanie - " + str(liczba[1]) + " razy co tydzień")
            print("Powtarzanie " + str(liczba[1]) + " razy co tydzień")
    if jak_czesto == "MONTHLY":
        if liczba[0] == '0':
            powiedz("Powtarzanie -" + str(liczba[0]) + " razy co miesiąc")
            print("Powtarzanie " + str(liczba[0]) + " razy co miesiąc")
    if jak_czesto == "YEARLY":
        if liczba[0] == '0':
            powiedz("Powtarzanie -" + str(liczba[1]) + " razy co rok")
            print("Powtarzanie " + str(liczba[1]) + " razy co rok")
    if sposob=='popup':
        if minutki[0]=='0':
            if '2' in str(minutki) or '3' in str(minutki) or '4' in str(minutki):
                powiedz("Powiadomienie - "+str(minutki[1])+" minuty przed")
                print("Powiadomienie " + str(minutki[1]) + " minuty przed")
            else:
                powiedz("Powiadomienie - "+str(minutki[1])+" minut przed")
                print("Powiadomienie " + str(minutki[1]) + " minut przed")
    if sposob=='email':
        if minutki[0]=='0':
            powiedz("Email -"+str(minutki[1])+" minut przed")
            print("Email " + str(minutki[1]) + " minut przed")


    odpowiedz = rozpoznaj("Jeśli powyższe dane są poprawne powiedz 'akceptuj', jeśli nie powiedz 'popraw'")


    stan = False
    while stan == False:
        stan1 = True
        while stan1:
            if 'akcept' in odpowiedz or 'popraw' in odpowiedz:
                stan1 = False
            else:
                odpowiedz = rozpoznaj("Nie rozumiem. Powiedz akceptuj lub popraw")
        if "popraw" in odpowiedz:
            odp = rozpoznaj("Co się nie zgadza?")
            rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1, nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki = poprawa(odp, rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1,nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)

        elif "akceptuj" in odpowiedz:
            event = dodaj_do_kalendarza(rok, miesiac, dzien, godzina, rok1, miesiac1, dzien1, godzina1,
                                        nazwa, opis, lokalizacja, jak_czesto, liczba, sposob, minutki)
            event = service.events().insert(calendarId='primary', body=event).execute()
            powiedz("Dodano wydarzenie")
            print('Dodano wydarzenie: %s' % (event.get('htmlLink')))
            break
        else:
            powiedz("Nie rozumiem. Powiedz 'akceptuję lub 'popraw'")

        print("Twoje wydarzenie: \nPoczątek wydarzenia:\n" + str(dzien) +"-"+ str(miesiac) +"-"+ str(rok) + "\nGodzina rozpoczęcia: " + str(godzina) + "\nKoniec wydarzenia:\n" + str(dzien1) +"-"+ str(miesiac1) +"-"+ str(rok1) + "\nGodzina zakończenia: " + str(godzina1) + "\nNazwa wydarzenia: " + str(nazwa))
        powiedz("Twoje wydarzenie: \nPoczątek wydarzenia:\n" + str(dzien) +"-"+ str(miesiac) +"-"+ str(rok) + "\nGodzina rozpoczęcia: " + str(godzina) + "\nKoniec wydarzenia:\n" + str(dzien1) +"-"+ str(miesiac1) +"-"+ str(rok1) + "\nGodzina zakończenia: " + str(godzina1) + "\nNazwa wydarzenia: " + str(nazwa))

        if opis != False:
            powiedz("Opis wydarzenia:" + str(opis))
            print("\nOpis wydarzenia: " + str(opis))
        if lokalizacja != False:
            powiedz("Lokalizacja:" + str(lokalizacja))
            print("Lokalizacja: " + str(lokalizacja))
        if jak_czesto == "DAILY":
            if liczba[0] == '0':
                powiedz("Powtarzanie " + str(liczba[1]) + " razy codziennie")
                print("Powtarzanie " + str(liczba[1]) + " razy codziennie")
        if jak_czesto == "WEEKLY":
            if liczba[0] == '0':
                powiedz("Powtarzanie " + str(liczba[1]) + " razy co tydzień")
                print("Powtarzanie " + str(liczba[1]) + " razy co tydzień")
        if jak_czesto == "MONTHLY":
            if liczba[0] == '0':
                powiedz("Powtarzanie " + str(liczba[0]) + " razy co miesiąc")
                print("Powtarzanie " + str(liczba[0]) + " razy co miesiąc")
        if jak_czesto == "YEARLY":
            if liczba[0] == '0':
                powiedz("Powtarzanie " + str(liczba[1]) + " razy co rok")
                print("Powtarzanie " + str(liczba[1]) + " razy co rok")
        if sposob == 'popup':
            if minutki[0] == '0':
                if '2' in str(minutki) or '3' in str(minutki) or '4' in str(minutki):
                    powiedz("Powiadomienie - " + str(minutki[1]) + " minuty przed")
                    print("Powiadomienie " + str(minutki[1]) + " minuty przed")
                else:
                    powiedz("Powiadomienie - " + str(minutki[1]) + " minut przed")
                    print("Powiadomienie " + str(minutki[1]) + " minut przed")
        if sposob == 'email':
            if minutki[0] == '0':
                powiedz("Email " + str(minutki[1]) + " minut przed")
                print("Email " + str(minutki[1]) + " minut przed")

        odpowiedz = rozpoznaj("Jeśli powyższe dane są poprawne powiedz 'akceptuj', jeśli nie powiedz 'popraw'")


def wyswietl(service, liczba_wydarzen):

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print('Getting the upcoming ' + str(liczba_wydarzen) + ' events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=liczba_wydarzen, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('Nie masz nadchodzących wydarzeń.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


def odczytywanie(service, odp):

    if odp.isnumeric():
        odp=int(odp)
    else:
        powiedz('Nie rozumiem')
        return False

    if odp <= 10:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=odp, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('Nie masz nadchodzących wydarzeń.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            dzien = str(start)[8:10]
            miesiac = str(start)[5:7]
            rok = str(start)[:4]
            powiedz(dzien + '-' + miesiac + '-' + rok + event['summary'])
        return True
    else:
        powiedz('Mogę odczytać maksymalnie 10 wydarzeń.')
        return False


def interfejs(service, odp):

    if 'doda' in odp.lower():
        dodaj_wydarzenie(service)
        odpowiedz = rozpoznaj("Chcesz dodać kolejne wydarzenie, wyświetlić wydarzenia, odczytać wydarzenia czy zamknąć program?")
        interfejs(service, odpowiedz)
    elif 'wyświetl' in odp.lower():
        liczba1 = rozpoznaj("Ile najbliższych wydarzeń chcesz wyświetlić?")
        liczba = ilosc(liczba1)
        while liczba == False:
            liczba1 = rozpoznaj("Podaj samą liczbę")
            liczba = ilosc(liczba1)
        wyswietl(service, liczba)
        odpowiedz = rozpoznaj("Chcesz dodać wydarzenie, wyświetlić ponownie wydarzenia, odczytać wydarzenia czy zamknąć program?")
        interfejs(service, odpowiedz)
    elif 'czyta' in odp.lower():
        odp = rozpoznaj('Ile wydarzeń chcesz odczytać')
        odp2 = odczytywanie(service, odp)
        while odp2 == False :
            odp = rozpoznaj('Podaj inną liczbę.')
            odp2 = odczytywanie(service, odp)
        odpowiedz = rozpoznaj("Chcesz dodać wydarzenie, wyświetlić ponownie wydarzenia, odczytać wydarzenia czy zamknąć program?")
        interfejs(service, odpowiedz)
    elif 'zamkn' in odp.lower():
        powiedz("Dziękuję za współpracę. Do usłyszenia.")
        sys.exit()
    else:
        odpowiedz = rozpoznaj("Nie ma takiej opcji. Możesz dodać wydarzenie, wyświetlić wydarzenia, odczytać wydarzenia lub zamknąć program")
        interfejs(service, odpowiedz)


def main():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)


    odp = rozpoznaj("Tu twój organizer głosowy. Chcesz dodać wydarzenie, wyświetlić wydarzenia, odczytać wydarzenia czy zamknąć program?")
    interfejs(service, odp)


if __name__ == '__main__':
    main()
