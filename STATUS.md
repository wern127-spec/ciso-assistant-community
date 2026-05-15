# Status: Etap 2 — API (DRF)

## Co zrobiłem
- Dodałem API (interfejs programistyczny) dla wszystkich 5 tabel — można teraz odczytywać i zapisywać dane przez sieć
- Każda tabela ma komplet operacji: lista, podgląd, tworzenie, edycja, usuwanie
- Zbudowałem **specjalny endpoint zbiorczy** `overview` — zwraca w jednym zapytaniu wszystko o usłudze: jej domenę, zasoby z opisem wpływu, RTO/RPO, plany ciągłości i historię testów (posortowaną od najnowszego). To on zasili główny widok w Etapie 4.
- Dodałem endpointy pomocnicze z listami wartości (np. poziomy krytyczności, typy testów) — przydadzą się przy formularzach
- Uprawnienia działają zgodnie z mechanizmem CISO Assistant (RBAC per domena)
- Napisałem 4 testy API (dostępność endpointów, tworzenie usługi, listy wartości, endpoint zbiorczy) — **wszystkie przeszły**

## Jak to sprawdzić (klikalnie)
1. Wejdź na **https://localhost:8443/api/schema/swagger/**
   - (jeśli przeglądarka ostrzega o certyfikacie → "Zaawansowane" → "Przejdź mimo to")
2. To jest interaktywna dokumentacja API. Użyj **Ctrl+F** i wpisz `business-continuity`
3. Powinieneś zobaczyć **5 nowych grup endpointów**:
   - `business-continuity/business-services`
   - `business-continuity/service-asset-links`
   - `business-continuity/continuity-plans`
   - `business-continuity/continuity-plan-tests`
   - `business-continuity/asset-recovery-procedures`
4. Rozwiń `business-services` — zobaczysz m.in. operację **`overview`** (endpoint zbiorczy)

Alternatywnie Redoc (ładniejszy podgląd): **https://localhost:8443/api/schema/redoc/**

## Co działa
- 5 kompletów endpointów CRUD + endpoint zbiorczy `overview`
- Endpointy są widoczne w oficjalnym schemacie API (Swagger/Redoc)
- Zabezpieczenie działa: bez logowania endpoint zwraca 401 (odmowa), nie 404 — czyli istnieje i jest chroniony
- 9/9 testów zielonych łącznie (5 z Etapu 1 + 4 nowe API)

## Co nie działa lub świadomie pominąłem
- **Frontend (interfejs graficzny) nadal nie wstaje** — build pada na braku pamięci Dockera. Etap 2 jest backendowy, więc to nie przeszkadza. **Przed Etapem 3 (interfejs) trzeba zwiększyć pamięć Docker Desktop** — przeprowadzę Cię przez to.
- Eksport do Excela / zaawansowane filtry — świadomie pominięte, nie ma ich w MVP
- Pełny interfejs użytkownika — to Etap 3 i 4

## Co dalej
Następny krok: **Etap 3 — Frontend CRUD** (interfejs: listy, formularze, sekcja "Business Continuity" w menu). To wymaga naprawy pamięci Dockera. Napisz **"dalej"** — wtedy najpierw zajmiemy się pamięcią, potem interfejsem.
