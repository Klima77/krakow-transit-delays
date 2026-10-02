# Uwagi na później

Obserwacje z etapu zbierania danych, ważne dla liczenia opóźnień, modelu, planera i mapy.

## Dostępność danych
- Zdarzają się zaplanowane przerwy techniczne (np. 12.07.2026: 8 h bez GTFS-RT dla autobusów MPK). Analiza musi obsługiwać dłuższe dziury w danych.
- Pliki .pb bywają chwilowo puste (`Content-Length: 0`) albo uszkodzone (`Wire format was corrupt`), bo serwer nadpisuje je w miejscu. W danych będą pojedyncze brakujące migawki.
- Serwer zwraca nagłówek `Last-Modified`. Można go użyć w zapytaniach warunkowych (`If-Modified-Since`, odpowiedź 304).
- Rozmiary zmierzyliśmy tylko w nocy (236 pojazdów). Trzeba powtórzyć pomiar w szczycie.

## Identyfikatory
- Autobusy MPK i tramwaje mają zupełnie inne formaty `trip_id`: `20260930_4_128828036_21` kontra `block_354_trip_17_service_4`. Najpewniej pochodzą z różnych systemów.
- `trip_id` autobusów zaczyna się od daty wersji rozkładu, więc po zmianie rozkładu identyfikatory się zmienią. Każdą migawkę trzeba łączyć z właściwą wersją GTFS.
- Tramwaje nie mają `route_id` w VehiclePositions. Linię trzeba odczytać przez `trips.txt`.
- Tramwaje używają `stop_id` w formacie `stop_258_44219`, a autobusy liczbowych (`8112`). Trzy paczki GTFS (A, T, M) trzeba połączyć w jedną sieć i zmapować przystanki.

## Jakość pól
- `speed` u autobusów wynosi 0 nawet w ruchu, a u tramwajów pola brak. Prędkość ewentualnie liczymy sami.
- `occupancy_status: EMPTY` u tramwajów może być wartością domyślną. Do sprawdzenia na danych z dnia.
- Prognozy w TripUpdates przypadają równo co 60 s między przystankami, co wygląda na prognozę wyliczoną z rozkładu. Trzeba zbadać ich jakość, bo to punkt odniesienia dla modelu.
- Bieżący rozkład (`feed_info.txt`) jest ważny do 2027-01-31, czyli do końca okresu zbierania. Zmiany rozkładu w trakcie są jednak prawdopodobne.
