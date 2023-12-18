<template>
  <v-container class="lorem-ipsum">
    <v-layout column>
      <v-flex>
        <h2>Kyykkä sivusto on päivittynyt!</h2>
        
        <p>Hei täältä kehitystyön takaa. Täällä on painettu duunia maailman parasta kyykkää pelaavan liigan iloksi ja nyt (ehkä) ensimmäiset kunnolliset muutokset meidän ihanalle nettisivullemme saapuvat kaikkien näkyville. Tulevaisuudessa näistä päivityksistä tuskin ilmoitamme näin äänekkäästi, mutta ymmärtääkseni sivustolle on tullut jotain uutta viimeksi, kun uusi sivusto luotiin (josta alkaa olemaan jo 4-5 vuotta). Listaan alla uusista asioita/muutoksista:</p>
        <p><b>1.</b> Uusi '<b>Pelaaja</b>' - sivu kaikkineen hienouksineen. Paina pelaajan nimeä missä vain päästäksesi katsomaan tämän pelaajan statseja kautta historian!</p>
        <p><b>2.</b> <b>Vanha data</b> on lisätty. Dataa löytyy 2000-kaudesta alkaen. Huomioita datan lukijalla: Aikoinaan pelattiin 19 tolpalla. Aikoinaan oli sanktioita ja aikoinaan haukia ei ollut merkitty heittokohtaisesti tietokantaan, vaan erä kohtaisesti summattu. Nämä ohi heitot on merkitty eri tavalla jos ei voinut olla varma että heitto oli ollut hauki vai virkamies. Muistaakseni tämä vaikuttaa vain ennen 2013 kautta pelattuja pelejä. Merkintä tapa heittäjälle on ollut. Formaatti on niinkin epäselvä kuin " h{haukien määrä}0{virkamiesten määrä} "</p>
        <p><b>3.</b> <b>Sivupalkin</b> tilastoihin: Lisätty pistettä per ottelu ja ottelu keskiarvo. Lisäksi sivupalkki näyttää nyt vain runkosarjan tulokset ja jaoteltuna eri lohkoihin </p>
        <p><b>4.</b> <b>Ottelut</b> - sivulla on nyt myös pelityyppi (Runkosarja, Finaali, puolivälierä tms.). Jos valitsee katsottavaksi vain jatkosarjan pelejä, on pelit ryhmitelty per jatkopelisarja.</p>
        <p><b>5.</b> <b>Skaalatut Pisteet</b> ovat takaisin <b>Pelaajat</b>-sivulla! Skaalatut pisteet ovat mallia NKL. Kaava on: s = (2n(w + h))/10 , missä s on skaalatut pisteet, n on heitossa poistetut kyykät, w on skaalauskerroin (heittäjän 1. ja 2. heitolle 9 ja lopuille 13) ja h on heittovuoro.</p>
        <p>Joitain pienmpiä muutoksia ehkä jäi mainisematta ja siitäkin suurin osa onkin vain esiriipun takana tapahtunutta muutosta. Omaksi huviksi tätä on koodailu ja siksi talvikauden aikana tuskin tulee mitää yhtä 'mullistavaa' tai ainakaan yhtä paljon muutoksia.</p>
        <p></p>
        <p>Terveisin sivuston (tämän hetkinen) ylläpitäjä.</p>
        
        <h2>Ohjeita kapteeneille</h2>

        <p>
          Voitte varata joukkueeseen pelaajia "Oma joukkue" sivun alalaidasta löytyvällä "Varaa pelaajia" toiminnolla.
          Ottelutulos tallentuu syötettäessä reaaliaikaisesti. Suosittelemme ottelutuloksen syöttämisen jälkeen vielä päivittämään ottelusivun, ja varmistamaan että syöttö on onnistunut.
          Ottelutuloksen syöttämisen jälkeen vierasjoukkueen kapteenin tulee vielä vahvistaa tulos ottelusivulta, jonka jälkeen pisteet päivittyvät statseihin.
        </p>

        <h2>Kausiennakko 2023</h2>

          <h3>Lohko A</h3>
          <p>1. Mallinnetaan Haukia Laskimet Kuumana [MaHaLasKu]</p>
          <p>Neljännen sijan kirouksesta ei tämän joukkueen tapauksessa voida enää puhua. Jarnon varmalla johdatuksella MaHaLasKu laskeskelee itsensä helpon oloisesti lohkon ykkösenä jatkoon. Massupojat ovat tehneet offseasonilla hankintoja nuoremmista laskimennäpyttelijöistä jatkamaan seuran perinteitä. Tästä johtuen runkosarjan aikana saattaa tuloksissa ilmetä pientä satunnaisvaihtelua, mutta tulokkailla on kuitenkin konkareiden jäljiltä hyvä polku tampattuna, jota seurata päätyyn asti. Suurin uhka joukkueella on ennakkosuosikin viitan paino hartioilla.</p>

          <p>2. Draconis [Dra] </p>
          <p>Draconiksen viime kausi päättyi sensaatiomaiseen pettymykseen, joukkueen pudottua ensimmäistä kertaa miesmuistiin NKL:än neljän parhaan ulkopuolelle. Niinpä Lohikärmes on 
          laittanut pelaajamarkkinoilla tuulemaan ja hankkinut “uuden” pelaajan ja Tiinan myötä lisää sitä kuuluisaa kokemuksen tuomaa varmuutta. Löytyypä joukkueesta myös kolmea kyykkäliigaa pelaavaa Ippe ja kaikessa keitetty Temmi vaan se että sattuvatko männävuosien tähdet samaan peliin pelaamaan on asia erikseen. Kannatteleeko ääretön kokemus Draconiksen vielä runkkarin piikkipaikoille vai alkaako reumatismi jo vaivata ranteita?</p>
          <p>3. Kyykkäkerho RSÄ [KyRSÄ]</p>
          <p>Titeläisten ikääntyvä edustusjoukkue on tahkonnut NKL:ää jo useamman vuoden ja löytänyt tiensä lopulta myös kyykkä A. Sian tuntijoiden tietoisuuteen. Poijukartut on toivottavasti jo poltettu wappunotskissa sillä huhujen mukaan joukkueen pelaajat ovat hankkineet ihan oikean mallisia kapuloita sekä naisoletetun tähtipelaajan kantamaan poikia kohti liigan kärkeä. Alkukesästä kuului myös uhkauksia ahkerasta harjoittelusta, valitettavasti ne treenitunnit valui joko CS-servuille tai johonkin helvetin golfkentille. Aiemmilta vuosilta tuttu tasaisuus saattaa pienellä tulostason korotuksella kantaa pitkälle. Simulaatioissa Kyykkäkerho RSÄ siis A-lohkon kolmas.</p>
          <p>4. Karttu Wiskarit [KW]</p>
          <p>Karttu Wiskarit lähtevät liigan parhaalla nimellä ja mielenkiintoisilla rosterimuutoksilla uuteen NKL-kauteen. Suomen muotoisen pilven alla on tehty uusia mielenkiintoisia hankintoja ja joukkueesta löytyykin liitonkin kisoissa kesällä kunnostautuneita nimiä. Joukkueesta löytyy sopivassa suhteessa vielä nuoruuden intoa kuten myös Elämän Kovan Koulun tuomaa kokemusta. Jos KooWeelle siunaantuu menestystä, järjestettänee juhlat Kankaanpään torilla, mutta sinne mieliäkseen täytyy varoa Tappavan hiljaisia rivinpätkiä ja niiden jättämistä kenttään. Mökkitien päässä siintää kuitenkin A-lohkon nelossija jonka jälkeen pelaajat jäävät miettimään Tässäkö tää oli? No ei sentään vaan pudotuspelien jälkeen muistellaan sitä Kun me DiSKOA suudeltiin.</p>
          <p>5. Skinnarilan Sika Klupi [SSK]</p>
          <p>Jaaha, viina maistuu ja kartut lentää. lappeen Rantojen kovaäänisin kyykkäjoukkue kuorii vastustajien sipulia huutelullaan ja pelaa siinä sivussa hämmentävän kovaa tulosta. Viime kaudella siat olivat runkkarissa top 8 joukossa sekä etenivät pudotuspeleissä vakuuttavasti toiselle kierrokselle, missä kuitenkin vastaan tuli MaHaLasKu-niminen seinä. Tänä vuonna tullee olemaan samanlainen ääni kellossa, ja miksei samanlainen tulostasokin. Vanhojen karjujen eläköityessä on klupi hankkinut uutta (sian)verta täydentämään rivejään, mutta eivätköhän tulokkaatkin opi pikkuhiljaa tavoille - ja pelaamaan kyykkää.</p>


          <h3>Lohko B</h3>
          <p>1. KonjakkiMafia [VSOP]</p>
          <p>Uusi nimi ja uudet kujeet. Viime kaudella hyviä elkeitä näyttänyt mafiosojen jengi otti suomi-konepistoolit käteen ja lähti pimeille markkinoille hankkimaan uusia pelaajia. Rosterista päätellen voi todeta että uhkailu, kiristys ja lahjonta toimii erittäin hyvin pelaajahankinnoissa. On vuoden tulokasta, 2 kpl kaksinkertaista NKL mestaria ja mansikkana kakun välissä 2022 paras runkkari, eiku runkosarjan paras pelaaja ja SM hopeamitalisti. Paljon uusia kovan luokan pelaajia ja kapteenin roolikin siirretty uudelle pelaajalle. KonjakkiMafialla pontentiaalia on vähintäänkin riittävästi, mutta nähtäväksi jää hajoaako paletti kesken kauden taiteellisiin erimielisyyksiin.</p>
          <p>2. Sätkyn Äärettömän Taidokas Kyykkä Yhteisö [SÄTKY KY]</p>
          <p>Viime kauden menestyksen myötä SÄTKY KY imaisi mukaansa lisää tasokkaita pelaajia. AA-kerho tuo vihreähaalareille varmasti sekä kovan tasonnoston tuloksiin että liigaformaatissa aina niin tärkeää tasaisuutta. B-lohkon kärkipaikasta käydään tiukkaa kamppailua joka voi hyvinkin ratketa peluutukseen. Rosterista näyttää löytyvän abaut tosi monta riviheittäjää suhteessa lakaisijoiden määrään, joten peräpään puhtaana pitämisessä voi ilmetä hankaluuksia. Kaikkein säteilevimpiin tuloksiin tarvitaan huippusuorituksia koko rosterin leveydeltä, mutta alkukauden kovimman jännityksen purkauduttua saatetaan kyykkäkentällä nähdä vaikka voltteja.</p>
          <p>3. Diskonttaajat Sipuloivat Katiska Osumia [DiSKO]</p>
          <p>Tutalaisten dream team on päättänyt mennä, muista kärkijoukkueista poiketen, vain yhden pelaajan hankinnalla. Tutalaiset ovat huhujen mukaan hankkineet uuden pelaajan puhtaasti pelinjohdollisiin tehtäviin, kuitenkin sillä oletuksella että joukkueen johtaja osallistuisi myös peliin. Tutalaisten hankinta on kuin onkin lähes täydellinen tutalainen. Neliöön kävellessä mies ei aina tiedä itsekkään mitä kättä heiluttaa kartun kahvalle. Joukkueen treenitulokset ovat täysin mysteerejä asiantuntijoille. Treenitunteja kerrytetään niin pohjoisessa, ettei asiantuntija ole löytäneet näille kaukomaan kenttien laidoille. Joukkueelta taitaa kuitenkin jäädä korkeimmat sijat saavuttamatta, ellei uusi joukkueenjohtaja tuo mullistavia muutoksia peluutukseen.</p>
          <p>4. Bitches out of Booze, Saatana! [BooB's]</p>
          <p>Sosiaalisessa mediassa maailman eniten seurattua kyykkäjoukkuetta, BooB’s:eja ei voi enää kukaan ottaa helppona vastuksena. 2022 MM-kyykässä tissit näyttivät olevansa valmiita haastamaan kenet tahansa sijoittumalla turnauksessa hopealle. BooB’s peli tulee olemaan henkisesti vaikea paikka monelle kovalle joukkueelle loputtoman länkytyksen ansiosta. Henkisen yliotteen avulla tissit nostavat aina pelin tunnelmaa korkealle. Näennäisesti uusia tulokkaita on joukkeessa paljon, mutta rekrytointi on kyykkä_asian_tuntijoiden mielestä onnistunut erinomaisesti. Rintoja kohottaneen nuorennusleikkauksen jälkeen Boobsit lähtevätkin terhakkaina haastamaan kaikkia. Kuitenkin B-lohkon 4. sija tulee todennäköisesti olemaan korkein sijoitus tällä kaudella, ellei joukkuessa päästä eroon runkosarjassa aikaisemmin piinaneesta “aina maksimit”-viiruksesta. </p>
          <p>5. Alkosta Liikaa Tiukkaa Faktat Filosofioitiin Fiksusti Finaalissa [ALT F4]</p>
          <p>Pelistä mahdollisimman nopeasti poistuvilla koodareilla alkaa pikkuhiljaa olla kaikki edellytykset alkaa menestyä NKL:ssä ja havitella pudotuspelipaikkaa tosissaan. Vaikka pelaajamarkkinoilla ei kesäkauden aikana pystyttykään vastaamaan muiden joukkueiden tarjouksiin huippupelaajista, on titeläisten lähtökohdat kauteen parhaat tähän mennessä. Kyykkä aasian tuntijoiden vakoilu- ja tiedustelujaosto on havainnut porukan treenaamassa gardenilla ja tulostaso on tietojen mukaan ollut vähintään kohtalaista, eikä pidä myöskään unohtaa, että joukkue kävi viime vuonna keräämässä kokemusta PoWiCupin jalosarjasta. Erityisesti joukkueen konapommiosasto Otto ja Konsta ovat aiheuttaneet preseasonin suorituksillaan hyväksyvää nyökyttelyä. Kovan kärjen jälkeen alkaakin murheet kasautua sillä siivousosastolla tulossarakkeeseen kirjataan liian usein 01001000. Niimpä kovimpiin kärkisijoihin oikeuttavat tulokset loistavat poissaolollaan.</p>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
    name: 'LoremIpsum'
};
</script>

<style scoped></style>
