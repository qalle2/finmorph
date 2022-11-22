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
    # more than one result (all)
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

    # Kotus 1
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

    # Kotus 2
    "palvelu": ("palvelun",),
    "väestö": ("väestön",),

    # Kotus 3
    "valtio": ("valtion",),
    "yhtiö": ("yhtiön",),

    # Kotus 4
    "laatikko": ("laatikon",),

    # Kotus 5
    "lux": ("luxin",),
    "risti": ("ristin",),
    "šakki": ("šakin",),
    "self-made man": ("self-made manin",),
    "wok": ("wokin",),
    "vouti": ("voudin",),

    # Kotus 6
    "lumen": ("lumenin",),
    "paperi": ("paperin",),
    "weber": ("weberin",),

    # Kotus 7
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

    # Kotus 8
    "jeppe": ("jepen",),
    "nalle": ("nallen",),
    "nukke": ("nuken",),

    # Kotus 9
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

    # Kotus 10
    "kahdeksan": ("kahdeksan",),
    "koira": ("koiran",),
    "nälkä": ("nälän",),
    "seitsemän": ("seitsemän",),
    "yhdeksän": ("yhdeksän",),
    "ylkä": ("yljän",),

    # Kotus 11
    "omena": ("omenan",),

    # Kotus 12
    "kulkija": ("kulkijan",),

    # Kotus 13
    "katiska": ("katiskan",),

    # Kotus 14
    "solakka": ("solakan",),

    # Kotus 15
    "korkea": ("korkean",),

    # Kotus 16
    "idempi": ("idemmän",),
    "vanhempi": ("vanhemman",),

    # Kotus 17
    "vapaa": ("vapaan",),

    # Kotus 18
    "maa": ("maan",),

    # Kotus 19
    "suo": ("suon",),

    # Kotus 20
    "filee": ("fileen",),

    # Kotus 21
    "rosé": ("rosén",),

    # Kotus 22
    "parfait": ("parfait'n",),

    # Kotus 23
    "tiili": ("tiilen",),

    # Kotus 24
    "uni": ("unen",),

    # Kotus 25
    "toimi": ("toimen",),

    # Kotus 26
    "pieni": ("pienen",),

    # Kotus 27
    "käsi": ("käden",),

    # Kotus 28 (all)
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

    # Kotus 29 (all)
    "hapsi": ("hapsen",),
    "lapsi": ("lapsen",),
    "uksi": ("uksen",),

    # Kotus 30 (all)
    "veitsi": ("veitsen",),

    # Kotus 31 (all)
    "haaksi": ("haahden",),
    "kaksi": ("kahden",),
    "yksi": ("yhden",),

    # Kotus 32
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

    # Kotus 33
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

    # Kotus 34
    "alaston": ("alastoman",),
    "onneton": ("onnettoman",),
    "yötön": ("yöttömän",),

    # Kotus 35 (all)
    "lämmin": ("lämpimän",),

    # Kotus 36
    "alin": ("alimman",),
    "sisin": ("sisimmän",),
    "uloin": ("uloimman",),

    # Kotus 37 (all)
    "vasen": ("vasemman",),

    # Kotus 38
    "nainen": ("naisen",),
    "osanen": ("osasen",),
    "öinen": ("öisen",),

    # Kotus 39
    "aines": ("aineksen",),
    "vastaus": ("vastauksen",),
    "varis": ("variksen",),
    "yritys": ("yrityksen",),

    # Kotus 40
    "kalleus": ("kalleuden",),
    "äreys": ("äreyden",),

    # Kotus 41
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

    # Kotus 42 (all)
    "mies": ("miehen",),

    # Kotus 43
    "immyt": ("impyen",),
    "ohut": ("ohuen",),

    # Kotus 44 (all)
    "kevät": ("kevään",),

    # Kotus 45
    "kahdeksas": ("kahdeksannen",),
    "neljäs": ("neljännen",),

    # Kotus 46 (all)
    "tuhat": ("tuhannen",),

    # Kotus 47
    "kuollut": ("kuolleen",),
    "tehnyt": ("tehneen",),

    # Kotus 48
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

    # Kotus 49 (all)
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
    ):
        print("Running test:", case.title() + number.title())
        run_test(case, number, dict_)
        print(f"Test passed.")
    print(f"All tests passed.")

main()
