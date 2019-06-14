# Notulen 14 Juni

## User stories
Hier is een overzicht van de user stories waar we nu aan willen/moeten werken, en waar we nu over hebben gepokerd met een score van 1 t/m 5. We werden echter halverwege onderbroken toen Thomas en Ana Oprescu binnenkwamen, daarna hebben we besproken hoe de vorige sprint ging en we hebben een overzicht gemaakt van wat nog allemaal moet gebeuren voor het vastzetten/locken van berichten.

- **Een blok code vastzetten/locken** - We gaven dit een 4.
- **Een blok code wat vastgezet/gelocked is als enige kunnen aanpassen** - Hierbij is het probleem natuurlijk dat je aanpassingen ook op de server moeten komen te staan, en gelijk zichtbaar moeten worden voor andere gebruikers. We gaven dit een 4.
- **Kunnen communiceren via een chat** - We gaven dit een 2.5.
- **Versie van bestanden lokaal opslaan om ook offline te kunnen werken** - We gaven dit een 2.
- **Bestanden toevoegen/verwijderen**
- **Een annotatie toevoegen bij een stuk code**
- **Het kunnen zien als iemand anders iets selecteert**

Een probleem wat we nog hadden is dat het testen en documenteren van code wel iets is wat moet gebeuren, maar daar kun je natuurlijk moeilijk een user story over schrijven. Maandag is echter een hoorcollege hierover.

## Afgelopen sprint
We hebben de doelen voor de afgelopen sprint niet helemaal gehaald, het is nog de vraag waarom. Het is wel zo dat de moeilijke problemen moeilijk te verdelen zijn tussen een grotere groep mensen, en we denken dat dit ook een belangrijke reden is geweest dat de sprint niet helemaal is gehaald.

## Over het vastzetten/locken van stukken code

### Wat is de piecetable?
De piecetable is de representatie die we hebben voor een bestand en de locks in dat bestand. Van elk bestand wat op de server staat geeft de piecetable aan waar een bepaald gelocked stuk code in een bestand staat. Elke kolom van het tabel bevat een id van het lock, de startregel van de lock en de lengte van het lock. In de backend is al geregeld dat twee pieces gemerged kunnen worden.

Hieronder staat een overzicht van alle dingen die voor dit issue/user story nog op de back- en frontend geimplementeerd moeten worden. We werken dit nu uit omdat dit het belangrijkste is wat er nog moet gebeuren voor het hele project en we het dus echt aankomende vrijdag af moeten hebben.

### Backend
- De piecetable moet unieke IDs per piece hebben.
- De piecetable moet naar de client gestuurd worden.
- Een stuk code moet gelocked kunnen worden op basis van de ID, offset, en lengte.
- Edit messages - berichten die aanpassingen in bestanden aangeven ontvangen en interpreteren.
- Veranderingen in de piecetable moeten gebroadcast worden naar de frontend. *Dependency: edit messages*.
- Veranderingen in een piece moeten gebroadcast worden naar de frontend. *Dependency: piecetable sturen naar client*.

### Frontend
- De piecetable kunnen representeren in de frontend.
- Een lock aan kunnen vragen in de user interface.
- Een lock aan kunnen vragen vanuit de frontend naar de client. *Dependency: locken op server*.
- Errormessages moeten getoond kunnen worden.
- Het koppelen van de piecetable met de codemirror editor. *Dependency: representatie piecetable*.
- Broadcasts van de server moeten geinterpreteerd worden. *Dependencies: broadcasts vanuit de server, errormessages*.
- Veranderingen in een piece moeten (asynchroon) gestuurd worden naar de backend. *Dependency: edit messages*.

Het unlocken van een stuk code is natuurlijk heel nuttig, maar nog niet noodzakelijk voor de demo of voor een minimum viable product, daarom staat het er niet tussen.

We hebben afgesproken maandag met Thomas de voortgang te bespreken.
