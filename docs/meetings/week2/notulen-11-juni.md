# Notulen 11 Juni
Notulist: Sverre Kroesen

Iedereen is aanwezig behalve Chris, Martijn en Jim, zij hadden het ook alledrie gemeld.

Vergadering geopend om 13:43, vergadering gesloten om 14:13.

Thomas had wat commentaar op de huidige implementatie van de cursors. We gebruiken TCP, dat verhelpt het probleem, maar we zullen er nog verder naar blijven kijken. Er moet wel nog meer gekeken naar de clientside functionaliteit van de cursors, want nu is er vooral voorgang bij de serverside functionaliteit. Martijn is hier wel al een beetje mee bezig geweest.  

We zijn bezig geweest met de piecetable, Maxim weet hoe dit werkt dus voor vragen kun je bij hem zijn.

Frederick is tot nu toe nog redelijk vaak afwezig, en hij is ook nog een beetje op zoek naar een taak. Er is besloten dat Frederick mee gaat werken aan een stuk tekst vastzetten zodat je het als enige kan bewerken. De projectleider taak is ook niet helemaal een ding meer nu.

## Voortgang user stories
- **Cursor van anderen zien** - Thomas had wat commentaar op de huidige implementatie hiervan. We gebruiken TCP, dat verhelpt het probleem, maar we zullen er nog verder naar blijven kijken. Er moet wel nog meer gekeken naar de clientside functionaliteit van de cursors, want nu is er vooral voorgang bij de serverside functionaliteit. Martijn is hier wel al een beetje mee bezig.

- **Meerdere tabbladen in de editor** - De layout en basisfuncitonaliteit is er, alleen de tabbladen zijn nu een beetje geimplementeerd als snelkoppelingen ipv als tabbladen, en dat is nog niet helemaal ideaal.

## Doel demo vrijdag
Voor de demo van vrijdag willen we iniedergeval dat het zien van de cursor van anderen werkt. Ook willen we dat een bestandlijst ingeladen kan worden en de bestanden zelf ook (allebei vanuit de server, dus niet lokaal zoals we nu wel al hebben).

## Tests
Er wordt nog niet heel veel getest. Het is de vraag hoeveel voor alles unit tests schrijven toevoegt en of het de tijd waard is, maar integratie tests doen kan wel handig zijn, dus Mund gaat hiermee aan de slag. Het idee is een paar tests te maken die alle gewenste functionaliteit testen, zodat je eenvoudig kan zien of er iets stuk gaat bij het aanpassen van code of schrijven van nieuwe code.

## Documentatie
Het is handig om wel een beetje documentatie/comments te schrijven voor je code, en om iniedergeval aan te geven wat voor type bepaalde variabelen zijn. Er kan ook documentatie gegenereerd worden op basis van comments, en dit ook automatisch in de wiki laten zetten. Martijn heeft dit al een keer gedaan, dus met vragen kun je bij hem zijn, of je kunt [hier](https://jsdoc.app) kijken.

## Actiepunten
- Jorik gaat de milestones van deze week bekijken en fixen.
- Mund gaat aan de slag met integratietests.
- Iedereen moet onthouden om zijn code documenteren.
