---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "maskfleet-release-parity-2026-09-13",
  "kind": "analysis",
  "version": 1,
  "title": "Wydania i zgodność runtime Maskfleet oraz Displaynet",
  "status": "accepted",
  "owner": "maskservice/.github",
  "created": "2026-09-13",
  "updated": "2026-09-13",
  "review_after": "2026-09-20",
  "source_revision": "faf3ec2f749be954b51811f50cdb6bd0fc34ecfc",
  "affected_repositories": [
    "maskservice/update",
    "maskservice/displaynet",
    "maskservice/redeploy",
    "maskservice/c2004",
    "maskservice/maskauth",
    "maskservice/stacknet"
  ],
  "evidence": [
    "https://github.com/maskservice/update/pull/139",
    "https://github.com/maskservice/update/pull/140",
    "https://github.com/maskservice/update/pull/141",
    "https://github.com/maskservice/displaynet/pull/3",
    "repo://maskservice/redeploy/scripts/test_parallel_image_build.py"
  ]
}
---

# Wydania i zgodność runtime — 2026-09-13

<!-- docs:section question -->
## Cel

Wykonać bump ostatnio zmienianych projektów, sprawdzić rzeczywisty mechanizm
aktualizacji Maskfleet i porównać Displaynet RPi5 z localhost:8100.

<!-- docs:section scope -->
## Zakres i metoda

Odczyty Git, obrazów Docker/Podman, systemd, API, schematów PostgreSQL,
sprawdzenia TestQL i renderowanie w Chrome przez Playwright. Sprawdzono również
MCP Code2LLM, Code2Logic, NLP2CMD, NLP2DSL i reDUP. Pełne logi, kopie baz i
lokalna konfiguracja operatora pozostały w prywatnych katalogach.

Zaobserwowane adresy DHCP: Displaynet RPi5 `192.168.188.116`, kontroler
`maskfleet5.local` — `192.168.188.249`. Historyczne `.109`, `.108` i `.100`
nie odpowiadały. Nazwy ról na Displaynet zostały uzgodnione przez API Maskfleet;
nie zmieniano konfiguracji interfejsów ani adresów urządzenia.

<!-- docs:section evidence -->
## Wydania

| Repozytorium | Wersja | Publikacja |
|---|---|---|
| c2004 | 1.1.21 | `c3c195821661ee016bac201606a74adf0071da51`, tag `v1.1.21` |
| maskauth | 0.1.1 | `a561a4d`, main |
| stacknet | 1.12.1 | `7208212`, main; wersja firmware w CMakeLists.txt |
| update / Maskfleet | 0.2.1 | PR #139–141 zmergowane; runtime `0bed9bb80bb32fc55dbd7a7d0f45ab3875910d24` |
| displaynet | 0.1.1 | chroniony PR #3; osobna wersja od aplikacji C2004 |
| redeploy | identyfikacja commitem | poprawki pełnej przebudowy i weryfikacji wdrożeń |

## Naprawione przyczyny rozbieżności

- Skrypt bumpa C2004 pomijał root package w `uv.lock`; teraz aktualizuje go
  bez zmiany pinów zależności, z testem regresji.
- Lokalny nginx montował stary `frontend/dist` nad nowym obrazem. Zainstalowano
  sprawdzone artefakty 1.1.21 w tym katalogu; poprzednie pliki zachowano.
- Lokalna baza nie miała `core.alembic_version`. Po prywatnym backupie
  istniejący migrator doprowadził ją do `c52_drop_legacy_dsl_tables`.
  Obsługuje teraz również Docker, obok Podmana.
- Aktywacja Displaynet nie sprawdzała wersji aplikacji ani migracji. PR #139
  dodaje migrację z backupem oraz sprawdzenie wersji frontendu, backendu i
  aktualności schematu przed zmianą `.deploy-commit`.
- Pełna przebudowa odwoływała się do pomocników usuwanych przez rsync.
  Pomocniki są teraz rozwiązywane względem repozytorium, które je posiada.
- Backend szablonów budowano z kontekstem pozbawionym współdzielonych pakietów.
  Używany jest kontekst głównego repozytorium.
- W katalogu CQL `vendor/oqlts` został sam lockfile. Builder odtwarza teraz
  zależność z przypiętego submodułu C2004 przed obliczeniem skrótu i buildem.
- Brak przypiętego SubLLM blokował rollback. Dostarczono commit
  `0a5f2d56e2e2ab4b9fb422a41a44169f29e19b0b` z lokalnego bundle Git.
  Następnie dodano mirror publicznego `subactor/subllm` do konfiguracji
  operatora Maskfleet i trwałe, dokładne przekierowanie jego URL w Git
  Displaynet. Potwierdzono dostęp do przypiętego commita i odczyt przez LAN.
- Sonda Maskfleet sprawdzała nieaktualne adresy mirrorów. Prywatna konfiguracja
  operatora wskazuje bieżący adres; po dodaniu SubLLM dostępnych i zgodnych
  z GitHub jest 10/10. Domyślna konfiguracja repozytorium nadal obejmuje
  dziewięć mirrorów; dziesiąty jest zapisany w profilu operatora.
- Pełny redeploy Maskfleet oczekiwał sztywno ośmiu repozytoriów. Sprawdza teraz
  liczbę z konfiguracji, a wybór kontrolera korzysta z identyfikacji roli.
- Cleanup deweloperskiego wdrożenia wysyłał STOP pompy mimo wyłączonego
  wskaźnika sprzętowego. Wymaga teraz włączenia wskaźnika przez operatora.

## Trwałe ustawienia urządzenia

Displaynet ma drop-in `60-complete-release.conf` dla
`maskservice-auto-update.service`, włączający `DISPLAYNET_REBUILD_IMAGES=1`
i `C2004_SOURCE_HASH_COMPUTE=1`. Obejmuje to również `update.apply` z Maskfleet,
które uruchamia tę usługę. Operatorowa konfiguracja sondy kontrolera znajduje
się w `proxy/storage/auto-update/update-targets.runtime.json`; oddzielny
`operator-compose.yml` zachowuje istniejące mapowanie `db.mask.services`.
Danych uwierzytelniających ani baz operacyjnych nie kopiowano z localhost na RPi5.

<!-- docs:section findings -->
## Bazy nie są identyczne

Obie instalacje mają rewizję `c52_drop_legacy_dsl_tables`, ale różnią się
fizycznymi schematami i rekordami. Lokalnie pozostały historyczne tabele
w `public`; Displaynet używa `core`, `menu` i `devtools`. Sama zgodność numeru
migracji nie potwierdza równoważności wszystkich kolumn ani danych.

| Tabela logiczna | localhost | Displaynet |
|---|---:|---:|
| scenario_library | 15 | 0 |
| test_scenarios | 34 | 1 |
| menu_items | 914 | 43 |
| template_json_data | 5 | 4 |

To obserwacje liczby rekordów, nie dowód, że wszystkie dodatkowe rekordy są
błędne. Nie usuwano historycznych ani użytkowych danych w celu wymuszenia
identyczności. Nazwa `db.mask.services` wskazuje obecnie komputer operatora
`192.168.188.212`. Dostęp SSH nadal zgłasza `connection_refused`: usługa/socket
SSH są nieaktywne. Nie uruchamiano SSH ani nie potwierdzono synchronizacji
baz przez ten kanał. Działające API nie dowodzi działania kanału SSH.

## Walidacja

- C2004: kontrola wersji i Wellmanifest, test regresji lockfile, pełny build
  obrazów, odtworzenie 19 usług aplikacyjnych; PostgreSQL zachował wolumen.
- Aktualizacja Displaynet: 33 testy aktywacji i weryfikatora; niezależny
  Validator zatwierdził i zmergował PR #139.
- Redeploy: 40 testów profilu Displaynet, 17 kontraktów Maskfleet i test
  wykonania równoległego buildera poza katalogiem aplikacji.
- MaskAuth: 6 testów; runtime `/health/live` zgłasza 0.1.1,
  `/health/ready` potwierdza tożsamości maszynowe i podpis ES256.
- Stacknet: testy narzędzi, TypeScript i 29 kontroli backendu; nie wykonywano
  poleceń sterowania wyjściami ani kolejnego flashowania dla samego bumpa.
- MCP: wszystkie pięć serwerów przeszło właściwe dla nich sondy. Pierwsze
  wywołanie Code2LLM z plikiem zamiast katalogu było błędne; po korekcie
  wejścia sonda przeszła. Wyniki analizy są pomocnicze, nie zastępują testów.

<!-- docs:section limitations -->
## Stan końcowy

Displaynet zakończyło pełną aktualizację przez Maskfleet. Checkout, opt runtime
oraz `.deploy-commit` wskazują `c3c195821661ee016bac201606a74adf0071da51`.
Frontend i backend na localhost oraz RPi5 zgłaszają 1.1.21, a obie bazy
mają aktualny schemat `c52_drop_legacy_dsl_tables`. Na Displaynet 11/11 kontenerów
używa obrazów zgodnych z bieżącymi tagami; systemd nie zgłasza błędnych usług.
Maskfleet potwierdza `current` dla update, c2004-displaynet i redeploy-data.

TestQL przeszedł 78/78 sprawdzeń dla obu instalacji. Chrome/Playwright
wyrenderował stronę główną i edytor scenariuszy bez nieobsłużonych błędów JS,
również po aktywacji nowego wydania na RPi5. To smoke funkcjonalności dostępnej
bez sterowania urządzeniami, nie pełny test każdej operacji biznesowej.

Z Displaynet sprawdzono również istniejące poświadczenie usługi MaskAuth:
wydanie tokenu dla `hardware.node.output.set` i `hardware.node.outputs.replace`
na Stacknet zwraca 200; analogiczny zasób Boardnet zwraca 403. Tokenów nie
publikowano ani nie użyto do sterowania wyjściami.

PR #141 został niezależnie zatwierdzony i zmergowany. Maskfleet sam wdrożył
commit `0bed9bb80bb32fc55dbd7a7d0f45ab3875910d24`; `/api/runtime` zgłasza
wersję 0.2.1 i ten sam commit. Test regresji porównuje wersję API z VERSION.
Ostatnia sonda potwierdza dostęp do 10/10 repozytoriów GitHub oraz aktualność
i dostępność 10/10 mirrorów LAN.

Lokalny zestaw usług i profil RPi5 różnią się zakresem oraz architekturą
obrazów (amd64/arm64); nie są to identyczne bajtowo obrazy ani identyczne
bazy. Potwierdzono zgodność wersji aplikacji, stanu migracji i sprawdzonych
ścieżek użytkowych. Firmware Stacknet 1.12.1 opublikowano w źródłach;
urządzenie nie zostało ponownie flashowane w ramach tego wydania.
