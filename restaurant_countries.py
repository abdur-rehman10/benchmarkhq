"""
Restaurant & Food — Country Site Lists
========================================
Top restaurant chain websites per country.
Mix of fast food, casual dining, pizza, coffee, fast casual, and fine dining chains.
"""

COUNTRIES = {
    # ============ TIER 1: 30 sites each ============
    "usa": {
        "name": "United States",
        "sites": [
            "mcdonalds.com", "starbucks.com", "chipotle.com", "chickfila.com",
            "dominos.com", "pizzahut.com", "tacobell.com", "wendys.com",
            "burgerking.com", "subway.com", "dunkindonuts.com", "papajohns.com",
            "olivegarden.com", "applebees.com", "chillis.com", "ihop.com",
            "dennys.com", "outback.com", "buffalowildwings.com", "pandaexpress.com",
            "fiveguys.com", "jackinthebox.com", "sonicdriveins.com",
            "whataburger.com", "crackerbarrel.com", "cheesecakefactory.com",
            "sweetgreen.com", "shakeshack.com", "wingstop.com",
        ],
    },
    "uk": {
        "name": "United Kingdom",
        "sites": [
            "mcdonalds.com/gb", "starbucks.co.uk", "dominos.co.uk", "pizzahut.co.uk",
            "nandos.co.uk", "kfc.co.uk", "burgerking.co.uk", "greggs.co.uk",
            "wagamama.com", "francosmanca.co.uk", "zizzi.co.uk", "prezzo.co.uk",
            "itsu.com", "leonrestaurants.co.uk", "yo-sushi.com", "tgifridays.co.uk",
            "harvester.co.uk", "beefeater.co.uk", "toby-carvery.co.uk",
            "papajohns.co.uk", "subway.com/en-gb", "costacoffee.com",
            "pizzaexpress.com", "dishoom.com", "thegoodlife-eatery.com",
            "bfrankk.com", "honest-burgers.co.uk", "gourmetburger.co.uk",
            "byronhamburgers.com", "pret.com",
        ],
    },
    "india": {
        "name": "India",
        "sites": [
            "mcdonaldsindia.com", "dominos.co.in", "pizzahut.co.in", "kfc.co.in",
            "burgerking.in", "subway.com/en-in", "starbucks.in", "haldirams.com",
            "barbeque-nation.com", "saravanaabhavanrestaurants.com", "bikkgane.com",
            "socioffline.in", "faasos.com", "behrouz.com", "freshmenupak.com",
            "wow-momo.com", "chaipoint.com", "cafecoffeeday.com", "swiggy.com",
            "zomato.com", "biryaniblues.com", "paradisebiryani.com",
            "taco-bell.co.in", "dunkindonuts.co.in", "thebeerbistro.com",
            "mainland-china.co.in", "sigreerestaurant.com", "pind-balluchi.com",
            "nirulas.com", "naturalicecream.com",
        ],
    },
    "brazil": {
        "name": "Brazil",
        "sites": [
            "mcdonalds.com.br", "burgerking.com.br", "dominos.com.br", "pizzahut.com.br",
            "starbucks.com.br", "subway.com.br", "kfc.com.br", "bfrankk.com.br",
            "habibs.com.br", "giraffas.com.br", "bfrankk.com.br", "ifood.com.br",
            "madero.com.br", "outback.com.br", "tfrankk.com.br", "jeronimo-burger.com.br",
            "bobsburger.com.br", "coco-bambu.com.br", "parrilla.com.br",
            "ragazzo.com.br", "popeyes.com.br", "china-in-box.com.br",
            "spoleto.com.br", "bullguer.com.br", "lanchoneteformosa.com.br",
            "tacobell.com.br", "dunkin.com.br", "wendys.com.br",
            "papajohns.com.br", "pfrankk.com.br",
        ],
    },
    "germany": {
        "name": "Germany",
        "sites": [
            "mcdonalds.de", "burgerking.de", "dominos.de", "kfc.de",
            "subway.de", "starbucks.de", "dunkindonuts.de", "pizzahut.de",
            "vapiano.com", "hans-im-glueck.de", "peter-pane.de", "nordsee.com",
            "backwerk.de", "pottsalat.de", "block-house.de", "sausalitos.de",
            "leonrestaurants.de", "cotidiano.me", "ditsch.de", "yormas.de",
            "marinara.de", "freddy-schilling.de", "dean-david.de",
            "jim-block.de", "cinnabon.de", "five-guys.de",
            "pommes-freunde.de", "burgerme.de", "lieferheld.de", "wolt.com/de",
        ],
    },
    "france": {
        "name": "France",
        "sites": [
            "mcdonalds.fr", "burgerking.fr", "dominos.fr", "kfc.fr",
            "starbucks.fr", "subway.fr", "pizzahut.fr", "flfrankk.fr",
            "hippopotamus.fr", "courtepaille.com", "buffalogrill.fr", "leon.fr",
            "bagelsandcoffee.com", "class-croute.com", "pomme-de-pain.fr",
            "quick.fr", "briochedoree.fr", "paulboulangerie.com", "lardoise.fr",
            "bagelstein.com", "five-guys.fr", "bigfernand.com", "popeyes.fr",
            "pfrankk.fr", "tacobell.fr", "pitayafood.com", "nachos.fr",
            "fufu.fr", "eataly.net/fr", "flunch.fr",
        ],
    },
    "china": {
        "name": "China",
        "sites": [
            "mcdonalds.com.cn", "kfc.com.cn", "starbucks.com.cn", "pizzahut.com.cn",
            "burgerking.com.cn", "subway.com.cn", "dominos.com.cn", "dfrankk.com.cn",
            "haidilao.com", "xibei.com", "yum.com.cn", "luckin.cn",
            "tianyanchafen.com", "dicos.com.cn", "kungfurestaurant.com",
            "ajisen.com.cn", "wanghong.com", "sfrankk.com",
            "shaxian.com", "dangui.com", "heytea.com",
            "nayuki.cn", "coco-tea.com", "mixue.com.cn",
            "tastien.com", "juewei.com", "zhengxin.com.cn",
            "jibiya.com", "mxbc.com", "eleme.cn",
        ],
    },
    "japan": {
        "name": "Japan",
        "sites": [
            "mcdonalds.co.jp", "starbucks.co.jp", "kfc.co.jp", "dominos.co.jp",
            "pizzahut.jp", "subway.co.jp", "burgerking.co.jp", "mos.jp",
            "yoshinoya.com", "matsuya-group.com", "sukiya.jp", "saizeriya.co.jp",
            "skylark.co.jp", "dennys.jp", "coco-curry.com", "tenya.co.jp",
            "gyukaku.ne.jp", "genki-sushi.co.jp", "kappazushi.jp",
            "ichibanya.co.jp", "freshnessburger.co.jp", "lotteriaburger.co.jp",
            "first-kitchen.co.jp", "wendysfirstkitchen.co.jp", "komeda.co.jp",
            "tullys.co.jp", "doutor.co.jp", "pronto.co.jp",
            "misterdonut.jp", "gindaco.com",
        ],
    },
    "saudi_arabia": {
        "name": "Saudi Arabia",
        "sites": [
            "mcdonalds.com.sa", "kfc.com.sa", "dominos.com.sa", "pizzahut.com.sa",
            "starbucks.com.sa", "burgerking.com.sa", "subway.com.sa", "hardees.com.sa",
            "albaik.com", "kudu.com.sa", "herfy.com", "maestropizza.com",
            "shawarmer.com", "aldawali.com.sa", "almarsam.com", "tazaj.com",
            "littlecaesars.com.sa", "papajohns.com.sa", "popeyes.com.sa",
            "dunkin.com.sa", "baskinrobbins.com.sa", "tacobell.com.sa",
            "wfrankk.com.sa", "jollibee.com.sa", "chophouse.com.sa",
            "saltbae.com", "shakeshack.com.sa", "fiveguys.com.sa",
            "caribou-coffee.com.sa", "timhortons.com.sa",
        ],
    },
    "australia": {
        "name": "Australia",
        "sites": [
            "mcdonalds.com.au", "kfc.com.au", "dominos.com.au", "pizzahut.com.au",
            "starbucks.com.au", "subway.com.au", "burgerking.com.au", "nandos.com.au",
            "grilld.com.au", "hungryjacks.com.au", "redrooster.com.au", "oporto.com.au",
            "zambreros.com.au", "guzmanygomez.com.au", "bfrankk.com.au",
            "madmex.com.au", "tfrankk.com.au", "salsas.com.au",
            "betty-burger.com.au", "pancakeplace.com.au", "papparich.net.au",
            "guzmanygomez.com.au", "gloriasjeans.com.au", "soulgrill.com.au",
            "boost.com.au", "chatime.com.au", "donut-king.com.au",
            "muffin-break.com.au", "thecheesecakeshop.com.au", "rashays.com.au",
        ],
    },

    # ============ TIER 2: 10 sites each ============
    "mexico": {"name": "Mexico", "sites": [
        "mcdonalds.com.mx", "dominos.com.mx", "starbucks.com.mx", "burgerking.com.mx",
        "kfc.com.mx", "subway.com.mx", "littlecaesars.com.mx", "carls-jr.com.mx",
        "vfrankk.com.mx", "elportoncito.com.mx",
    ]},
    "turkey": {"name": "Turkiye", "sites": [
        "mcdonalds.com.tr", "dominos.com.tr", "kfc.com.tr", "burgerking.com.tr",
        "starbucks.com.tr", "subway.com.tr", "popeyes.com.tr", "simit-sarayi.com",
        "bayraklitantuni.com", "komagene.com.tr",
    ]},
    "south_korea": {"name": "South Korea", "sites": [
        "mcdonalds.co.kr", "dominos.co.kr", "kfc.co.kr", "burgerking.co.kr",
        "starbucks.co.kr", "subway.co.kr", "pizzahut.co.kr", "bbq.co.kr",
        "kyochon.com", "lotteeatz.com",
    ]},
    "italy": {"name": "Italy", "sites": [
        "mcdonalds.it", "dominos.it", "burgerking.it", "starbucks.it",
        "kfc.it", "subway.it", "pizzahut.it", "eataly.net",
        "rossopomodoro.com", "autogrill.com",
    ]},
    "spain": {"name": "Spain", "sites": [
        "mcdonalds.es", "dominos.es", "burgerking.es", "kfc.es",
        "starbucks.es", "subway.es", "telepizza.es", "papajohns.es",
        "vfrankk.es", "100montaditos.com",
    ]},
    "canada": {"name": "Canada", "sites": [
        "mcdonalds.com/ca", "timhortons.com", "dominos.ca", "starbucks.ca",
        "burgerking.ca", "kfc.ca", "subway.com/en-ca", "pizzahut.ca",
        "harveys.ca", "boosterjuice.com",
    ]},
    "uae": {"name": "UAE", "sites": [
        "mcdonalds.com/ae", "kfc.ae", "dominos.ae", "pizzahut.ae",
        "starbucks.ae", "burgerking.ae", "subway.ae", "shakeshack.ae",
        "timhortons.ae", "albaik.com/ae",
    ]},
    "indonesia": {"name": "Indonesia", "sites": [
        "mcdonalds.co.id", "kfc.co.id", "dominos.co.id", "pizzahut.co.id",
        "starbucks.co.id", "burgerking.co.id", "hokben.co.id", "jfrankk.co.id",
        "richeese-factory.com", "marugame-seimen.co.id",
    ]},
    "thailand": {"name": "Thailand", "sites": [
        "mcdonalds.co.th", "kfc.co.th", "dominos.co.th", "pizzahut.co.th",
        "starbucks.co.th", "burgerking.co.th", "minormak.com", "mkrestaurant.com",
        "1112delivery.com", "shabushi.com",
    ]},
    "nigeria": {"name": "Nigeria", "sites": [
        "kfc.com.ng", "dominos.com.ng", "pizzahut.com.ng", "subway.com.ng",
        "chickrepublic.com", "tantalizers.com", "kilimanjaro-restaurant.com",
        "mrbiggs.com.ng", "coldstone.com.ng", "barcelos.com.ng",
    ]},
    "egypt": {"name": "Egypt", "sites": [
        "mcdonalds.com.eg", "kfc.com.eg", "dominos.com.eg", "pizzahut.com.eg",
        "starbucks.eg", "hardees.com.eg", "buffalowings.com.eg",
        "cookdoor.com", "sobhy-kaber.com", "gad.com.eg",
    ]},
    "pakistan": {"name": "Pakistan", "sites": [
        "mcdonalds.com.pk", "kfc.com.pk", "dominos.com.pk", "pizzahut.com.pk",
        "subway.com.pk", "hardees.com.pk", "broadwaypizza.com.pk",
        "howdy.pk", "optp.com.pk", "lfrankk.com.pk",
    ]},
    "south_africa": {"name": "South Africa", "sites": [
        "mcdonalds.co.za", "kfc.co.za", "dominos.co.za", "nandos.co.za",
        "steers.co.za", "debonairs.co.za", "rocomamas.co.za",
        "wimpy.co.za", "fishaways.co.za", "pizzahut.co.za",
    ]},
    "russia": {"name": "Russia", "sites": [
        "vkusnoitochka.ru", "kfc.ru", "dfrankk.ru", "burgerking.ru",
        "subway.ru", "dodo.ru", "papajohns.ru", "yakitoriya.ru",
        "shokoladnitsa.ru", "coffeelike.ru",
    ]},
    "poland": {"name": "Poland", "sites": [
        "mcdonalds.pl", "kfc.pl", "dominos.pl", "burgerking.pl",
        "starbucks.pl", "subway.pl", "pizzahut.pl", "sfrankk.pl",
        "amrest.pl", "sphinx.pl",
    ]},
}

# Print summary
tier1 = {k:v for k,v in COUNTRIES.items() if len(v["sites"]) >= 30}
tier2 = {k:v for k,v in COUNTRIES.items() if len(v["sites"]) < 30}
total_sites = sum(len(v["sites"]) for v in COUNTRIES.values())
print(f"Tier 1 countries: {len(tier1)} ({30} sites each)")
print(f"Tier 2 countries: {len(tier2)} ({10} sites each)")
print(f"Total countries: {len(COUNTRIES)}")
print(f"Total sites: {total_sites}")
