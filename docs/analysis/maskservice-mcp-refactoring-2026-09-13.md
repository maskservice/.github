---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "maskservice-mcp-refactoring-2026-09-13",
  "kind": "analysis",
  "version": 4,
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
użyciu dostępnego Chrome. Zmiany wypchnięto i ponownie otwarto PR #136. Validator odrzucił pomijanie testu nieobecnego checkoutu; zastąpiono je wymaganiem rzeczywistej zależności. Sześć testów public-key przechodzi, a nowy HEAD ponownie oczekuje na niezależną walidację. Po doprecyzowaniu właściciela testu i jawnym oznaczeniu fikcyjnego tokena pełna bramka governance dla opublikowanej różnicy przechodzi.

<!-- docs:section hypotheses -->
## Hipotezy

Naprawy obrazu NLP powinny trafić do źródłowego Dockerfile NLP2DSL; obecny adapter
wdrożenia pozwala używać MCP, ale nie stanowi wydania poprawionego upstreamu.
Heurystyczne sugestie refaktoryzacji wymagają sprawdzenia zachowania testami. NLP2CMD dla bogatszego zapytania `Find Python files` zwrócił niską pewność 0.148 i plan z wildcardem `*`, bez zawężenia do `.py`; prosty test dostępności nie dowodzi poprawności dowolnego polecenia naturalnego.

<!-- docs:section limitations -->
## Ograniczenia

Aktualizacja standardów update ticket-090 jest wykonywana kolejno po integracji
ticket-087; zabezpieczono ją patchem z SHA-256. Chronionego review nie zastępuje
samo zaliczenie testów lokalnych. Użytkownik potwierdził rozszerzenie uprawnień maskauth; zmianę opublikowano w `10e535be0c40`. Rozdzielono zasoby pojedynczego wyjścia/dzierżawy i banku wyjść; sześć testów sprawdza dozwolone operacje oraz odmowę dla innych węzłów i niepasujących par capability/resource.
Same indeksy ticketów Displaynet/laboratorium nie zostały opublikowane: pre-commit odrzuca tracking-only changes (GOV-AGENT-HOST-007); zachowano lokalne pliki. Surowe mapy środowiska, logi planfile i lokalne obrazy dysków nie są dowodem
gotowości do publikacji kodu. Checkout c20 wskazuje repozytorium zlecenia/c20,
a jego nieśledzone obrazy dysków przekraczają zwykły limit pliku GitHub.

Próba dodatkowego checkera wellmanifest/docs ujawniła brak formalnej adopcji tego pakietu w `.github` i różnicę własności raportu: sprawdzony wtedy profil 0.1.1 wymagał `subactor/docs` jako domu raportów przekrojowych. Nowszy zaobserwowany main docs 0.2.0 wskazuje `maskservice/report`; takiego repo nie znaleziono w dostępnym katalogu organizacji. Utworzenie i migracja wymagają ustalenia widoczności oraz adopcji/chronionej publikacji tego domu raportów. Poprawiono zgodność nazw plików z ID. Dokumentacja pozostaje raportem organizacji Maskservice; nie deklarujemy pełnej zgodności z tym profilem ani nie zmieniamy jego reguł. C2004 ma odrębną, zweryfikowaną adopcję docs. Uzupełniono ją do polityki 0.2.0 z main `4bd5096e59a4a4b2022949b1a49cba2eb94ed424` (ostatni formalny Release nadal v0.1.0). Preflight miejsca dokumentu, 25 testów adopcji, kontrola 28 dokumentów i hooki przeszły; publikacja C2004: `46cff7ba5`.

<!-- docs:section recommendations -->
## Dalsze prace

Przywrócić dostępne rozliczenie CI lub uzyskać niezależnie zatwierdzoną zmianę
chronionego profilu publikacji. Po integracji ticket-087 odtworzyć ticket-090
na zaakceptowanej bazie i ponownie przeprowadzić oficjalną walidację adopcji.
Przeładować klienta MCP, aby użył poprawionego profilu. Dalsze refaktoryzacje
wybierać z konkretnych kontraktów i pomiarów; nie aktualizować mechanicznie
niezaadoptowanych szkiców standardów ani nie utożsamiać harmonogramu z wykonanym CI.
