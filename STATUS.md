# Status: Etap 4 — Widok zbiorczy usługi (najważniejszy ekran)

## Co zrobiłem
- Zbudowałem **dedykowany widok zbiorczy usługi** pod adresem `/business-services/{id}` — to najważniejszy ekran całego modułu
- Strona pobiera komplet danych jednym zapytaniem (endpoint `overview` z Etapu 2)
- Świadomie zrobiłem go jako osobną stronę — dzięki temu **omija** błąd generycznej strony szczegółów z Etapu 3
- Zawiera wszystkie **7 sekcji** zgodnie ze specyfikacją:
  1. Domena (ścieżka u góry)
  2. Parametry usługi (krytyczność, RTO, RPO, MTPD, właściciel)
  3. Wpływ na domenę (renderowany markdown)
  4. Zasoby wykorzystywane (tabela: zasób, typ zależności, wpływ, procedury odtworzeniowe)
  5. Plan ciągłości (scenariusz, strategia, kroki — wszystko jako renderowany markdown)
  6. Historia testów (tabela od najnowszego: data, typ, wynik z kolorową ikoną, ustalenia)
  7. Przyciski akcji (Edytuj usługę / Dodaj plan / Dodaj test)

## Jak to sprawdzić (klikalnie)
1. Wejdź na **http://localhost:5173** (uwaga: teraz port 5173, nie 8443 — interfejs chodzi w trybie dev)
2. Zaloguj się: `admin@admin.com` / `admin1234`
3. W menu po lewej kliknij **"Business Continuity"** → **"Business services"**
4. Lista będzie pusta (dane testowe sprzątnąłem) — **pełne dane demo utworzę w Etapie 5**
5. Aby zobaczyć widok zbiorczy już teraz: dodaj usługę przyciskiem **+** na liście, potem kliknij w nią

Sprawdziłem to programowo na danych testowych: wszystkie 7 sekcji renderuje się poprawnie, markdown (nagłówki, pogrubienia, listy) zamienia się na ładny tekst, ikony wyników testów są kolorowe (zielony=sukces, żółty=częściowy, czerwony=porażka).

## Co działa
- Widok zbiorczy `/business-services/{id}` — wszystkie 7 sekcji, z markdownem i kolorami
- Listy 5 encji, dodawanie rekordów, menu "Business Continuity"
- Logowanie

## Co nie działa lub świadomie pominąłem
- **Generyczna strona szczegółów** pojedynczych pod-encji (plan/test/procedura) nadal zwraca 500 — znany problem z Etapu 3, do diagnozy później. Nie dotyka głównego widoku zbiorczego (zrobiony osobno).
- Przycisk "Edytuj usługę" prowadzi do generycznego formularza edycji — może wymagać tej samej naprawy później.
- Dane demo — to Etap 5.

## Co dalej
Etap 5 — skrypt tworzący realistyczne dane demo (2 usługi, zasoby, plany, testy, procedury), żebyś zobaczył moduł "z życia". Napisz **"dalej"**.
