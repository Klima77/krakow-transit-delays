# Dziennik decyzji

## Krok 1. Rozpoznanie danych ZTP (2026-10-02)

**Dostępne dane.** Serwer gtfs.ztp.krakow.pl udostępnia trzy grupy danych: A (autobusy MPK), T (tramwaje) i M (autobusy przewoźnika Mobilis). Każda grupa ma rozkład GTFS (.zip) oraz trzy strumienie GTFS-Realtime: VehiclePositions, TripUpdates i ServiceAlerts. Do projektu włączamy wszystkie trzy grupy, bo z perspektywy pasażera to jedna sieć, a grupa M odpowiada tylko za około 10% danych.

**Charakter danych.** Pliki realtime odświeżają się co około 10 s. TripUpdates podają prognozowane godziny przyjazdu (średnio 12–15 kolejnych przystanków na kurs), ale nie podają opóźnienia wprost: pole `delay` jest puste. Opóźnienie trzeba więc liczyć względem rozkładu, przez co archiwizacja kolejnych wersji GTFS jest konieczna.

**Częstotliwość odpytywania: 60 s.** Rozważaliśmy 10, 30, 60 i 120 s. Przy 10 s danych byłoby kilka razy więcej przy niewielkim zysku. Przy 120 s ginęłyby przejazdy przez przystanki, bo między przystankami jedzie się 1–2 min, a błąd pomiaru (±60 s) byłby porównywalny z samymi opóźnieniami. Przy 60 s precyzja wynosi ±30 s przy akceptowalnym rozmiarze danych.

**Zakres zapisu.** Nie zapisujemy surowych plików .pb, bo przy 10 s dawałoby to około 2,8 GB na dobę. Zapisujemy wybrane pola do CSV kompresowanego gzipem: pozycje pojazdów co 60 s, z TripUpdates tylko najbliższy przystanek co 60 s, a pełne TripUpdates co 5 min jako punkt odniesienia do porównania naszego modelu z prognozą ZTP. Pomiar (skrypt `scripts/measure_storage.py`, w nocy) dał około 27,5 MB na dobę. Pełne TripUpdates co 5 min to około 1,5 raza więcej niż sam najbliższy przystanek, co uznaliśmy za akceptowalny koszt.

**Licencja.** Ani strona z plikami, ani `feed_info.txt` nie podają licencji. Wydawcą metadanych jest R&G PLUS Sp. z o.o., a bieżący rozkład jest ważny od 2026-09-30 do 2027-01-31. Status licencji ustalamy bezpośrednio z ZTP (zapytanie mailowe).

## Krok 2. Repozytorium (2026-10-03)

**Repozytorium.** Kod jest w repozytorium `krakow-transit-delays` na GitHubie, na razie prywatnym. Upublicznimy je albo udostępnimy prowadzącemu przed obroną.

**Co nie trafia do repo.** `.gitignore` wyklucza dane (`data/`, `*.pb`, `*.zip`, `*.csv.gz`, `*.parquet`), środowisko wirtualne i sekrety (`.env`, klucze, konfigurację rclone). Dane są za duże na gita i odtwarzalne z loggera, a sekret raz wypchnięty do repozytorium trzeba uznać za ujawniony.

**Końce linii.** `.gitattributes` wymusza linuksowe końce linii (LF), bo skrypty i wpisy crona działają na serwerze z Linuksem, gdzie windowsowe CRLF psują skrypty powłoki. Alternatywą było poleganie na ustawieniach edytora, ale reguła w repozytorium działa niezależnie od komputera i edytora.

**Commity (zasada).** Każdy commit to jedna logiczna zmiana. Opisy mają temat w trybie rozkazującym (do ~50 znaków) i treść wyjaśniającą, dlaczego wprowadzono zmianę.

## Krok 3. Środowisko (2026-10-03)

**Narzędzie: uv zamiast venv + pip.** uv jednym narzędziem instaluje Pythona 3.12 (bez ingerencji w condę ani w systemowego Pythona), tworzy środowisko wirtualne i zapisuje zależności w `pyproject.toml`. Najważniejszy argument to odtwarzalność: plik `uv.lock` zapisuje dokładne wersje wszystkich bibliotek, łącznie z zależnościami pośrednimi, więc środowisko da się odtworzyć identycznie za kilka miesięcy albo na innym komputerze. Klasyczny venv + `requirements.txt` daje to tylko przy ręcznym pilnowaniu wersji.

**Podział zależności.** Biblioteki główne (`requests`, `gtfs-realtime-bindings`) są potrzebne loggerowi i trafią na serwer. `pandas` i `pyarrow` są w osobnej grupie `analysis`, instalowanej tylko na laptopie. Na serwerze z 256 MB RAM sam import pandas zająłby znaczną część pamięci, a do zbierania danych nie jest potrzebny.

**Wersja Pythona: 3.12.** Wybraliśmy dojrzałą wersję, dla której wszystkie biblioteki mają gotowe paczki binarne. Wersja jest przypięta w pliku `.python-version`.
