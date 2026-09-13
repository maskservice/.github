---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "maskservice-wellmanifest-adoption-2026-09-13",
  "kind": "analysis",
  "version": 3,
  "title": "Adopcja i aktualizacja Wellmanifest w Maskservice",
  "status": "accepted",
  "owner": "maskservice/.github",
  "created": "2026-09-13",
  "updated": "2026-09-13",
  "review_after": "2026-09-20",
  "source_revision": "5606150512999746206c031e31446aaed5a4b35b",
  "affected_repositories": [
    "maskservice/.github",
    "maskservice/01.mask.services",
    "maskservice/1001.mask.services",
    "maskservice/C2003",
    "maskservice/boardnet-digital-twin",
    "maskservice/c20",
    "maskservice/c2002",
    "maskservice/c2004",
    "maskservice/c2004-firmware",
    "maskservice/c201001.mask.services",
    "maskservice/c20frame3",
    "maskservice/c20frame4",
    "maskservice/cm",
    "maskservice/core",
    "maskservice/cpp",
    "maskservice/deploy",
    "maskservice/displaynet",
    "maskservice/firmware",
    "maskservice/fleet",
    "maskservice/maskauth",
    "maskservice/maskservice-digital-twin-lab",
    "maskservice/redeploy",
    "maskservice/rp2040-keyboard",
    "maskservice/stacknet",
    "maskservice/stacknet-digital-twin",
    "maskservice/update",
    "maskservice/viewer",
    "maskservice/wiki",
    "maskservice/workshop"
  ],
  "evidence": [
    "repo://maskservice/.github/worktrees/standards.py",
    "repo://maskservice/.github/docs/analysis/wellmanifest-adoption-2026-09-13.json"
  ]
}
---

# Adopcja Wellmanifest w Maskservice

<!-- docs:section question -->
## Pytanie

Które repozytoria mają wdrożone standardy, czy aktualizują je automatycznie i co wymaga odświeżenia?

<!-- docs:section scope -->
## Zakres

29 bezpośrednich lokalnych checkoutów Git w `maskservice/*`, w tym `.github`. Nie jest to audyt wszystkich repozytoriów konta ani zagnieżdżonych submodułów. 8 repozytoriów ma artefakty lub deklaracje pinów, 10 tylko instrukcje, 11 bez wykrytej adopcji. Deklaracja pinów szkicu nie oznacza implementacji kontraktu.

<!-- docs:section method -->
## Metoda

Odczyt śledzonych plików, locków, hashy zarządzanego pakietu, efektywnego hooka Git i harmonogramów CI. Zdalne wersje sprawdzono przez GitHub API i `git ls-remote`; aktualizacje governance wykonano oficjalnym `goal governance adopt` z pełnym SHA. Harmonogram, hook, integralność i wynik testów są oddzielnymi dowodami.

<!-- docs:section evidence -->
## Dowody

[Pełny inwentarz JSON](wellmanifest-adoption-2026-09-13.json), [audytor](../../worktrees/standards.py), [updater worktrees](../../worktrees/refresh_standard.py).

Opublikowane źródła: [new-project v0.20.26](https://github.com/wellmanifest/new-project/releases/tag/v0.20.26), commit `8d86cd61404d51809532a8292ce9c0cc02ed6157`; [worktrees v0.5.3](https://github.com/wellmanifest/worktrees/releases/tag/v0.5.3), commit `57bcd6b6f5d266fa9952824f1d89d4d45d8a386d`.

<!-- docs:section facts -->
## Ustalenia

| Repozytorium | Poziom adopcji | Standardy |
| --- | --- | --- |
| `.github` | Artefakty / pin | worktrees |
| `01.mask.services` | Nie wykryto | — |
| `1001.mask.services` | Nie wykryto | — |
| `C2003` | Nie wykryto | — |
| `boardnet-digital-twin` | Artefakty / pin | logs, new-project, twin-lifecycle |
| `c20` | Nie wykryto | — |
| `c2002` | Nie wykryto | — |
| `c2004` | Artefakty / pin | docs, git-lifecycle, logs, worktrees |
| `c2004-firmware` | Tylko instrukcje | — |
| `c201001.mask.services` | Nie wykryto | — |
| `c20frame3` | Nie wykryto | — |
| `c20frame4` | Nie wykryto | — |
| `cm` | Nie wykryto | — |
| `core` | Tylko instrukcje | — |
| `cpp` | Nie wykryto | — |
| `deploy` | Tylko instrukcje | — |
| `displaynet` | Artefakty / pin | deployment, logs, new-project |
| `firmware` | Tylko instrukcje | — |
| `fleet` | Tylko instrukcje | — |
| `maskauth` | Tylko instrukcje | — |
| `maskservice-digital-twin-lab` | Artefakty / pin | deployment, logs, new-project, twin-lifecycle |
| `redeploy` | Tylko instrukcje | — |
| `rp2040-keyboard` | Tylko instrukcje | — |
| `stacknet` | Tylko instrukcje | — |
| `stacknet-digital-twin` | Artefakty / pin | logs, new-project, twin-lifecycle |
| `update` | Artefakty / pin | dsl, new-project, poa |
| `viewer` | Artefakty / pin | pcb, sch |
| `wiki` | Nie wykryto | — |
| `workshop` | Tylko instrukcje | — |

Cztery projekty (`boardnet-digital-twin`, `displaynet`, `maskservice-digital-twin-lab`, `stacknet-digital-twin`) miały pakiet 0.20.9, ale dodatkowo deklarowały 0.18.1 w `.wellmanifest/adoption.json`. Odświeżono pakiet i projekcję do 0.20.26, zachowując status szkiców logs/deployment/twin-lifecycle. `update` otrzymał kandydat 0.20.18 → 0.20.26 oraz aktualny DSL z commita `5f40ad5d228d6301bdbf4bb78e1646ebd3c2b95b`; POA nie wymaga zmiany.

W `.github` worktrees zmieniono z 0.5.1 do 0.5.3, a w C2004 z 0.5.2 do 0.5.3. C2004 otrzymał również aktualne piny logs i git-lifecycle; bajty ich używanych kontraktów pozostały takie same. Docs uzupełniono do 0.2.0 z main `4bd5096e59a4a4b2022949b1a49cba2eb94ed424` (C2004 `46cff7ba5`); formalny Release pozostaje v0.1.0. `viewer` przechodzi kontrolę PCB 1.23.0, SCH 1.9.0 i procesu POA; lokalne HEAD PCB/SCH są zgodne ze zdalnym main.

Przed zmianą nie wykryto okresowego odświeżania pakietów. Cztery stare hooki wywoływały kontroler aktualizacji przy commicie, co nie stanowi dowodu automatycznej publikacji. Pakiet 0.20.26 ma lokalną kontrolę integralności bez pobierania w hooku. Dodano tygodniowe kontrole świeżości do pięciu kandydatów governance, C2004 oraz `.github`. Są to kontrole zgłaszające drift, a nie automatyczne scalanie lub wdrażanie. Harmonogram zacznie działać dopiero po publikacji na gałęzi domyślnej.

Walidacja: 97 testów narzędzi organizacji; 30 testów adopcji/logów C2004; po 3 testy twinów i lint; walidacja topologii Displaynet/laboratorium; kontrola standardów `update` oraz 24 testy DSL. Pięć bramek governance przeszło dla lokalnych zmian. Pełna bramka C2004 potwierdziła 28 dokumentów oraz 61 strumieni / 201 zdarzeń logów. Hooki C2004 (w tym regix i redup) przeszły; zmiana została wypchnięta na `main` w commicie `e4410c528`. Zweryfikowano również składnię YAML i shell wszystkich siedmiu nowych workflow.

Stan kandydatów po publikacji:

- `boardnet-digital-twin`: `d101e1a0fb97`, pushed-pr, `ticket-007`.
- `displaynet`: `106f76268728`, pushed-pr, `ticket-006`.
- `maskservice-digital-twin-lab`: `621830250508`, pushed-pr, `ticket-005`.
- `stacknet-digital-twin`: `32e45abbef47`, pushed-pr, `ticket-007`.
- `update`: `990945ce0c57`, [PR #138](https://github.com/maskservice/update/pull/138), `ticket-090`.

<!-- docs:section hypotheses -->
## Hipotezy

Nie przypisano samej obecności plików ani harmonogramu do udanej egzekucji zdalnej. Powód braku kontrolera w starszym `update` nie został ustalony; aktualny pakiet celowo nie pobiera standardu w pre-commit.

<!-- docs:section limitations -->
## Ograniczenia i blokady

Kolizję zakresu `update` rozwiązano przez serializację: niezależny Validator zatwierdził i scalił [PR #136](https://github.com/maskservice/update/pull/136), main `18cf0d4e8aa9`. Odtworzono ticket-090 na tej bazie z zachowaniem nowych właścicieli konfiguracji. Pełna bramka governance, integralność 11 artefaktów i 19 testów kontraktowych/przeglądarkowych przeszły. [PR #138](https://github.com/maskservice/update/pull/138) zaliczył trzy bramki OneDev, lecz niezależny Validator zablokował scalenie: `SEMANTIC_REVIEW_UNRESOLVED`. Kontrolna próba potwierdziła, że upstreamowy `_staleness_only` rozpoznaje ogólną odmowę `GOV-STANDARD-UPDATE-001` jako samą nieaktualność pinu, jeśli staged digests pasują. Naprawa wymaga poprawionego, zatwierdzonego źródła standardu; nie zmieniano ręcznie zarządzanego pliku ani wymagań review. Ten sam pakiet jest kandydatem w czterech pozostałych PR-ach.

Brak finalnych GitHub Releases dla części standardów dziedzinowych nie jest błędem sieci ani dowodem gotowości: piny szkiców pozostają szkicami, a brakujące dokumenty instancji nie zostały wymyślone. Nie potwierdzano ochrony gałęzi ani wykonania nowych workflow na GitHub. Nie wdrażano zmian na urządzeniach.

<!-- docs:section recommendations -->
## Dalsze prace

1. Poprawić rozpoznawanie odmów Goal w źródle new-project, przyjąć zatwierdzoną wersję i ponownie zweryfikować PR #138 oraz pozostałych adopterów.
2. Doprowadzić do chronionego scalenia czterech opublikowanych PR-ów governance. OneDev zaliczył ich lokalne bramki; GitHub Actions blokuje rozliczenie konta. `.github` i C2004 są opublikowane.
3. Dla 10 repozytoriów z samymi instrukcjami zaplanować rzeczywistą adopcję dopasowaną do produktu; nie przedstawiać hostowej polityki worktrees jako pełnego governance.
4. Viewer aktualizować istniejącym `scripts/standard_check.py --sync` po zmianie opublikowanych źródeł; brak automatycznego publikowania jest jawny.

Powtórzenie audytu: `python3 worktrees/standards.py /path/to/maskservice --remote`. Odświeżenie worktrees: `python3 worktrees/refresh_standard.py /path/to/adopter --apply`, następnie testy adoptera. Domyślny tryb updatera nie zapisuje plików.

Aktualny raport narzędzi i publikacji: [MCP i refaktoryzacja](maskservice-mcp-refactoring-2026-09-13.md).
