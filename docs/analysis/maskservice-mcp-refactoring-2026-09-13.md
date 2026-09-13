---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "maskservice-mcp-refactoring-2026-09-13",
  "kind": "analysis",
  "version": 6,
  "title": "Dostępność MCP i refaktoryzacja Maskservice",
  "status": "accepted",
  "owner": "maskservice/.github",
  "created": "2026-09-13",
  "updated": "2026-09-13",
  "review_after": "2026-09-20",
  "source_revision": "f76b9f16df8400accffb4fa52692ba5c47606c23",
  "affected_repositories": ["maskservice/.github", "maskservice/update", "maskservice/redeploy", "maskservice/stacknet", "maskservice/c2004", "maskservice/maskauth"],
  "evidence": ["repo://maskservice/.github/mcp/smoke.py", "repo://maskservice/.github/mcp/test_contracts.py", "repo://maskservice/.github/worktrees/standards.py"]
}
---

# MCP i refaktoryzacja Maskservice

<!-- docs:section question -->
## Pytanie

Czy dostępne narzędzia Semcod i Autogrammar rzeczywiście pomagają w refaktoryzacji,
i jakie przeszkody ujawnia publikacja lokalnych zmian?

<!-- docs:section scope -->
## Zakres

Lokalne repozytoria Maskservice oraz skonfigurowane serwery MCP. Wynik dotyczy
wywołanych narzędzi, nie wszystkich funkcji każdej biblioteki. Nie wykonano
wygenerowanych poleceń NLP, operacji sprzętowych ani wysyłania wiadomości.

<!-- docs:section method -->
## Metoda

Rzeczywiste wywołania MCP, następnie nowe procesy stdio z poprawionym profilem.
Testy pozytywne i negatywne, kontrola granic katalogów, odczyt implementacji,
testy projektów i obserwacja wyników CI dla konkretnych SHA. Surowe wyniki są
w prywatnych lokalnych receipts; instrukcja odtworzenia jest w `mcp/README.md`.

<!-- docs:section evidence -->
## Dowody

| Narzędzie | Obserwacja i wynik |
| --- | --- |
| Code2LLM, Code2Logic | Początkowo odmawiały dostępu do Maskservice z powodu niewłaściwego root. Po profilu projektowym analizują źródła i nadal odrzucają katalog nadrzędny. |
| NLP2CMD | Uszkodzone importy intent/planner/pact naprawiono w środowisku. Nowy proces zwraca IR i plan dla `list files`, confidence 0.95. Stary proces wymaga przeładowania. |
| NLP2DSL | Backend i worker działały; NLP nie działało. Poprawiono port 8002→8012 i lokalny obraz z brakującymi env2llm/dsl-contracts/dsl-validate. Trzy healthchecks przechodzą; pusty workflow jest odrzucany. Tryb regułowy, bez LLM. |
| reDUP | Skan źródeł działa. Kontrolny duplikat daje jedną grupę exact z dwoma wystąpieniami; kwalifikacja review respektuje granice komponentów. Brak opcjonalnego runtime embeddingów. |
| Intract | Poprawny kontrakt przechodzi; `forbid:network` z `requests.get` daje violation. Skan bez dowodów dopasowania nie dowodzi pokrycia wymagań. |
| SUMD | SUMD Viewera jest poprawny. Niepoprawny dokument daje cztery błędy mimo MCP `isError: false`. |
| VALLM | Niepoprawny Python daje SyntaxError i verdict fail mimo transportowego success. |
| Pfix / Iterun | Diagnostyka środowiska i katalog interfejsów dostępne; nie badano całej funkcjonalności wykonawczej. |

<!-- docs:section facts -->
## Ustalenia

Code2LLM wskazał `standards.observe()` o złożoności cyklomatycznej 35. Oddzielono
odczyt pinów i obserwację mechanizmów aktualizacji: złożoność koordynatora wynosi
5, dwóch funkcji pomocniczych po 16. Wszystkie 97 testów narzędzi worktree
przechodzi; cztery testy adaptera MCP kontrolują fałszywe sukcesy i serializację.

Zmiany standardów `.github` i `c2004` opublikowano na main. Aktualizacje
new-project 0.20.26 wypchnięto w PR-ach boardnet-digital-twin #3, displaynet #2,
maskservice-digital-twin-lab #2 i stacknet-digital-twin #3. OneDev wykonuje lokalne
bramki; GitHub Actions nie uruchamia zadań z powodu rozliczeń konta. Niezależny
Validator dla boardnet #3 odmówił scalenia, ponieważ chronione wymagania nadal
obejmują niezaliczone kontrole hostowane. Nie zmieniono tych wymagań.

`stacknet` opublikowano po 105 testach (`ef4a9bd68d3b`), `redeploy` po 24 testach (`548065bf085e`). Poprawkę odświeżania discovery opublikowano w submodule connect-scenario (`1934753`, 15 testów), a jego pin i port maskauth w C2004 (`16386c849e8f`). Hooki regix/redup oraz kontrola 28 dokumentów i 61 strumieni/201 zdarzeń C2004 przeszły; wup nie raportuje problemów. Szeroki test
redeploy/update początkowo miał 916 sukcesów i siedem błędów: niezgodny bundle,
kontrakt montowania katalogu oraz pięć braków przeglądarki. Istniejące zadanie
update ticket-087 odświeża bundle do pinu C2004 i poprawia przenośność testu
zewnętrznego redeploy; 19 testów kontraktowych/przeglądarkowych przechodzi przy
użyciu dostępnego Chrome. Zmiany wypchnięto i ponownie otwarto PR #136. Validator odrzucił pomijanie testu nieobecnego checkoutu; zastąpiono je wymaganiem rzeczywistej zależności. Sześć testów public-key przechodzi. OneDev zaliczył trzy bramki dla `fd9fc9289f95`; niezależny Validator zatwierdził i scalił PR #136 do main `18cf0d4e8aa9`. Po doprecyzowaniu właściciela testu i jawnym oznaczeniu fikcyjnego tokena pełna bramka governance dla opublikowanej różnicy przechodzi.


Dodatkowo usunięto błąd importu w lokalnym środowisku Validatora: odizolowany runtime z deklarowanych zależności używa LiteLLM 1.100.1, OpenAI 2.54.0 i przypiętego SubLLM 1.10.2. Z tym środowiskiem wykonano rzeczywiste review i scalenie #136. Współdzielonego środowiska ani chronionego profilu publikacji nie zmieniano.

Audyt alertów C2004 wskazał Tornado 6.5.8, Mistune 3.3.3 i Vitest 4.1.11 jako wersje naprawcze. Aktualizację OQLTS opublikowano w `autogrammar/oqlts` (`afd1006`): build, kontrola typów i 186 testów przechodzą, 47 wcześniej oznaczonych testów pozostaje skipped. Stare lokalne wyniki kompilacji zawierały osierocone testy; zarchiwizowano je i wykonano czysty build. Powiązane aktualizacje manifestów C2004 i uv.lock opublikowano na main w `f8ea71f87` po zaliczeniu hooków regix/reDUP, kontroli standardów i 25 testów adopcji.

Pełny frontend na Vitest 4.1.11: 2865 testów przechodzi, 13 błędów w czterech plikach. Powtórzenie dokładnie tych czterech plików na odizolowanym Vitest 4.1.7 odtwarza wszystkie 13 błędów (21 sukcesów). Dotyczą starych oczekiwań localStorage, zapamiętanych celów sprzętu i etykiet/wyboru banku wyjść. Nie przywracano zabronionej persystencji w przeglądarce ani nie pomijano tych testów. Pakiety operational-oql (23 testy), frontend-services (25) i logger (6) przechodzą; drzewo zależności Vitest/UI/coverage jest spójne na 4.1.11. Po przeliczeniu zależności GitHub potwierdził status `fixed` dla wszystkich pięciu alertów Dependabot (#212–#216).


Kontynuacja przez USB: Stacknet `10:51:DB:41:2F:64` miał aplikację 1.12.0 z commita `ff1ecea37c641eb4a6c78df0e72f8bad7c9ac4e8`. Sama zmiana polityki MaskAuth nie wymaga firmware, lecz osobna poprawka autoryzacji DRI0050 z `ef4a9bd68d3b2e4239b0ed62862a35cd14d1eef3` wymagała wgrania. Zbudowano ten czysty commit z profilem `cores3se-usb-module-motors`; 105 testów i 80 podtestów przeszło. Przed zapisem odczytano pełne 16 MiB flash do prywatnej kopii (SHA-256 `29b340b9e27830a5a64a8c6efcd8c1739a2cf2e3c9a9981c65ebc2e75817beec`). Obraz aplikacji ma SHA-256 `bb818cb21b808cd7ebd4f2b413b8c244566f2db9701aad94ad670450e6cbb8a9`. Układ partycji jest identyczny; zakres zapisu nie obejmował NVS.

Esptool zweryfikował hash zapisanych segmentów. Standardowy reset USB pozostawiał układ w DOWNLOAD; obsługiwany przez zainstalowany esptool reset watchdogiem uruchomił aplikację. Rozpoznanie trybu startu opisuje [dokumentacja Espressif](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html). Po kolejnym starcie i potwierdzeniu przez użytkownika podłączenia całego zestawu, rzeczywiste OQL API zgłosiło `healthy: true`, ten sam commit, 16 wyjść, oba M122 (`0x45`, `0x66`) z zerem błędów odczytu, zgodny kontrakt oraz brak brakujących wymaganych peryferiów. LAN: `192.168.188.224`, Wi-Fi: `192.168.188.163`. To dowód działania aplikacji i odczytów; nie wykonano poleceń wyjść ani silników.

Przeładowano tylko kontener `c2004-maskauth-1`, aby zastosować wersjonowaną politykę. Rzeczywiste żądania usługi Displaynet zwracają 200 dla OUT1, OUT16 i dwóch operacji banku oraz 403 dla BoardNet i niepasującej pary capability/resource. Tokeny nie zostały opublikowane ani wysłane do sprzętu. Fingerprint klucza publicznego MaskAuth zgadza się z kluczem raportowanym przez Stacknet; gotowość podpisywania ES256 jest potwierdzona.

Próba kontynuacji naprawy źródłowego new-project potwierdziła brak nowszego źródła niż `8d86cd6`. Kontrola dla konkretnych plików dopuszczała nowy zakres, ale oficjalny allocator, badający cały zakres `**`, odmówił rezerwacji ticketu (`GOV-WORK-START-001`) z powodu istniejących pending/unassigned branches i checkoutów. Nie użyto force-new, nie zmieniano obcych plików ani zarządzanych kopii adopterów. Błąd helpera i ta przeszkoda wymagają kontynuacji w poprawnie przydzielonym zakresie źródłowego standardu.

<!-- docs:section hypotheses -->
## Hipotezy

Naprawy obrazu NLP powinny trafić do źródłowego Dockerfile NLP2DSL; obecny adapter
wdrożenia pozwala używać MCP, ale nie stanowi wydania poprawionego upstreamu.
Heurystyczne sugestie refaktoryzacji wymagają sprawdzenia zachowania testami. NLP2CMD dla bogatszego zapytania `Find Python files` zwrócił niską pewność 0.148 i plan z wildcardem `*`, bez zawężenia do `.py`; prosty test dostępności nie dowodzi poprawności dowolnego polecenia naturalnego.

<!-- docs:section limitations -->
## Ograniczenia

Aktualizację standardów update ticket-090 odtworzono z zabezpieczonego patcha po scaleniu ticket-087. Commit `990945ce0c57` w PR #138 przechodzi pełną bramkę governance, integralność 11 artefaktów i 19 testów; OneDev zaliczył trzy bramki, lecz Validator zablokował scalenie (`SEMANTIC_REVIEW_UNRESOLVED`). Chronionego review nie zastępuje
samo zaliczenie testów lokalnych. Użytkownik potwierdził rozszerzenie uprawnień maskauth; zmianę opublikowano w `10e535be0c40`. Rozdzielono zasoby pojedynczego wyjścia/dzierżawy i banku wyjść; sześć testów sprawdza dozwolone operacje oraz odmowę dla innych węzłów i niepasujących par capability/resource.
Same indeksy ticketów Displaynet/laboratorium nie zostały opublikowane: pre-commit odrzuca tracking-only changes (GOV-AGENT-HOST-007); zachowano lokalne pliki. Surowe mapy środowiska, logi planfile i lokalne obrazy dysków nie są dowodem
gotowości do publikacji kodu. Checkout c20 wskazuje repozytorium zlecenia/c20,
a jego nieśledzone obrazy dysków przekraczają zwykły limit pliku GitHub.

Próba dodatkowego checkera wellmanifest/docs ujawniła brak formalnej adopcji tego pakietu w `.github` i różnicę własności raportu: sprawdzony wtedy profil 0.1.1 wymagał `subactor/docs` jako domu raportów przekrojowych. Nowszy zaobserwowany main docs 0.2.0 wskazuje `maskservice/report`; takiego repo nie znaleziono w dostępnym katalogu organizacji. Utworzenie i migracja wymagają ustalenia widoczności oraz adopcji/chronionej publikacji tego domu raportów. Poprawiono zgodność nazw plików z ID. Dokumentacja pozostaje raportem organizacji Maskservice; nie deklarujemy pełnej zgodności z tym profilem ani nie zmieniamy jego reguł. C2004 ma odrębną, zweryfikowaną adopcję docs. Uzupełniono ją do polityki 0.2.0 z main `4bd5096e59a4a4b2022949b1a49cba2eb94ed424` (ostatni formalny Release nadal v0.1.0). Preflight miejsca dokumentu, 25 testów adopcji, kontrola 28 dokumentów i hooki przeszły; publikacja C2004: `46cff7ba5`.


Validator przeanalizował wszystkie 23 części diffu PR #138 i wskazał błąd w źródłowym pakiecie new-project 0.20.26, w `.governance/precommit_standard_update.py`. `_staleness_only` sprawdza obecność ogólnego tekstu `GOV-STANDARD-UPDATE-001`, a nie jednoznaczny typ odmowy. Przy poprawnych staged digests także kontrolny komunikat o odmowie autoryzacji, niezwiązanej z nieaktualnym pinem, dał `True`. Próba tylko wywołała predykat z syntetycznym `CompletedProcess`; nie uruchomiła Goal ani nie wykonała commita przez ten helper. Zarządzany plik pozostawiono zgodny z oficjalnym SHA. Scalenie wymaga poprawionego źródła standardu i ponownej niezależnej oceny; testy i integralność same w sobie nie rozstrzygają tego błędu.

<!-- docs:section recommendations -->
## Dalsze prace

Przywrócić dostępne rozliczenie CI lub uzyskać niezależnie zatwierdzoną zmianę
chronionego profilu publikacji. Naprawić źródłowy standard new-project i ponownie przeprowadzić chronioną publikację ticket-090 w PR #138.
Przeładować klienta MCP, aby użył poprawionego profilu. Dalsze refaktoryzacje
wybierać z konkretnych kontraktów i pomiarów; nie aktualizować mechanicznie
niezaadoptowanych szkiców standardów ani nie utożsamiać harmonogramu z wykonanym CI.
