---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "maskservice-mcp-refactoring-2026-09-13",
  "kind": "analysis",
  "version": 1,
  "title": "Dostępność MCP i refaktoryzacja Maskservice",
  "status": "accepted",
  "owner": "maskservice/.github",
  "created": "2026-09-13",
  "updated": "2026-09-13",
  "review_after": "2026-09-20",
  "source_revision": "00ea472c9dbad3eab461da6f3bac26a64641fb7a",
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

`stacknet` opublikowano po 105 testach, `redeploy` po 24 testach. Szeroki test
redeploy/update początkowo miał 916 sukcesów i siedem błędów: niezgodny bundle,
kontrakt montowania katalogu oraz pięć braków przeglądarki. Istniejące zadanie
update ticket-087 odświeża bundle do pinu C2004 i poprawia przenośność testu
zewnętrznego redeploy; 19 testów kontraktowych/przeglądarkowych przechodzi przy
użyciu dostępnego Chrome. Zmiany wypchnięto i ponownie otwarto PR #136.

<!-- docs:section hypotheses -->
## Hipotezy

Naprawy obrazu NLP powinny trafić do źródłowego Dockerfile NLP2DSL; obecny adapter
wdrożenia pozwala używać MCP, ale nie stanowi wydania poprawionego upstreamu.
Heurystyczne sugestie refaktoryzacji wymagają sprawdzenia zachowania testami.

<!-- docs:section limitations -->
## Ograniczenia

Aktualizacja standardów update ticket-090 jest wykonywana kolejno po integracji
ticket-087; zabezpieczono ją patchem z SHA-256. Chronionego review nie zastępuje
samo zaliczenie testów lokalnych. W maskauth zastana zmiana uprawnień wyjść
narusza istniejący test zakresu; intencja rozszerzenia wymaga rozstrzygnięcia.
Surowe mapy środowiska, logi planfile i lokalne obrazy dysków nie są dowodem
gotowości do publikacji kodu. Checkout c20 wskazuje repozytorium zlecenia/c20,
a jego nieśledzone obrazy dysków przekraczają zwykły limit pliku GitHub.

<!-- docs:section recommendations -->
## Dalsze prace

Przywrócić dostępne rozliczenie CI lub uzyskać niezależnie zatwierdzoną zmianę
chronionego profilu publikacji. Po integracji ticket-087 odtworzyć ticket-090
na zaakceptowanej bazie i ponownie przeprowadzić oficjalną walidację adopcji.
Przeładować klienta MCP, aby użył poprawionego profilu. Dalsze refaktoryzacje
wybierać z konkretnych kontraktów i pomiarów; nie aktualizować mechanicznie
niezaadoptowanych szkiców standardów ani nie utożsamiać harmonogramu z wykonanym CI.
