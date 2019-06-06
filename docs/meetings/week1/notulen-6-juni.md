Datum: Donderdag 6 juni 2019

Notulist: Maxim
Opening v. vergadering: 10:19
Folkert verlaat om 10:49
Vergadering wordt gesloten: 11:08

**Mededelingen**:
Geen medelingen

## Wat is bereikt

**Vorige actiepunten**:
- Robin heeft de discordkanalen geüpdatet
- De vorige notulen is doorgenomen door Jorik en Mark
- Ook zijn de tagbenamingen wat duidelijk gemaakt

**Voortgang editor**:
- Editing is functioneel, door [code mirror](https://codemirror.net/)
- Syntax highlighting is toegevoegd, ook door code mirror
- Meerdere cursoren kunnen worden afgebeeld
- Het editor menu heeft al een aantal basis-opties

**Voortgang server**:
- Belangrijkste: Superklasse die alle services gaan gebruiken is opgezet. Voor uitwisselen berichten
en automatisch doorsturen van berichttypes (via de message bus). Het ontvangen van en naar
de message bus wordt hier geïmplementeerd.
- De basis voor het doorsturen van berichten is functioneel, Robin heeft een demo gegeven.
- Decorators geven aan welke functies specifieke berichttypes kunnen afhandelen, en berichten van dit
type worden automatisch en meteen doorgestuurd naar deze functie. Coördinatie van berichten is daarom
sterk vereenvoudigd.
- Ook gaan reacties op berichten op een efficiënte manier bijgehouden worden, met "prefered destination".


## Wat we gaan doen

**Vandaag editor**:
- Bestanden laden en opslaan
- Mergen van de verschillende onderdelen
- Morgen wilt men een werkende editor kunnen demonstreren

**Vandaag server**: 
- De superklasse wordt in elke apparte service toegepast
- Het file system (in zijn basis, werkende vorm) wordt afgerond
- Het autenticatiesystem zal afgerond worden.

Het doel voor morgen is een demo kunnen geven met twee computers. De basiseditor zal functioneel zijn,
en de server kan met de clients verbinden. Een bestand kan via de server naar de clients worden verstuurd,
en wellicht kunnen verschillende clients hun cursoren tegelijkertijd bewegen.

We gaan ook een gestructueerde demo opstellen. Iemand van het serverteam én van het editor team 
presenteerd. Ze moeten goed op de hoogte zijn van alle voortgang in beide groepen, zodat vragen
kunnen worden beantwoord.

## Actiepunten en opmerkingen

**Opmerking omtrend notulen** 
Wellicht eerst alleen steekwoorden noteren. Ook de discussie wordt als belangrijk ondervonden! 
Daarom wordt vanaf nu verwacht dat deze ook wordt opgenomen in de notulen. 

Omdat er zoveel moet worden geschreven, kan de notulist moeilijker deelnemen aan de discussie.
Wellicht willen we daarom gaan afwisselen

**Opmerking omtrend code mirror**:
Code mirror is door Martijn en Mund als de beste optie voor ons project ondervonden, en
deze gaan we gebruiken voor het project. Ze hebben verschillende frameworks bekijken, 
en code mirror had de volgende voordelen boven andere frameworks:
- Mooie editor
- Goed uitbreidbaar
- Redelijke documentatie

**Opmerking omtrend Network protocol**:
Editor team wilt graag een duidelijk overzicht hebben van de berichten die de client gaat ontvangen.
Dit gaat het server team samen met enkelen van de editor bespreken.

**Over git-gebruik**:
Push controlles van twee mensen is in veel gevallen veel, en zorgt voor teveel overhead. 
Mensen waren _tegen_ open zetten van controlles als er nog snel veel bugs moeten worden gefixt.

Bespreking "hotfix" branch, maar wordt gezien als potentiële bron van verwarring. De keuze ligt 
tussen de develop branch voor dit doeleinde, of een apparte branch. Maar duidelijke commit messages
zouden dit kunnen verbeteren.
Als je geen hotfix channel hebt, dan heb je altijd een reviewer nodig, zelfs voor kleine fixes. 
Zorgt waarschijnlijk voor veel overhead.
Er is nu nog geen beslissing gemaakt, maar deze zal spoedig volgen.

**Evaluatie samenwerking**:
De servergroep zit bij Folkert bij multimedia (hij is TA). Daar is het altijd rustig,
en hierdoor houden we hem betrokken bij de ontwikkelingen. Folkert vond het zelf ook fijn.
Echter wordt nagedacht of het de rest van de samenwerking hindert, omdat de twee groepen
ver van elkaar zitten. Folkert is wel vaak TA, we kijken dit aan. Beslissing: de servergroep
blijft voor nu naar het multimedia-lokaal gaan.

Niemand is ontevreden over hun eigen rol.

Iedereen is tevreden met Robin als voorzitten. Hij wordt gezien als gestructureerd. 
Robin wilt meer aandacht besteden aan de agenda's uitwerken.

Iedereen is tevreden met Jorik als git-coordinator. Mensen zijn tevreden met structuur van
het github-project.

Code reviewers wordt bij teamleden gehouden, omdat deze de code beter begrijpen.

Teamleider, Frederick, wordt verzocht meer betrokken te zijn als leider. Hij wordt verwacht
te overleggen met beide teams, om zo een goed overzicht te houden van het project, de voortgang,
en samenwerking (dus vragen waar iedereen mee bezig is en dergelijke).

Jorik is nu de subleider van het editor team.

Jim rol als communicatie-coordinator gaat goed.

**Actiepunten**:
- Jorik: Notulen + Agenda van master naar develop branch verplaatsen 
- Sverre: Notulen kunnen zeker meer uitgebreid. Zie punt hierboven.
- Robin, Sam, Maxim: Kijken naar valkuilen bij vergelijkbare projecten.
- Tags updaten - "server" voor alle server-gerelateerde dingen, en "editor" voor alle editordingen (GUI én back-end) 
- Server team: Opzetten van de berichttypes naar de clients, zie opmerking hierboven.
- Robin: C++- en C-experts veranderen in Python- en Javascript-experts
