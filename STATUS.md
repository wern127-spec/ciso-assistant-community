# Status: Etap 1 — Modele i migracje (backend)

## Co zrobiłem
- Utworzyłem nową część aplikacji "business_continuity" z 5 tabelami danych:
  - **Usługa biznesowa** (BusinessService) — centralna jednostka ciągłości
  - **Powiązanie usługa-zasób** (ServiceAssetLink) — który zasób wspiera którą usługę i jak bardzo jest krytyczny
  - **Plan ciągłości** (ContinuityPlan) — plan przypisany do usługi
  - **Test planu** (ContinuityPlanTest) — historia ćwiczeń/testów planu
  - **Procedura odtworzeniowa zasobu** (AssetRecoveryProcedure) — dokument techniczny per zasób
- Podpiąłem uprawnienia (kto może oglądać/edytować) do wszystkich ról w systemie, zgodnie z mechanizmem CISO Assistant
- Wygenerowałem i zastosowałem migrację bazy danych (tabele utworzone)
- Napisałem 5 testów automatycznych sprawdzających tworzenie obiektów i powiązania między nimi — **wszystkie 5 przeszło pomyślnie**

## Jak to sprawdzić (klikalnie)
**Nie zobaczysz nic w przeglądarce — to fundament (warstwa bazy danych).** Etap 1 jest niewidoczny w UI z założenia. Interfejs powstaje w Etapie 3 i 4.

To, co potwierdza że działa:
- Migracja `business_continuity.0001_initial` zastosowana OK (widoczne w logach startu)
- Backend uruchamia się bez błędów
- Testy automatyczne: 5/5 zielonych

## Co działa
- 5 tabel utworzonych w bazie z poprawnymi relacjami
- Usługa może mieć wiele zasobów (i odwrotnie — zasób może być w wielu usługach)
- Plan należy do usługi, test należy do planu, procedura należy do zasobu
- Backend działa na obrazie budowanym z naszego kodu (docker-compose-build.yml)

## Co nie działa lub świadomie pominąłem
- **Frontend (interfejs) tymczasowo nie wstaje** — budowanie frontendu przerywa się na braku pamięci Dockera ("cannot allocate memory"). To NIE blokuje Etapu 1 (backendowy). Naprawię to przed Etapem 3 (interfejs) — najpewniej trzeba zwiększyć limit pamięci w Docker Desktop. Zanotowane do rozwiązania.
- API (endpointy) — świadomie pominięte, to Etap 2
- Interfejs użytkownika — świadomie pominięty, to Etap 3 i 4

## Co dalej
Następny krok: Etap 2 — API (endpointy, żeby dało się te dane czytać/zapisywać programowo). Napisz **"dalej"** żeby kontynuować.
