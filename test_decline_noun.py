import re, sys
import decline_noun

# Kotus declensions:
# 1=valo, 2=palvelu, 3=valtio, 4=laatikko, 5=risti, 6=paperi, 7=ovi, 8=nalle,
# 9=kala, 10=koira/kahdeksan, 11=omena, 12=kulkija, 13=katiska, 14=solakka,
# 15=korkea, 16=vanhempi, 17=vapaa, 18=maa, 19=suo, 20=filee, 21=rosé,
# 22=parfait, 23=tiili, 24=uni, 25=toimi, 26=pieni, 27=käsi, 28=kynsi,
# 29=lapsi, 30=veitsi, 31=kaksi, 32=sisar/kymmenen, 33=kytkin, 34=onneton,
# 35=lämmin, 36=sisin, 37=vasen, 38=nainen, 39=vastaus, 40=kalleus, 41=vieras,
# 42=mies, 43=ohut, 44=kevät, 45=kahdeksas, 46=tuhat, 47=kuollut, 48=hame,
# 49=askel/askele

# nominative_singular: (genitive_singulars_in_alphabetical_order)
TESTS_GEN_SG = {
    # more than one declension (all)
    "ahtaus": ("ahtauden", "ahtauksen"),
    "alpi": ("alpin", "alven"),
    "csárdás": ("csárdáksen", "csárdásin"),
    "havas": ("hapaan", "havaksen"),
    "helpi": ("helpin", "helven"),
    "kaihi": ("kaihen", "kaihin"),
    "kallas": ("kallaksen", "kaltaan"),
    "karhi": ("karhen", "karhin"),
    "karvaus": ("karvauden", "karvauksen"),
    "koiras": ("koiraan", "koiraksen"),
    "kuori": ("kuoren", "kuorin"),
    "kuskus": ("kuskuksen", "kuskusin"),
    "kuusi": ("kuuden", "kuusen"),
    "kymi": ("kymen", "kymin"),
    "kymmenes": ("kymmeneksen", "kymmenennen"),
    "lahti": ("lahden", "lahdin"),
    "laki": ("laen", "lain"),
    "olas": ("olaan", "olaksen"),
    "ori": ("oriin", "orin"),
    "pallas": ("pallaksen", "paltaan"),
    "palvi": ("palven", "palvin"),
    "peitsi": ("peitsen", "peitsin"),
    "ripsi": ("ripsen", "ripsin"),
    "rosvous": ("rosvouden", "rosvouksen"),
    "saksi": ("saksen", "saksin"),
    "siitake": ("siitaken", "siitakkeen"),
    "siivous": ("siivouden", "siivouksen"),
    "sini": ("sinen", "sinin"),
    "sioux": ("sioux'n", "siouxin"),
    "syli": ("sylen", "sylin"),
    "uros": ("uroksen", "uroon"),
    "vakaus": ("vakauden", "vakauksen"),
    "viini": ("viinen", "viinin"),
    "vuori": ("vuoren", "vuorin"),
    "vyyhti": ("vyyhden", "vyyhdin"),

    # declension 1
    "ehto": ("ehdon",),
    "kirppu": ("kirpun",),
    "korko": ("koron",),
    "kumpu": ("kummun",),
    "kyky": ("kyvyn",),
    "laku": ("lakun",),
    "muki": ("mukin",),
    "murto": ("murron",),
    "orpo": ("orvon",),
    "pelto": ("pellon",),
    "rako": ("raon",),
    "rapu": ("ravun",),
    "rento": ("rennon",),
    "suku": ("suvun",),
    "söpö": ("söpön",),
    "tikku": ("tikun",),
    "tyttö": ("tytön",),
    "valo": ("valon",),
    "vappu": ("vapun",),
    "vihko": ("vihon",),
    "vilu": ("vilun",),
    "yö": ("yön",),
    "äly": ("älyn",),

    # declension 2
    "palvelu": ("palvelun",),
    "väestö": ("väestön",),

    # declension 3
    "valtio": ("valtion",),
    "yhtiö": ("yhtiön",),

    # declension 4
    "laatikko": ("laatikon",),

    # declension 5
    "lux": ("luxin",),
    "risti": ("ristin",),
    "šakki": ("šakin",),
    "self-made man": ("self-made manin",),
    "wok": ("wokin",),
    "vouti": ("voudin",),

    # declension 6
    "lumen": ("lumenin",),
    "paperi": ("paperin",),
    "weber": ("weberin",),

    # declension 7
    "arki": ("arjen",),
    "arpi": ("arven",),
    "impi": ("immen",),
    "jälki": ("jäljen",),
    "järki": ("järjen",),
    "kaski": ("kasken",),
    "lehti": ("lehden",),
    "läpi": ("läven",),
    "olki": ("oljen",),
    "onki": ("ongen",),
    "ovi": ("oven",),
    "piki": ("pien",),
    "soppi": ("sopen",),
    "tuki": ("tuen",),

    # declension 8
    "jeppe": ("jepen",),
    "nalle": ("nallen",),
    "nukke": ("nuken",),

    # declension 9
    "aika": ("ajan",),
    "arka": ("aran",),
    "jalka": ("jalan",),
    "kala": ("kalan",),
    "iskä": ("iskän",),
    "lanka": ("langan",),
    "lika": ("lian",),
    "taika": ("taian",),
    "takka": ("takan",),
    "vaaka": ("vaa'an",),
    "vehka": ("vehkan",),
    "velka": ("velan",),
    "vihta": ("vihdan",),
    "virka": ("viran",),

    # declension 10
    "kahdeksan": ("kahdeksan",),
    "koira": ("koiran",),
    "nälkä": ("nälän",),
    "seitsemän": ("seitsemän",),
    "yhdeksän": ("yhdeksän",),
    "ylkä": ("yljän",),

    # declension 11
    "omena": ("omenan",),

    # declension 12
    "kulkija": ("kulkijan",),

    # declension 13
    "katiska": ("katiskan",),

    # declension 14
    "solakka": ("solakan",),

    # declension 15
    "korkea": ("korkean",),

    # declension 16
    "idempi": ("idemmän",),
    "vanhempi": ("vanhemman",),

    # declension 17
    "vapaa": ("vapaan",),

    # declension 18
    "maa": ("maan",),

    # declension 19
    "suo": ("suon",),

    # declension 20
    "filee": ("fileen",),

    # declension 21
    "rosé": ("rosén",),

    # declension 22
    "parfait": ("parfait'n",),

    # declension 23
    "tiili": ("tiilen",),

    # declension 24
    "uni": ("unen",),

    # declension 25
    "toimi": ("toimen",),

    # declension 26
    "pieni": ("pienen",),

    # declension 27
    "käsi": ("käden",),

    # declension 28 (all)
    "hirsi": ("hirren",),
    "jälsi": ("jällen",),
    "kansi": ("kannen",),
    "karsi": ("karren",),
    "kirsi": ("kirren",),
    "korsi": ("korren",),
    "kynsi": ("kynnen",),
    "länsi": ("lännen",),
    "orsi": ("orren",),
    "parsi": ("parren",),
    "ponsi": ("ponnen",),
    "pursi": ("purren",),
    "varsi": ("varren",),
    "virsi": ("virren",),

    # declension 29 (all)
    "hapsi": ("hapsen",),
    "lapsi": ("lapsen",),
    "uksi": ("uksen",),

    # declension 30 (all)
    "veitsi": ("veitsen",),

    # declension 31 (all)
    "haaksi": ("haahden",),
    "kaksi": ("kahden",),
    "yksi": ("yhden",),

    # declension 32
    "ahven": ("ahvenen",),
    "höyhen": ("höyhenen",),
    "ien": ("ikenen",),
    "jumalatar": ("jumalattaren",),
    "jäsen": ("jäsenen",),
    "kaunotar": ("kaunottaren",),
    "kymmenen": ("kymmenen",),
    "nivel": ("nivelen",),
    "onnetar": ("onnettaren",),
    "papitar": ("papittaren",),
    "siemen": ("siemenen",),
    "sisar": ("sisaren",),
    "syöjätär": ("syöjättären",),
    "sävel": ("sävelen",),

    # declension 33
    "annin": ("antimen",),
    "avarrin": ("avartimen",),
    "elin": ("elimen",),
    "heitin": ("heittimen",),
    "kytkin": ("kytkimen",),
    "näin": ("näkimen",),
    "otin": ("ottimen",),
    "pidin": ("pitimen",),
    "puin": ("pukimen",),
    "pyyhin": ("pyyhkimen",),
    "raavin": ("raapimen",),
    "sydän": ("sydämen",),
    "uistin": ("uistimen",),
    "ydin": ("ytimen",),

    # declension 34
    "alaston": ("alastoman",),
    "onneton": ("onnettoman",),
    "yötön": ("yöttömän",),

    # declension 35 (all)
    "lämmin": ("lämpimän",),

    # declension 36
    "alin": ("alimman",),
    "sisin": ("sisimmän",),
    "uloin": ("uloimman",),

    # declension 37 (all)
    "vasen": ("vasemman",),

    # declension 38
    "nainen": ("naisen",),
    "osanen": ("osasen",),
    "öinen": ("öisen",),

    # declension 39
    "aines": ("aineksen",),
    "vastaus": ("vastauksen",),
    "varis": ("variksen",),
    "yritys": ("yrityksen",),

    # declension 40
    "kalleus": ("kalleuden",),
    "äreys": ("äreyden",),

    # declension 41
    "allas": ("altaan",),
    "altis": ("alttiin",),
    "kinnas": ("kintaan",),
    "mätäs": ("mättään",),
    "ratas": ("rattaan",),
    "ruis": ("rukiin",),
    "rynnäs": ("ryntään",),
    "tahdas": ("tahtaan",),
    "tikas": ("tikkaan",),
    "vantus": ("vanttuun",),
    "varas": ("varkaan",),
    "varras": ("vartaan",),
    "vieras": ("vieraan",),

    # declension 42 (all)
    "mies": ("miehen",),

    # declension 43
    "immyt": ("impyen",),
    "ohut": ("ohuen",),

    # declension 44 (all)
    "kevät": ("kevään",),

    # declension 45
    "kahdeksas": ("kahdeksannen",),
    "neljäs": ("neljännen",),

    # declension 46 (all)
    "tuhat": ("tuhannen",),

    # declension 47
    "kuollut": ("kuolleen",),
    "tehnyt": ("tehneen",),

    # declension 48
    # -Ve
    "aie": ("aikeen",),
    "alue": ("alueen",),
    "hiue": ("hiukeen",),
    "koe": ("kokeen",),
    "lippue": ("lippueen",),
    "pesue": ("pesueen",),
    "pue": ("pukeen",),
    "säe": ("säkeen",),
    "tae": ("takeen",),
    "yhtye": ("yhtyeen",),
    # -je
    "hylje": ("hylkeen",),
    "kirje": ("kirjeen",),
    "koje": ("kojeen",),
    "lahje": ("lahkeen",),
    "sulje": ("sulkeen",),
    # -ke
    "hanke": ("hankkeen",),
    "jatke": ("jatkeen",),
    "leike": ("leikkeen",),
    "ryske": ("ryskeen",),
    "sähke": ("sähkeen",),
    "virke": ("virkkeen",),
    "välke": ("välkkeen",),
    # -Ce (not -je, -ke)
    "ahne": ("ahneen",),
    "aihe": ("aiheen",),
    "ape": ("appeen",),
    "hame": ("hameen",),
    "helle": ("helteen",),
    "ihme": ("ihmeen",),
    "lumme": ("lumpeen",),
    "ripe": ("rippeen",),
    "sose": ("soseen",),
    "suhde": ("suhteen",),
    "tunne": ("tunteen",),
    "uurre": ("uurteen",),
    "vuode": ("vuoteen",),

    # declension 49 (all)
    "askel": ("askelen",),
    "askele": ("askeleen",),
    "kannel": ("kantelen",),
    "kinner": ("kinteren",),
    "manner": ("manteren",),
    "ommel": ("ompelen",),
    "penger": ("penkeren",),
    "piennar": ("pientaren",),
    "säen": ("säkenen",),
    "taival": ("taipalen",),
    "tanner": ("tanteren",),
    "udar": ("utaren",),
    "vemmel": ("vempelen",),
}

# these behave like genitive plural, so not many tests needed
TESTS_NOM_PL = {
    "kuusi": ("kuudet", "kuuset"),
    "esine": ("esineet",),
    "kymmenen": ("kymmenet",),
    "valo": ("valot",),
}
TESTS_TRA_SG = {
    "kuusi": ("kuudeksi", "kuuseksi"),
    "esine": ("esineeksi",),
    "kymmenen": ("kymmeneksi",),
    "valo": ("valoksi",),
}
TESTS_INE_SG = {
    "kuusi": ("kuudessa", "kuusessa"),
    "esine": ("esineessä",),
    "kymmenen": ("kymmenessä",),
    "valo": ("valossa",),
}
TESTS_ELA_SG = {
    "kuusi": ("kuudesta", "kuusesta"),
    "esine": ("esineestä",),
    "kymmenen": ("kymmenestä",),
    "valo": ("valosta",),
}
TESTS_ADE_SG = {
    "kuusi": ("kuudella", "kuusella"),
    "esine": ("esineellä",),
    "kymmenen": ("kymmenellä",),
    "valo": ("valolla",),
}
TESTS_ABL_SG = {
    "kuusi": ("kuudelta", "kuuselta"),
    "esine": ("esineeltä",),
    "kymmenen": ("kymmeneltä",),
    "valo": ("valolta",),
}
TESTS_ABE_SG = {
    "kuusi": ("kuudetta", "kuusetta"),
    "esine": ("esineettä",),
    "kymmenen": ("kymmenettä",),
    "valo": ("valotta",),
}

TESTS_ESS_SG = {
    # more than one declension (all)
    "ahtaus": ("ahtauksena", "ahtautena"),
    "alpi": ("alpena", "alpina"),
    "csárdás": ("csárdáksena", "csárdásina"),
    "havas": ("hapaana", "havaksena"),
    "helpi": ("helpenä", "helpinä"),
    "kaihi": ("kaihena", "kaihina"),
    "kallas": ("kallaksena", "kaltaana"),
    "karhi": ("karhena", "karhina"),
    "karvaus": ("karvauksena", "karvautena"),
    "koiras": ("koiraana", "koiraksena"),
    "kuori": ("kuorena", "kuorina"),
    "kuskus": ("kuskuksena", "kuskusina"),
    "kuusi": ("kuusena", "kuutena"),
    "kymi": ("kymenä", "kyminä"),
    "kymmenes": ("kymmeneksenä", "kymmenentenä"),
    "lahti": ("lahtena", "lahtina"),
    "laki": ("lakena", "lakina"),
    "olas": ("olaana", "olaksena"),
    "ori": ("oriina", "orina"),
    "pallas": ("pallaksena", "paltaana"),
    "palvi": ("palvena", "palvina"),
    "peitsi": ("peitsenä", "peitsinä"),
    "ripsi": ("ripsenä", "ripsinä"),
    "rosvous": ("rosvouksena", "rosvoutena"),
    "saksi": ("saksena", "saksina"),
    "siitake": ("siitakena", "siitakkeena"),
    "siivous": ("siivouksena", "siivoutena"),
    "sini": ("sinenä", "sininä"),
    "sioux": ("sioux'na", "siouxina"),
    "syli": ("sylenä", "sylinä"),
    "uros": ("uroksena", "uroona"),
    "vakaus": ("vakauksena", "vakautena"),
    "viini": ("viinenä", "viininä"),
    "vuori": ("vuorena", "vuorina"),
    "vyyhti": ("vyyhtenä", "vyyhtinä"),

    # declension 1
    "valo": ("valona",),

    # declension 2
    "palvelu": ("palveluna",),

    # declension 3
    "valtio": ("valtiona",),

    # declension 4
    "laatikko": ("laatikkona",),

    # declension 5
    "lux": ("luxina",),
    "risti": ("ristinä",),
    "šakki": ("šakkina",),
    "self-made man": ("self-made manina",),
    "wok": ("wokina",),
    "vouti": ("voutina",),

    # declension 6
    "lumen": ("lumenina",),
    "paperi": ("paperina",),
    "weber": ("weberinä",),

    # declension 7
    "ovi": ("ovena",),

    # declension 8
    "nalle": ("nallena",),

    # declension 9
    "kala": ("kalana",),

    # declension 10
    "koira": ("koirana",),
    "kahdeksan": ("kahdeksana",),

    # declension 11
    "omena": ("omenana",),

    # declension 12
    "kulkija": ("kulkijana",),

    # declension 13
    "katiska": ("katiskana",),

    # declension 14
    "solakka": ("solakkana",),

    # declension 15
    "korkea": ("korkeana",),

    # declension 16
    "vanhempi": ("vanhempana",),

    # declension 17
    "vapaa": ("vapaana",),

    # declension 18
    "maa": ("maana",),

    # declension 19
    "suo": ("suona",),

    # declension 20
    "filee": ("fileenä",),

    # declension 21
    "rosé": ("roséna",),

    # declension 22
    "parfait": ("parfait'na",),

    # declension 23
    "tiili": ("tiilenä",),

    # declension 24
    "uni": ("unena",),

    # declension 25
    "toimi": ("toimena",),

    # declension 26
    "pieni": ("pienenä",),

    # declension 27
    "käsi": ("kätenä",),

    # declension 28
    "kynsi": ("kyntenä",),

    # declension 29
    "lapsi": ("lapsena",),

    # declension 30
    "veitsi": ("veitsenä",),

    # declension 31
    "kaksi": ("kahtena",),

    # declension 32
    "kymmenen": ("kymmenenä",),
    "sisar": ("sisarena",),
    "tytär": ("tyttärenä",),

    # declension 33
    "kytkin": ("kytkimenä",),
    "ydin": ("ytimenä",),

    # declension 34
    "onneton": ("onnettomana",),
    "yötön": ("yöttömänä",),

    # declension 35
    "lämmin": ("lämpimänä",),

    # declension 36
    "sisin": ("sisimpänä",),

    # declension 37
    "vasen": ("vasempana",),

    # declension 38
    "nainen": ("naisena",),

    # declension 39
    "vastaus": ("vastauksena",),

    # declension 40
    "kalleus": ("kalleutena",),

    # declension 41
    "vieras": ("vieraana",),
    "äes": ("äkeenä",),

    # declension 42
    "mies": ("miehenä",),

    # declension 43
    "immyt": ("impyenä",),
    "ohut": ("ohuena",),

    # declension 44
    "kevät": ("keväänä",),

    # declension 45
    "kahdeksas": ("kahdeksantena",),

    # declension 46
    "tuhat": ("tuhantena",),

    # declension 47
    "kuollut": ("kuolleena",),

    # declension 48
    "hame": ("hameena",),
    "vuode": ("vuoteena",),

    # declension 49
    "askel": ("askelena",),
    "askele": ("askeleena",),
    "säen": ("säkenenä",),
}

TESTS_ILL_SG = {
    # more than one declension (all)
    "ahtaus": ("ahtaukseen", "ahtauteen"),
    "alpi": ("alpeen", "alpiin"),
    "csárdás": ("csárdákseen", "csárdásiin"),
    "havas": ("hapaaseen", "havakseen"),
    "helpi": ("helpeen", "helpiin"),
    "kaihi": ("kaiheen", "kaihiin"),
    "kallas": ("kallakseen", "kaltaaseen"),
    "karhi": ("karheen", "karhiin"),
    "karvaus": ("karvaukseen", "karvauteen"),
    "koiras": ("koiraaseen", "koirakseen"),
    "kuori": ("kuoreen", "kuoriin"),
    "kuskus": ("kuskukseen", "kuskusiin"),
    "kuusi": ("kuuseen", "kuuteen"),
    "kymi": ("kymeen", "kymiin"),
    "kymmenes": ("kymmenekseen", "kymmenenteen"),
    "lahti": ("lahteen", "lahtiin"),
    "laki": ("lakeen", "lakiin"),
    "olas": ("olaaseen", "olakseen"),
    "ori": ("oriin", "oriiseen"),
    "pallas": ("pallakseen", "paltaaseen"),
    "palvi": ("palveen", "palviin"),
    "peitsi": ("peitseen", "peitsiin"),
    "ripsi": ("ripseen", "ripsiin"),
    "rosvous": ("rosvoukseen", "rosvouteen"),
    "saksi": ("sakseen", "saksiin"),
    "siitake": ("siitakeen", "siitakkeeseen"),
    "siivous": ("siivoukseen", "siivouteen"),
    "sini": ("sineen", "siniin"),
    "sioux": ("sioux'hun", "siouxiin"),
    "syli": ("syleen", "syliin"),
    "uros": ("urokseen", "urooseen"),
    "vakaus": ("vakaukseen", "vakauteen"),
    "viini": ("viineen", "viiniin"),
    "vuori": ("vuoreen", "vuoriin"),
    "vyyhti": ("vyyhteen", "vyyhtiin"),

    # declension 1
    "valo": ("valoon",),

    # declension 2
    "palvelu": ("palveluun",),

    # declension 3
    "valtio": ("valtioon",),

    # declension 4
    "laatikko": ("laatikkoon",),

    # declension 5
    "lux": ("luxiin",),
    "risti": ("ristiin",),
    "šakki": ("šakkiin",),
    "self-made man": ("self-made maniin",),
    "wok": ("wokiin",),
    "vouti": ("voutiin",),

    # declension 6
    "lumen": ("lumeniin",),
    "paperi": ("paperiin",),
    "weber": ("weberiin",),

    # declension 7
    "ovi": ("oveen",),

    # declension 8
    "nalle": ("nalleen",),

    # declension 9
    "kala": ("kalaan",),

    # declension 10
    "koira": ("koiraan",),
    "kahdeksan": ("kahdeksaan",),

    # declension 11
    "omena": ("omenaan",),

    # declension 12
    "kulkija": ("kulkijaan",),

    # declension 13
    "katiska": ("katiskaan",),

    # declension 14
    "solakka": ("solakkaan",),

    # declension 15
    "korkea": ("korkeaan",),

    # declension 16
    "vanhempi": ("vanhempaan",),

    # declension 17
    "vapaa": ("vapaaseen",),

    # declension 18
    "maa": ("maahan",),

    # declension 19
    "suo": ("suohon",),

    # declension 20
    "filee": ("fileehen", "fileeseen"),

    # declension 21
    "rosé": ("roséhen",),

    # declension 22
    "parfait": ("parfait'hen",),

    # declension 23
    "tiili": ("tiileen",),

    # declension 24
    "uni": ("uneen",),

    # declension 25
    "toimi": ("toimeen",),

    # declension 26
    "pieni": ("pieneen",),

    # declension 27
    "käsi": ("käteen",),

    # declension 28
    "kynsi": ("kynteen",),

    # declension 29
    "lapsi": ("lapseen",),

    # declension 30
    "veitsi": ("veitseen",),

    # declension 31
    "kaksi": ("kahteen",),

    # declension 32
    "kymmenen": ("kymmeneen",),
    "sisar": ("sisareen",),
    "tytär": ("tyttäreen",),

    # declension 33
    "kytkin": ("kytkimeen",),
    "ydin": ("ytimeen",),

    # declension 34
    "onneton": ("onnettomaan",),
    "yötön": ("yöttömään",),

    # declension 35
    "lämmin": ("lämpimään",),

    # declension 36
    "sisin": ("sisimpään",),

    # declension 37
    "vasen": ("vasempaan",),

    # declension 38
    "nainen": ("naiseen",),

    # declension 39
    "vastaus": ("vastaukseen",),

    # declension 40
    "kalleus": ("kalleuteen",),

    # declension 41
    "vieras": ("vieraaseen",),
    "äes": ("äkeeseen",),

    # declension 42
    "mies": ("mieheen",),

    # declension 43
    "immyt": ("impyeen",),
    "ohut": ("ohueen",),

    # declension 44
    "kevät": ("kevääseen",),

    # declension 45
    "kahdeksas": ("kahdeksanteen",),

    # declension 46
    "tuhat": ("tuhanteen",),

    # declension 47
    "kuollut": ("kuolleeseen",),

    # declension 48
    "hame": ("hameeseen",),
    "vuode": ("vuoteeseen",),

    # declension 49
    "askel": ("askeleen",),
    "askele": ("askeleeseen",),
    "säen": ("säkeneen",),
}

TESTS_PAR_SG = {
    # more than one declension (all)
    "ahtaus": ("ahtausta", "ahtautta"),
    "alpi": ("alpea", "alpia"),
    "csárdás": ("csárdásia", "csárdásta"),
    "havas": ("havasta",),
    "helpi": ("helpeä", "helpiä"),
    "kaihi": ("kaihea", "kaihia"),
    "kallas": ("kallasta",),
    "karhi": ("karhea", "karhia"),
    "karvaus": ("karvausta", "karvautta"),
    "koiras": ("koirasta",),
    "kuori": ("kuoria", "kuorta"),
    "kuskus": ("kuskusia", "kuskusta"),
    "kuusi": ("kuusta", "kuutta"),
    "kymi": ("kymeä", "kymiä"),
    "kymmenes": ("kymmenestä", "kymmenettä"),
    "lahti": ("lahtea", "lahtia"),
    "laki": ("lakea", "lakia"),
    "olas": ("olasta",),
    "ori": ("oria", "oritta"),
    "pallas": ("pallasta",),
    "palvi": ("palvea", "palvia"),
    "peitsi": ("peistä", "peitsiä"),
    "ripsi": ("ripseä", "ripsiä"),
    "rosvous": ("rosvousta", "rosvoutta"),
    "saksi": ("saksea", "saksia"),
    "siitake": ("siitakea", "siitaketta"),
    "siivous": ("siivousta", "siivoutta"),
    "sini": ("sineä", "siniä"),
    "sioux": ("sioux'ta", "siouxia"),
    "syli": ("syliä", "syltä"),
    "uros": ("urosta",),
    "vakaus": ("vakausta", "vakautta"),
    "viini": ("viiniä", "viintä"),
    "vuori": ("vuoria", "vuorta"),
    "vyyhti": ("vyyhteä", "vyyhtiä"),

    # declension 1
    "valo": ("valoa",),

    # declension 2
    "palvelu": ("palvelua",),

    # declension 3
    "valtio": ("valtiota",),

    # declension 4
    "laatikko": ("laatikkoa",),

    # declension 5
    "lux": ("luxia",),
    "risti": ("ristiä",),
    "šakki": ("šakkia",),
    "self-made man": ("self-made mania",),
    "wok": ("wokia",),
    "vouti": ("voutia",),

    # declension 6
    "lumen": ("lumenia",),
    "paperi": ("paperia",),
    "weber": ("weberiä",),

    # declension 7
    "ovi": ("ovea",),

    # declension 8
    "nalle": ("nallea",),

    # declension 9
    "kala": ("kalaa",),

    # declension 10
    "koira": ("koiraa",),
    "kahdeksan": ("kahdeksaa",),

    # declension 11
    "omena": ("omenaa",),

    # declension 12
    "kulkija": ("kulkijaa",),

    # declension 13
    "katiska": ("katiskaa",),

    # declension 14
    "solakka": ("solakkaa",),

    # declension 15
    "korkea": ("korkeaa", "korkeata"),

    # declension 16
    "vanhempi": ("vanhempaa",),

    # declension 17
    "vapaa": ("vapaata",),

    # declension 18
    "maa": ("maata",),

    # declension 19
    "suo": ("suota",),

    # declension 20
    "filee": ("fileetä",),

    # declension 21
    "rosé": ("roséta",),

    # declension 22
    "parfait": ("parfait'ta",),

    # declension 23
    "tiili": ("tiiltä",),

    # declension 24
    "uni": ("unta",),

    # declension 25
    "toimi": ("toimea", "tointa"),

    # declension 26
    "pieni": ("pientä",),

    # declension 27
    "käsi": ("kättä",),

    # declension 28
    "kynsi": ("kynttä",),

    # declension 29
    "lapsi": ("lasta",),

    # declension 30
    "veitsi": ("veistä",),

    # declension 31
    "kaksi": ("kahta",),

    # declension 32
    "kymmenen": ("kymmentä",),
    "sisar": ("sisarta",),
    "tytär": ("tytärtä",),

    # declension 33
    "kytkin": ("kytkintä",),
    "ydin": ("ydintä",),

    # declension 34
    "onneton": ("onnetonta",),
    "yötön": ("yötöntä",),

    # declension 35
    "lämmin": ("lämmintä",),

    # declension 36
    "sisin": ("sisintä",),

    # declension 37
    "vasen": ("vasempaa", "vasenta"),

    # declension 38
    "nainen": ("naista",),

    # declension 39
    "vastaus": ("vastausta",),

    # declension 40
    "kalleus": ("kalleutta",),

    # declension 41
    "vieras": ("vierasta",),
    "äes": ("äestä",),

    # declension 42
    "mies": ("miestä",),

    # declension 43
    "immyt": ("immyttä",),
    "ohut": ("ohutta",),

    # declension 44
    "kevät": ("kevättä",),

    # declension 45
    "kahdeksas": ("kahdeksatta",),

    # declension 46
    "tuhat": ("tuhatta",),

    # declension 47
    "kuollut": ("kuollutta",),

    # declension 48
    "hame": ("hametta",),
    "vuode": ("vuodetta",),

    # declension 49
    "askel": ("askelta",),
    "askele": ("askeletta",),
    "säen": ("säentä",),
}

def run_test(case, number, dict_):
    # compare output of decline_noun to dictionary
    # case: e.g. "gen"
    # number: e.g. "sg"
    # dict_: {NomSg: (inflected, ...), ...}

    for word in dict_:
        result = tuple(sorted(set(
            decline_noun.decline_noun_main(word, case, number)
        )))
        if result != dict_[word]:
            sys.exit("{}{} of {}: expected {}, got {}".format(
                case.title(),
                number.title(),
                word,
                "/".join(dict_[word]),
                "/".join(result),
            ))

def main():
    print("Testing decline_noun.py...")

    for (case, number, dict_) in (
        ("nom", "pl", TESTS_NOM_PL),
        ("gen", "sg", TESTS_GEN_SG),
        ("tra", "sg", TESTS_TRA_SG),
        ("ine", "sg", TESTS_INE_SG),
        ("ela", "sg", TESTS_ELA_SG),
        ("ade", "sg", TESTS_ADE_SG),
        ("abl", "sg", TESTS_ABL_SG),
        ("abe", "sg", TESTS_ABE_SG),
        ("ess", "sg", TESTS_ESS_SG),
        ("ill", "sg", TESTS_ILL_SG),
        ("par", "sg", TESTS_PAR_SG),
    ):
        print("Running test:", case.title() + number.title())
        run_test(case, number, dict_)
        print(f"Test passed.")
    print(f"All tests passed.")

main()
