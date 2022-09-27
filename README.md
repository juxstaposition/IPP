# IPP

Skript interpret.py bol vytvorený pre interpretáciu xml reprezentácie kódu IPPcode20,
ktorá môže byť generovaná skriptom parse.php z prvej úlohy projektu. Výstupom tohto
skriptu je chybový návratový kód so správou o chybe vypísanej na štandardný chybový
výstup alebo vykonanie inštrukcií, ktoré sú definované v špecifikácii IPPcode20, ktorých
výsledok sa vypíše na štandardný výstup.

Tento skript bol vytváraný objektovo orientovaným prístup, ktorý výrazne uľahčil
implementáciu. Všetky časti programu sa nachádzajú v jednom súbore. Využíva sa
predovšetkým definícia tried a ich metód, ktoré navzájom komunikujú prostredníctvom
inštancií. Jednotlivé triedy a metódy sú detailnejšie komentované v rámci samotného skriptu.
Funkcionalita skriptu bola navrhnutá podľa presnej špecifikácie zadania. Skript bol
implementovaný v plnom rozsahu základnej časti a neobsahuje žiadne z bonusových rozšírení.
Pre spracovanie zdrojového xml súboru bola použitá knižnica ElementTree, ktorá
zabezpečí správne spracovanie xml súboru a jednoduchú iteráciu inštrukciami.
V prípade potreby načítania obsahu zo súborov s koncovkou .in je súbor presmerovaný na
štandardný vstup. Ak chýba parameter --source a xml súbor má byť načítaný zo
štandardného vstupu, toto presmerovanie prebehne až po kompletnom načítaní xml obsahu.
Týmto presmerovaním sa zabezpečí bezproblémové použitie vstavanej funkcie input().
