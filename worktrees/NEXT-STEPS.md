# Plan dalszych prac — 2026-09-07

## Stan publikacji

Przejrzano 40 podstawowych checkoutów w workspace Maskservice (bez kopii
zapasowej `c2004-git-backup`); odświeżono 37 originów GitHub. Repozytorium
`redeploy` ma dodatkowy remote `github`, mimo że origin wskazuje serwer LAN.
Ten audyt nie jest pełnym spisem wszystkich repozytoriów organizacji ani
wszystkich zależności na komputerze.

Opublikowane zmiany:

| Repozytorium | Commit | Weryfikacja |
|---|---|---|
| autogrammar/oqlts (przekierowanie z oqlos/oqlts) | `99747f5` | 168 testów, 47 pominiętych testów zależnych od środowiska; build |
| oqlos/connect-scenario | `5f0fc33` | 197 testów frontendowych, 8 testów przeglądarkowych z mockami, build |
| maskservice/stacknet | `d2799c6` | 3 testy ADC i 48 subtestów; bez nowego flashowania i walidacji sprzętu |
| maskservice/redeploy | `b4e388f` | 2 testy instalatora ze stubami usług; składnia Bash |
| maskservice/c2004 | `885108c59` | integracja opublikowanych submodułów, hooki repozytorium |

Publikacja kodu nie potwierdza wdrożenia na DisplayNet ani zgodności danych.

## P0 — odblokować CI redeploy

Skonfigurować `DEPLOYMENT_DEPENDENCIES_READ_TOKEN` z prawem Contents read
wyłącznie do prywatnych repozytoriów maskservice/update i maskservice/c2004.
Następnie ponowić workflow i uzyskać sukces wszystkich 90 testów na runnerze.
Kontrola polityki już przechodzi; lokalny sukces testów nie zamyka tej blokady.
Nie kopiować szerokiego osobistego tokena agenta do repozytorium.

## P0 — dokończyć publikację istniejących prac

1. **Update: uporządkować podstawy i zakresy ticketów.** Aktualny gate
   ticket-063 zgłasza GOV-BASE-002, GOV-BUDGET-001, GOV-SCOPE-001,
   GOV-WORKSTREAM-003 oraz problem własności komponentów; analizuje także
   wcześniejszy ticket-068. Zweryfikować rzeczywiste merge i terminalne
   receipts, odświeżyć bazę i rozdzielić zakresy zgodnie z intentami.
   Ticket-064 zgłasza GOV-TICKET-005: diff nie wskazuje jednego aktywnego
   ticketu. Naprawić powiązanie z aktywnym ticketem przed commitem.
2. **Update: sprawdzić niezapisane tickety 070 i 071.** Gate bez staged diff
   zwrócił PASS, co nie dowodzi gotowości nieśledzonych plików do publikacji.
   Sprawdzić status, lease, pełny diff i testy, przygotować dokładny indeks,
   uruchomić gate ponownie, następnie PR i chroniony Validator.
3. **Update: uzgodnić pozostałe dane robocze.** Worktree 060, 067 i 069
   zawierają zmiany opisów/intentów, a primary zmiany indeksu TICKETS.
   Po sprawdzeniu merge zachować je jako lokalne dowody albo dołączyć do
   odpowiadającej im zmiany materialnej. Nie tworzyć commitów samych nośników
   planowania, których zabrania polityka tego repozytorium.
4. **Legacy i repozytoria LAN.** `maskservice.local/c10/all` i
   `maskservice.local/2025.06` mają lokalne commity i originy poza GitHub.
   Ustalić istniejące docelowe repozytorium GitHub przed migracją historii.
   `c20` zawiera osobne czyste repo `c20frame` oraz obrazy systemu około
   582 MiB i 156 MiB: ustalić magazyn artefaktów i ewentualny submodule,
   nie commitować obrazu dysku jako zwykłego pliku źródłowego.

Warunek zakończenia: każdy materialny diff ma opublikowany commit/PR oraz
wynik właściwej walidacji; pozostałe dane mają jawną klasyfikację i zachowaną
kopię. Bez force-push, obchodzenia gate i automatycznego usuwania worktree.

## P1 — domknąć wymuszanie standardów

1. Spis API GitHuba wykazał 21 repozytoriów organizacji. Dodano ochronę
   historii dla redeploy, archive, i2c-pwm-mosfet-driver i recovery-images.
   Redeploy otrzymał też lokalne hooki, ignore i CI. Pozostaje audyt
   wszystkich remote zależności oraz adopcja standardów w trzech pozostałych
   repozytoriach, których nie ma w podstawowym lokalnym workspace. Aktualny
   odczyt całej organizacji: ochrona historii 21/21, wymagane CI 6/21.
2. Dla 12 repozytoriów z kontrolą polityki (w tym redeploy), lecz bez wymaganych checków,
   przygotować zgodny z trybem publikacji profil Validatora i wymagane CI.
   C2004 i core mają main-only: rozwiązanie musi walidować zmianę przed
   publikacją bez naruszania tego trybu. Nie dodawać wymagania, którego
   spełnienie jest możliwe dopiero po zablokowanym pushu.
3. Przetestować negatywnie obejścia: brak hooka, pominięty hook, usunięty
   workflow, błędne ignore, prywatny plik usunięty w późniejszym commicie.
   Osobno dowieść działania blokady na serwerze.
4. Uaktualnić starsze adopcje Wellmanifest (wcześniejszy audyt: 13 starszych
   pakietów oraz 34 checkouty workspace bez pełnego pinu), zachowując
   właściciela oficjalnych hooków. Zweryfikować kontrakt dla wszystkich
   wspieranych hostów agentów, a nie tylko treść AGENTS.md.
5. Przejrzeć rzeczywiste użycia /tmp w skryptach wdrożeniowych i usługach;
   przenieść dane robocze do właściwego repozytorium lub trwałego katalogu
   właściciela runtime. Nie usuwać cudzych istniejących danych.

Warunek zakończenia: aktualny raport podaje zakres, wersję standardu, aktywny
hook, potwierdzony negatywny test, wymagany check i wynik dla konkretnego SHA.

## P1 — usunąć regresję UI i rozjazd wdrożenia

1. Odtworzyć dwie kolumny `role-address-menu` w źródłowym repo `update`,
   uzgadniając zachowaną poprawkę z aktualnym kodem. Poprzednia diagnoza:
   poprawka była wdrożona bez integracji z main i została nadpisana.
2. Dodać test regresji układu dla wymaganych rozmiarów ekranu; opublikować
   przez ticket/Validator przed wdrożeniem.
3. Porównać localhost:8100 i DisplayNet 192.168.188.118: SHA źródeł,
   artefakty frontendu, konfigurację oraz wersje/sumy danych scenariuszy.
   Jawnie ustalić źródło danych przy konfliktach i zachować odwracalną kopię.
4. Wdrożyć opublikowane artefakty; potwierdzić dwie kolumny w przeglądarce,
   zgodność danych i trwałość nakładki aktualizacji po ponownym sync.

Warunek zakończenia: zapisane SHA wdrożenia, porównanie danych oraz test UI
na docelowym urządzeniu; sam udany push nie zamyka tego zadania.

## P2 — pozostałe usterki wykonania i usług

- Zdiagnozować awarie usług Subactor uruchamianych timerami na podstawie
  bieżących logów; nie klasyfikować ich jako legacy wyłącznie po awarii.
- Zweryfikować przepływ pompy z rzeczywistymi bindingami, kalibracją i
  obsługą kierunku. Testy mocków nie potwierdzają działania sprzętu;
  ujemny przepływ DRI0050 nadal wymaga poprawnego kontraktu kierunku.
- Przygotować niezależny test regresji produktu dla każdego repozytorium;
  kontrola katalogów i ignore nie zastępuje testów zachowania aplikacji.
