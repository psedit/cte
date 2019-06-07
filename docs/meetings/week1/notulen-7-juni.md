# Notulen - 7 Juni
Notulist: Sverre Kroesen

De vergadering vandaag verliep niet zoals in de agenda, omdat we in plaats van de onderwerpen in de agenda aan de slag gingen aan de user stories bij dit project, op advies van Thomas. Zo kunnen we bepalen waar we aan moeten werken op basis van de user stories, in plaats van op basis van wat we technisch werkend willen hebben, zoals we tot nu toe hebben gedaan.

## User stories

Als een gebruiker, wil ik...
- ...de cursor van andere gebruikers kunnen zien, om een overzicht te hebben van wie wat waar doet.
- ...een stuk als enige kunnen aanpassen, om iets te kunnen aanpassen zonder dat mijn aanpassingen gauw ongedaan gemaakt wordt door een andere gebruiker.
- ...kunnen zien wie nog meer aan het werk is aan hetzelfde project als ik.
- ...toegang hebben tot bestanden op de server, om ze te kunnen bewerken, bekijken, runnen, etc.
- ...bestanden kunnen toevoegen aan (en verwijderen van) de server, zodat andere gebruikers die met mij samenwerken er bij deze bestanden kunnen.
- ...een account hebben met een wachtwoord, zodat mijn bestanden op die manier beschermd kunnen worden.
- ...verandering van text real-time kunnen zien, om een overzicht te hebben van wie wat waar doet.
- ...kunnen communiceren buiten de code.
- ...een project aan kunnen maken, om bestanden geclusterd op te kunnen slaan.
- ...git-integratie in de editor, want ik wil version control voor mijn project.
- ...meerdere tabbladen in de editor hebben, om gemakkelijk in meerdere bestanden tegelijk te kunnen werken.
- ...dat lokaal een versie van de bestanden waar ik aan werk wordt opgeslagen, om ook lokaal de code te kunnen runnen.
- ...mijn eigen aanpassingen gemakkelijk ongedaan kunnen maken, om eigen fouten snel te kunnen corrigeren.
- ...zien wie wat wanneer heeft aangepast, zodat ik weet aan wie ik vragen moet stellen over stukken code.

**Geschrapte user stories**
- Als een gebruiker, wil ik kunnen editen zonder conflicten met andere gebruikers, om consensus/overeenstemming te hebben met andere gebruikers over de code.

Deze user story werd beoordeeld als te groot.

## Scrum poker sessie
We hebben een scrum poker sessie gedaan, waarbij we allemaal (zonder dat de rest het ziet) een getal van 1 t/m 5 kiezen wat aangeeft hoe moeilijk we de user story vinden. Zo kunnen we erachter komen hoe moeilijk een probleem wordt gevonden en waarom, en zo een schatting maken van hoe moeilijk het daadwerkelijk is. 

Een score van 1 stelt hierbij een vrij triviaal probleem voor, en 5 een erg moeilijk probleem.

**Cursor van anderen zien** - Over het algemeen werd dit eerst niet gezien als een groot probleem. Alleen Mund gaf het een 4, en verder gaven mensen vooral 2 of 3. De enige moeilijkheid die veel mensen zagen was de server laten doorgegeven op welke locatie in de tekst een cursor staat, maar Mund kwam met het punt dat de cursor mee moet bewegen als er tekst wordt geplaatst boven de cursor.
Uiteindelijk gaven we het een 2.5.

**Editen zonder conflicten** - Mund, Jorik en Sam gaven het 5/5, de rest allemaal 4/5. Het werd dus als een erg moeilijk probleem ervaren, dus we hebben het geschrapt (en vervangen door de user story die zegt dat je als gebruiker iets als enige wilt kunnen aanpassen).

**Zien met wie je werkt** - Dit probleem werd rond de 2 en de 3 ingeschat. Niet iedereen interpreteerde het probleem hetzelfde: je kan bijhouden wie er allemaal nog meer aan hetzelfde project werkt, maar ook wie er precies allemaal in hetzelfde bestand werkt. Uiteindelijk bedachten we dat als de cursors van anderen zien werkend is, deze user story ook makkelijker op te lossen is door te kijken naar de cursors. We gaven het probleem dus een 2.

**Toegang tot bestanden tot de server**- Dit gaven we een 2.

**Een stuk tekst als enige aanpassen** - Dit gaven we een 3.

**Bestanden toevoegen aan en verwijderen van de server** - Dit gaven we een 2.

**Meerdere tabbladen in de editor** - De meeste mensen gaven dit een 3, er waren 3 mensen die het een 2 gaven, en Folkert gaf het een 4, want het kan moeilijk zijn om van alle aanpassingen van tabbladen in de achtergrond bij te houden. We kunnen het ook inplementeren door gewoon het bestand opnieuw te laden, dat is een stuk makkelijk. We gaven het uiteindeijk een 2.5.
