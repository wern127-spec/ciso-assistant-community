# Status: Etap 5 — Dane demo (moduł „z życia")

## Co zrobiłem
- Po drodze **naprawiłem logowanie**: w trybie roboczym (zwykłe `http://localhost`) przeglądarka odrzucała przepustkę z flagą „tylko HTTPS". Teraz ta flaga jest wyłączona **wyłącznie na Twoim komputerze w trybie roboczym** — w prawdziwym wdrożeniu (HTTPS) działa jak dawniej. Logowanie przetestowane: przechodzi.
- Napisałem skrypt tworzący **realistyczne dane demo** (wzorowany na oryginalnych komendach CISO `populate_*`).
- Wszystkie dane demo siedzą w osobnej domenie **„BC Demo - IT Operations"** — łatwo je w razie czego usunąć, nie mieszają się z resztą.
- Skrypt jest **bezpieczny do wielokrotnego uruchomienia** — przy ponownym starcie sam czyści poprzednie dane demo i tworzy świeże.

## Co utworzyłem (dane demo)
- **2 usługi biznesowe:**
  - *Service Desk* (krytyczność High, RTO 4h) — 3 zasoby, 3 procedury, 1 plan, 3 testy
  - *Email Service* (krytyczność Critical, RTO 2h) — 2 zasoby, 2 procedury, 1 plan, 2 testy
- Razem: 5 zasobów, 5 procedur odtworzeniowych, 2 plany ciągłości, 5 testów (różne wyniki: sukces / częściowy / porażka — żeby było widać kolorowe ikony).
- Opisy wpływu, scenariusze i kroki napisane w czytelnym formacie (nagłówki, listy, pogrubienia) — ładnie renderują się w widoku zbiorczym.

## Jak to sprawdzić (klikalnie)
1. Wejdź na **http://localhost:5173**
2. Zaloguj się: `admin@admin.com` / `admin1234` (logowanie już działa)
3. Menu po lewej: **„Business Continuity"** → **„Business services"**
4. Zobaczysz **2 usługi**. Kliknij w którąkolwiek (np. *Service Desk*)
5. Otworzy się **widok zbiorczy** — wszystkie 7 sekcji wypełnionych prawdziwymi danymi

Sprawdziłem to automatycznie przez API z prawdziwym logowaniem: usługa zwraca komplet — domenę, parametry, 3 zasoby z typami zależności i procedurami, zatwierdzony plan, 3 testy uporządkowane od najnowszego.

## Co działa
- Logowanie (naprawione)
- Dane demo — 2 pełne usługi z wszystkim
- Widok zbiorczy `/business-services/{id}` — komplet danych, markdown, kolorowe ikony wyników
- Listy 5 encji, dodawanie rekordów, menu „Business Continuity"

## Co nie działa lub świadomie pominąłem
- **Generyczna strona szczegółów** pojedynczych pod-encji (plan/test/procedura) nadal zwraca 500 — znany problem z Etapu 3. Nie dotyka głównego widoku zbiorczego. Do diagnozy w Etapie 6.
- Przycisk „Edytuj usługę" prowadzi do generycznego formularza — może wymagać tej samej naprawy.

## Co dalej
Etap 6 — szlif: przejrzenie etykiet po angielsku, sprawdzenie błędów w konsoli, krótka dokumentacja modułu, próba domknięcia problemu generycznej strony szczegółów, finalny raport. Napisz **„dalej"**.
