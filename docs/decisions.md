# Dziennik decyzji

## Krok 1. Rozpoznanie danych ZTP (2026-10-02)

**Dostępne dane.** Serwer gtfs.ztp.krakow.pl udostępnia trzy grupy danych: A (autobusy MPK), T (tramwaje) i M (autobusy przewoźnika Mobilis). Każda grupa ma rozkład GTFS (.zip) oraz trzy strumienie GTFS-Realtime: VehiclePositions, TripUpdates i ServiceAlerts. Do projektu włączamy wszystkie trzy grupy, bo z perspektywy pasażera to jedna sieć, a grupa M odpowiada tylko za około 10% danych.

**Charakter danych.** Pliki realtime odświeżają się co około 10 s. TripUpdates podają prognozowane godziny przyjazdu (średnio 12–15 kolejnych przystanków na kurs), ale nie podają opóźnienia wprost: pole `delay` jest puste. Opóźnienie trzeba więc liczyć względem rozkładu, przez co archiwizacja kolejnych wersji GTFS jest konieczna.

**Częstotliwość odpytywania: 60 s.** Rozważaliśmy 10, 30, 60 i 120 s. Przy 10 s danych byłoby kilka razy więcej przy niewielkim zysku. Przy 120 s ginęłyby przejazdy przez przystanki, bo między przystankami jedzie się 1–2 min, a błąd pomiaru (±60 s) byłby porównywalny z samymi opóźnieniami. Przy 60 s precyzja wynosi ±30 s przy akceptowalnym rozmiarze danych.

**Zakres zapisu.** Nie zapisujemy surowych plików .pb, bo przy 10 s dawałoby to około 2,8 GB na dobę. Zapisujemy wybrane pola do CSV kompresowanego gzipem: pozycje pojazdów co 60 s, z TripUpdates tylko najbliższy przystanek co 60 s, a pełne TripUpdates co 5 min jako punkt odniesienia do porównania naszego modelu z prognozą ZTP. Pomiar (skrypt `scripts/measure_storage.py`, w nocy) dał około 27,5 MB na dobę. Pełne TripUpdates co 5 min to około 1,5 raza więcej niż sam najbliższy przystanek, co uznaliśmy za akceptowalny koszt.

**Licencja.** Ani strona z plikami, ani `feed_info.txt` nie podają licencji. Wydawcą metadanych jest R&G PLUS Sp. z o.o., a bieżący rozkład jest ważny od 2026-09-30 do 2027-01-31. Status licencji ustalamy bezpośrednio z ZTP (zapytanie mailowe).
