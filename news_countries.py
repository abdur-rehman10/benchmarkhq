"""
BenchmarkHQ — News & Media Site Lists
160 countries, ~1,860 websites
Tier 1: 13 big countries × 30 sites = 390
Tier 2: 147 countries × 10 sites = 1,470
"""

# Tier 1 countries get 30 sites each
TIER1_COUNTRIES = {
    "usa": {
        "name": "United States", "language": "en", "region": "North America",
        "sites": [
            # Major newspapers
            "nytimes.com", "washingtonpost.com", "wsj.com", "usatoday.com", "latimes.com",
            "chicagotribune.com", "nypost.com", "bostonglobe.com", "sfchronicle.com", "dallasnews.com",
            # TV/Broadcast
            "cnn.com", "foxnews.com", "nbcnews.com", "abcnews.go.com", "cbsnews.com",
            "msnbc.com", "pbs.org/newshour",
            # Digital-native
            "axios.com", "politico.com", "thehill.com", "vox.com", "buzzfeednews.com",
            "huffpost.com", "thedailybeast.com", "slate.com",
            # Business/Finance
            "bloomberg.com", "cnbc.com", "fortune.com", "businessinsider.com",
            # Tech/Magazine
            "wired.com",
        ]
    },
    "uk": {
        "name": "United Kingdom", "language": "en", "region": "Europe",
        "sites": [
            "bbc.co.uk/news", "theguardian.com", "telegraph.co.uk", "thetimes.co.uk", "independent.co.uk",
            "dailymail.co.uk", "mirror.co.uk", "express.co.uk", "thesun.co.uk", "standard.co.uk",
            "ft.com", "economist.com", "newstatesman.com", "spectator.co.uk", "theweek.co.uk",
            "sky.com/news", "itv.com/news", "channel4.com/news", "lbc.co.uk", "inews.co.uk",
            "metro.co.uk", "cityam.com", "scotsman.com", "walesonline.co.uk", "belfasttelegraph.co.uk",
            "manchestereveningnews.co.uk", "birminghammail.co.uk", "bristolpost.co.uk",
            "buzzfeed.com/uk", "joe.co.uk",
        ]
    },
    "canada": {
        "name": "Canada", "language": "en", "region": "North America",
        "sites": [
            "cbc.ca/news", "globalnews.ca", "thestar.com", "theglobeandmail.com", "nationalpost.com",
            "ctv.ca/news", "cp24.com", "montrealgazette.com", "vancouversun.com", "ottawacitizen.com",
            "calgaryherald.com", "edmontonjournal.com", "winnipegfreepress.com", "thechronicleherald.ca", "ledevoir.com",
            "lapresse.ca", "journaldemontreal.com", "ici.radio-canada.ca", "macleans.ca", "thewalrus.ca",
            "narcity.com", "dailyhive.com", "blogto.com", "the-peak.ca", "canadaland.com",
            "ipolitics.ca", "thelogic.co", "bnnbloomberg.ca", "financialpost.com", "rabble.ca",
        ]
    },
    "australia": {
        "name": "Australia", "language": "en", "region": "Oceania",
        "sites": [
            "abc.net.au/news", "news.com.au", "smh.com.au", "theaustralian.com.au", "9news.com.au",
            "7news.com.au", "sbs.com.au/news", "theage.com.au", "brisbanetimes.com.au", "watoday.com.au",
            "canberratimes.com.au", "dailytelegraph.com.au", "heraldsun.com.au", "couriermail.com.au", "adelaidenow.com.au",
            "theguardian.com/au", "crikey.com.au", "theconversation.com", "pedestrian.tv", "junkee.com",
            "skynews.com.au", "afr.com", "businessnews.com.au", "newdaily.com.au", "michaelwest.com.au",
            "perthnow.com.au", "ntnews.com.au", "examiner.com.au", "geelongadvertiser.com.au", "dailymail.co.uk/auhome",
        ]
    },
    "france": {
        "name": "France", "language": "fr", "region": "Europe",
        "sites": [
            "lemonde.fr", "lefigaro.fr", "liberation.fr", "leparisien.fr", "lesechos.fr",
            "latribune.fr", "lexpress.fr", "lepoint.fr", "nouvelobs.com", "marianne.net",
            "france24.com/fr", "francetvinfo.fr", "bfmtv.com", "lci.fr", "cnews.fr",
            "rfi.fr", "arte.tv/fr", "europe1.fr", "rtl.fr", "franceinter.fr",
            "mediapart.fr", "slate.fr", "huffingtonpost.fr", "konbini.com", "brut.media",
            "ouest-france.fr", "sudouest.fr", "lavoixdunord.fr", "leprogres.fr", "dna.fr",
        ]
    },
    "germany": {
        "name": "Germany", "language": "de", "region": "Europe",
        "sites": [
            "spiegel.de", "bild.de", "faz.net", "sueddeutsche.de", "welt.de",
            "zeit.de", "stern.de", "focus.de", "handelsblatt.com", "tagesschau.de",
            "zdf.de/nachrichten", "n-tv.de", "t-online.de", "tagesspiegel.de", "taz.de",
            "berliner-zeitung.de", "rp-online.de", "haz.de", "stuttgarter-zeitung.de", "ksta.de",
            "netzpolitik.org", "golem.de", "heise.de", "manager-magazin.de", "wiwo.de",
            "deutschlandfunk.de", "br.de", "ndr.de", "mdr.de", "merkur.de",
        ]
    },
    "india": {
        "name": "India", "language": "en", "region": "South Asia",
        "sites": [
            "timesofindia.indiatimes.com", "hindustantimes.com", "indianexpress.com", "thehindu.com", "ndtv.com",
            "news18.com", "indiatoday.in", "livemint.com", "business-standard.com", "economictimes.indiatimes.com",
            "scroll.in", "thewire.in", "newslaundry.com", "firstpost.com", "moneycontrol.com",
            "zeenews.india.com", "aajtak.in", "republic.com", "theprint.in", "swarajyamag.com",
            "deccanherald.com", "telegraphindia.com", "tribuneindia.com", "newindianexpress.com", "outlookindia.com",
            "thequint.com", "thebetterindia.com", "yourstory.com", "medianama.com", "caravandaily.com",
        ]
    },
    "china": {
        "name": "China", "language": "zh", "region": "East Asia",
        "sites": [
            "people.com.cn", "xinhuanet.com", "chinadaily.com.cn", "globaltimes.cn", "scmp.com",
            "cctv.com", "caixin.com", "yicai.com", "thepaper.cn", "36kr.com",
            "163.com/news", "news.sina.com.cn", "news.qq.com", "news.sohu.com", "ifeng.com",
            "bjnews.com.cn", "infzm.com", "jiemian.com", "huxiu.com", "guancha.cn",
            "cn.nikkei.com", "ftchinese.com", "bbc.com/zhongwen", "dw.com/zh", "rfi.fr/cn",
            "zaobao.com.sg", "nbd.com.cn", "cls.cn", "stcn.com", "ynet.com",
        ]
    },
    "russia": {
        "name": "Russia", "language": "ru", "region": "Eastern Europe",
        "sites": [
            "tass.ru", "ria.ru", "rbc.ru", "lenta.ru", "gazeta.ru",
            "rt.com", "kommersant.ru", "vedomosti.ru", "iz.ru", "mk.ru",
            "kp.ru", "aif.ru", "novayagazeta.eu", "meduza.io", "thebell.io",
            "fontanka.ru", "ngs.ru", "e1.ru", "74.ru", "nn.ru",
            "bfm.ru", "forbes.ru", "snob.ru", "theins.ru", "mediazona.ca",
            "russianrt.com", "vesti.ru", "ntv.ru", "echo.msk.ru", "znak.com",
        ]
    },
    "saudi_arabia": {
        "name": "Saudi Arabia", "language": "ar", "region": "Middle East",
        "sites": [
            "alarabiya.net", "aleqt.com", "okaz.com.sa", "alriyadh.com", "aawsat.com",
            "sabq.org", "ajel.sa", "al-jazirah.com", "alwatan.com.sa", "almadinah.com",
            "arabnews.com", "saudigazette.com.sa", "spa.gov.sa", "argaam.com", "maaal.com",
            "thenationalnews.com", "middleeasteye.net", "aljazeera.net", "bbc.com/arabic", "skynewsarabia.com",
            "france24.com/ar", "dw.com/ar", "arabic.rt.com", "cnbcarabia.com", "asharqbusiness.com",
            "independentarabia.com", "alquds.co.uk", "arabi21.com", "sasapost.com", "raseef22.net",
        ]
    },
    "iran": {
        "name": "Iran", "language": "fa", "region": "Middle East",
        "sites": [
            "irna.ir", "isna.ir", "tasnimnews.com", "farsnews.ir", "mehrnews.com",
            "khabaronline.ir", "tabnak.ir", "mashreghnews.ir", "yjc.ir", "entekhab.ir",
            "bbc.com/persian", "radiofarda.com", "iranintl.com", "manoto1.com", "voanews.com/persian",
            "dw.com/fa", "iranwire.com", "zeitoons.com", "sharghDaily.ir", "hamshahriOnline.ir",
            "jamejamonline.ir", "etemadonline.com", "donya-e-eqtesad.com", "eghtesadnews.com", "tejarat-news.com",
            "digiato.com", "zoomit.ir", "varzesh3.com", "90tv.ir", "aftabnews.ir",
        ]
    },
    "poland": {
        "name": "Poland", "language": "pl", "region": "Europe",
        "sites": [
            "gazeta.pl", "wp.pl", "onet.pl", "interia.pl", "tvn24.pl",
            "polsatnews.pl", "tvp.info", "rmf24.pl", "tokfm.pl", "rp.pl",
            "wyborcza.pl", "dziennik.pl", "fakt.pl", "se.pl", "newsweek.pl",
            "polityka.pl", "tygodnikpowszechny.pl", "wprost.pl", "dorzeczy.pl", "natemat.pl",
            "oko.press", "krytykapolityczna.pl", "spidersweb.pl", "niebezpiecznik.pl", "money.pl",
            "bankier.pl", "pulshr.pl", "gazetaprawna.pl", "forsal.pl", "wirtualnemedia.pl",
        ]
    },
    "new_zealand": {
        "name": "New Zealand", "language": "en", "region": "Oceania",
        "sites": [
            "rnz.co.nz", "nzherald.co.nz", "stuff.co.nz", "1news.co.nz", "newshub.co.nz",
            "newsroom.co.nz", "interest.co.nz", "thespinoff.co.nz", "noted.co.nz", "scoop.co.nz",
            "odt.co.nz", "waikatonews.co.nz", "bayofplentytimes.co.nz", "nzgeographic.co.nz", "listener.co.nz",
            "businessdesk.co.nz", "nbr.co.nz", "idealog.co.nz", "techblog.nz", "pundit.co.nz",
            "thepost.co.nz", "press.co.nz", "manawatūstandard.co.nz", "timaru.herald.co.nz", "greymouth.star.co.nz",
            "crux.org.nz", "localmatters.co.nz", "e-tangata.co.nz", "thebigidea.nz", "accessnz.co.nz",
        ]
    },
}

# Tier 2 countries: 10 sites each (5 major news + 5 blog/independent)
TIER2_COUNTRIES = {
    # ===== EUROPE =====
    "spain": {"name": "Spain", "language": "es", "region": "Europe", "sites": [
        "elpais.com", "elmundo.es", "abc.es", "lavanguardia.com", "elconfidencial.com",
        "eldiario.es", "publico.es", "20minutos.es", "lainformacion.com", "maldita.es"]},
    "italy": {"name": "Italy", "language": "it", "region": "Europe", "sites": [
        "corriere.it", "repubblica.it", "lastampa.it", "ansa.it", "ilsole24ore.com",
        "fanpage.it", "ilpost.it", "open.online", "wired.it", "internazionale.it"]},
    "netherlands": {"name": "Netherlands", "language": "nl", "region": "Europe", "sites": [
        "nos.nl", "nu.nl", "ad.nl", "volkskrant.nl", "nrc.nl",
        "rtlnieuws.nl", "trouw.nl", "telegraaf.nl", "parool.nl", "decorrespondent.nl"]},
    "belgium": {"name": "Belgium", "language": "nl", "region": "Europe", "sites": [
        "vrt.be/vrtnws", "hln.be", "standaard.be", "demorgen.be", "nieuwsblad.be",
        "rtbf.be", "lesoir.be", "lalibre.be", "knack.be", "apache.be"]},
    "switzerland": {"name": "Switzerland", "language": "de", "region": "Europe", "sites": [
        "nzz.ch", "srf.ch", "blick.ch", "tagesanzeiger.ch", "20min.ch",
        "swissinfo.ch", "watson.ch", "rts.ch", "tdg.ch", "republik.ch"]},
    "austria": {"name": "Austria", "language": "de", "region": "Europe", "sites": [
        "orf.at", "derstandard.at", "diepresse.com", "kurier.at", "krone.at",
        "oe24.at", "wienerzeitung.at", "profil.at", "falter.at", "addendum.org"]},
    "sweden": {"name": "Sweden", "language": "sv", "region": "Europe", "sites": [
        "svt.se", "dn.se", "svd.se", "aftonbladet.se", "expressen.se",
        "sr.se", "gp.se", "sydsvenskan.se", "di.se", "breakit.se"]},
    "norway": {"name": "Norway", "language": "no", "region": "Europe", "sites": [
        "nrk.no", "vg.no", "dagbladet.no", "aftenposten.no", "nettavisen.no",
        "tv2.no", "bt.no", "dn.no", "e24.no", "filter.no"]},
    "denmark": {"name": "Denmark", "language": "da", "region": "Europe", "sites": [
        "dr.dk", "politiken.dk", "berlingske.dk", "jyllands-posten.dk", "bt.dk",
        "ekstrabladet.dk", "tv2.dk", "borsen.dk", "information.dk", "zetland.dk"]},
    "finland": {"name": "Finland", "language": "fi", "region": "Europe", "sites": [
        "yle.fi", "hs.fi", "is.fi", "iltalehti.fi", "kauppalehti.fi",
        "mtv.fi/uutiset", "ts.fi", "kaleva.fi", "keskisuomalainen.fi", "longplay.fi"]},
    "portugal": {"name": "Portugal", "language": "pt", "region": "Europe", "sites": [
        "publico.pt", "dn.pt", "jn.pt", "observador.pt", "expresso.pt",
        "rtp.pt", "tsf.pt", "sapo.pt/noticias", "sol.sapo.pt", "eco.sapo.pt"]},
    "ireland": {"name": "Ireland", "language": "en", "region": "Europe", "sites": [
        "rte.ie/news", "irishtimes.com", "independent.ie", "irishexaminer.com", "thejournal.ie",
        "breakingnews.ie", "newstalk.com", "joe.ie", "businesspost.ie", "hotpress.com"]},
    "czech_republic": {"name": "Czech Republic", "language": "cs", "region": "Europe", "sites": [
        "ct24.cz", "seznam.cz/zpravy", "novinky.cz", "idnes.cz", "aktualne.cz",
        "irozhlas.cz", "lidovky.cz", "denik.cz", "e15.cz", "denikn.cz"]},
    "hungary": {"name": "Hungary", "language": "hu", "region": "Europe", "sites": [
        "index.hu", "hvg.hu", "origo.hu", "444.hu", "telex.hu",
        "24.hu", "portfolio.hu", "rtl.hu/rtlklub/hirek", "nepszava.hu", "atlatszo.hu"]},
    "romania": {"name": "Romania", "language": "ro", "region": "Europe", "sites": [
        "digi24.ro", "hotnews.ro", "mediafax.ro", "adevarul.ro", "libertatea.ro",
        "stirileprotv.ro", "g4media.ro", "ziare.com", "profit.ro", "pressone.ro"]},
    "greece": {"name": "Greece", "language": "el", "region": "Europe", "sites": [
        "kathimerini.gr", "in.gr", "protothema.gr", "iefimerida.gr", "news247.gr",
        "ert.gr", "naftemporiki.gr", "liberal.gr", "tpp.gr", "thepressproject.gr"]},
    "ukraine": {"name": "Ukraine", "language": "uk", "region": "Europe", "sites": [
        "pravda.com.ua", "unian.net", "ukrinform.net", "liga.net", "nv.ua",
        "suspilne.media", "bbc.com/ukrainian", "hromadske.ua", "zn.ua", "texty.org.ua"]},
    "turkiye": {"name": "Turkiye", "language": "tr", "region": "Europe/Asia", "sites": [
        "hurriyet.com.tr", "milliyet.com.tr", "sabah.com.tr", "haberturk.com", "ntv.com.tr",
        "bbc.com/turkce", "dw.com/tr", "t24.com.tr", "bianet.org", "medyascope.tv"]},
    "serbia": {"name": "Serbia", "language": "sr", "region": "Europe", "sites": [
        "rts.rs", "blic.rs", "b92.net", "n1info.rs", "danas.rs",
        "kurir.rs", "nova.rs", "insajder.net", "balkaninsight.com", "cenzolovka.rs"]},
    "croatia": {"name": "Croatia", "language": "hr", "region": "Europe", "sites": [
        "hrt.hr", "index.hr", "jutarnji.hr", "vecernji.hr", "net.hr",
        "tportal.hr", "telegram.hr", "dnevnik.hr", "slobodnadalmacija.hr", "h-alter.org"]},
    "bulgaria": {"name": "Bulgaria", "language": "bg", "region": "Europe", "sites": [
        "bnt.bg", "btvnovinite.bg", "dnevnik.bg", "capital.bg", "mediapool.bg",
        "24chasa.bg", "offnews.bg", "bivol.bg", "clubz.bg", "segabg.com"]},
    "slovakia": {"name": "Slovakia", "language": "sk", "region": "Europe", "sites": [
        "rtvs.sk", "sme.sk", "dennikn.sk", "aktuality.sk", "pravda.sk",
        "hnonline.sk", "teraz.sk", "startitup.sk", "refresher.sk", "trend.sk"]},
    "slovenia": {"name": "Slovenia", "language": "sl", "region": "Europe", "sites": [
        "rtvslo.si", "delo.si", "24ur.com", "dnevnik.si", "vecer.com",
        "siol.net", "necenzurirano.si", "mladina.si", "podcrto.si", "n1info.si"]},
    "lithuania": {"name": "Lithuania", "language": "lt", "region": "Europe", "sites": [
        "lrt.lt", "delfi.lt", "15min.lt", "vz.lt", "lrytas.lt",
        "bernardinai.lt", "alfa.lt", "tv3.lt", "kauno.diena.lt", "sirenos.lt"]},
    "latvia": {"name": "Latvia", "language": "lv", "region": "Europe", "sites": [
        "lsm.lv", "delfi.lv", "tvnet.lv", "diena.lv", "nra.lv",
        "jauns.lv", "db.lv", "apollo.lv", "la.lv", "rebaltica.lv"]},
    "estonia": {"name": "Estonia", "language": "et", "region": "Europe", "sites": [
        "err.ee", "postimees.ee", "delfi.ee", "aripaev.ee", "epl.ee",
        "ohtuleht.ee", "maaleht.ee", "geenius.ee", "forte.delfi.ee", "propastop.org"]},
    "iceland": {"name": "Iceland", "language": "is", "region": "Europe", "sites": [
        "ruv.is", "visir.is", "mbl.is", "frettabladid.is", "dv.is",
        "stundin.is", "kjarninn.is", "heimildin.is", "kvennabladid.is", "grapevine.is"]},
    "malta": {"name": "Malta", "language": "en", "region": "Europe", "sites": [
        "timesofmalta.com", "maltatoday.com.mt", "tvm.com.mt", "independent.com.mt", "newsbook.com.mt",
        "one.com.mt", "lovinmalta.com", "guideme.com.mt", "maltachamber.org.mt", "theshiftnews.com"]},
    "cyprus": {"name": "Cyprus", "language": "el", "region": "Europe", "sites": [
        "sigmalive.com", "philenews.com", "politis.com.cy", "stockwatch.com.cy", "dialogos.com.cy",
        "reporter.com.cy", "inbusiness.com.cy", "cyprus-mail.com", "knews.kathimerini.com.cy", "brief.com.cy"]},
    "luxembourg": {"name": "Luxembourg", "language": "fr", "region": "Europe", "sites": [
        "wort.lu", "rtl.lu", "lequotidien.lu", "tageblatt.lu", "reporter.lu",
        "paperjam.lu", "delano.lu", "chronicle.lu", "land.lu", "journal.lu"]},
    "albania": {"name": "Albania", "language": "sq", "region": "Europe", "sites": [
        "top-channel.tv", "shqiptarja.com", "panorama.com.al", "exit.al", "reporter.al",
        "gazetadita.al", "balkanweb.com", "a2news.com", "dritare.net", "birn.eu.com"]},
    "north_macedonia": {"name": "North Macedonia", "language": "mk", "region": "Europe", "sites": [
        "mrt.com.mk", "sdk.mk", "meta.mk", "slobodenpecat.mk", "a1on.mk",
        "plusinfo.mk", "alsat.mk", "nova.mk", "prizma.mk", "truthmeter.mk"]},
    "bosnia": {"name": "Bosnia & Herzegovina", "language": "bs", "region": "Europe", "sites": [
        "klix.ba", "avaz.ba", "oslobodjenje.ba", "n1info.ba", "fena.ba",
        "radiosarajevo.ba", "bljesak.info", "zurnal.info", "capital.ba", "mediacentar.info"]},
    "montenegro": {"name": "Montenegro", "language": "sr", "region": "Europe", "sites": [
        "rtcg.me", "vijesti.me", "dan.co.me", "pobjeda.me", "in4s.net",
        "cdm.me", "cafe.me", "borba.me", "mina.news", "monitor.co.me"]},
    "kosovo": {"name": "Kosovo", "language": "sq", "region": "Europe", "sites": [
        "rtklive.com", "koha.net", "telegrafi.com", "gazetaexpress.com", "kallxo.com",
        "insajderi.com", "kosovapress.com", "botasot.info", "gazetablic.com", "preportr.com"]},
    "moldova": {"name": "Moldova", "language": "ro", "region": "Europe", "sites": [
        "trm.md", "moldpres.md", "newsmaker.md", "zdg.md", "deschide.md",
        "protv.md", "jurnal.md", "point.md", "noi.md", "anticoruptie.md"]},
    "georgia": {"name": "Georgia", "language": "ka", "region": "Europe/Asia", "sites": [
        "1tv.ge", "civil.ge", "tabula.ge", "formulanews.ge", "publika.ge",
        "netgazeti.ge", "sova.news", "mtavari.tv", "bm.ge", "imedinews.ge"]},
    "armenia": {"name": "Armenia", "language": "hy", "region": "Europe/Asia", "sites": [
        "1lurer.am", "armenpress.am", "azatutyun.am", "civilnet.am", "hetq.am",
        "mediamax.am", "news.am", "panorama.am", "evn.report", "mirrorspectator.com"]},
    "azerbaijan": {"name": "Azerbaijan", "language": "az", "region": "Europe/Asia", "sites": [
        "aztv.az", "apa.az", "trend.az", "report.az", "oxu.az",
        "meydan.tv", "bbc.com/azeri", "toplum.tv", "turan.az", "abzas.net"]},
    "belarus": {"name": "Belarus", "language": "be", "region": "Europe", "sites": [
        "belta.by", "tut.by", "nn.by", "svaboda.org", "zerkalo.io",
        "kyky.org", "dev.by", "reform.by", "belsat.eu", "mediazona.by"]},

    # ===== MIDDLE EAST =====
    "uae": {"name": "United Arab Emirates", "language": "ar", "region": "Middle East", "sites": [
        "thenationalnews.com", "gulfnews.com", "khaleejtimes.com", "arabianbusiness.com", "emaratalyoum.com",
        "albayan.ae", "alittihad.ae", "zawya.com", "alarabiya.net/uae", "lovin.co/dubai"]},
    "qatar": {"name": "Qatar", "language": "ar", "region": "Middle East", "sites": [
        "aljazeera.net", "alarab.qa", "thepeninsulaqatar.com", "gulf-times.com", "qna.org.qa",
        "al-sharq.com", "raya.com", "lusail.qa", "dohanews.co", "iloveqatar.net"]},
    "kuwait": {"name": "Kuwait", "language": "ar", "region": "Middle East", "sites": [
        "kuna.net.kw", "alqabas.com", "annahar.com/arabic", "alraimedia.com", "aljarida.com",
        "arabtimesonline.com", "kuwaittimes.com", "alaan.tv", "248am.com", "bazaar.town"]},
    "bahrain": {"name": "Bahrain", "language": "ar", "region": "Middle East", "sites": [
        "bna.bh", "alayam.com", "akhbar-alkhaleej.com", "gdnonline.com", "newsofbahrain.com",
        "al-bilad.com", "bt.com.bh", "bizbahrain.com", "manamapost.com", "bahrainthisweek.com"]},
    "oman": {"name": "Oman", "language": "ar", "region": "Middle East", "sites": [
        "timesofoman.com", "omanobserver.om", "muscatdaily.com", "omannews.gov.om", "shababoman.com",
        "atheer.om", "alroya.om", "2oom.com", "y-oman.com", "hellooman.com"]},
    "jordan": {"name": "Jordan", "language": "ar", "region": "Middle East", "sites": [
        "petra.gov.jo", "alghad.com", "alrai.com", "royanews.tv", "jordantimes.com",
        "addustour.com", "khaberni.com", "jo24.net", "7iber.com", "roya.tv"]},
    "lebanon": {"name": "Lebanon", "language": "ar", "region": "Middle East", "sites": [
        "naharnet.com", "annahar.com", "lorientlejour.com", "dailystar.com.lb", "mtv.com.lb",
        "lbcgroup.tv", "nna-leb.gov.lb", "al-akhbar.com", "megaphone.news", "daraj.com"]},
    "iraq": {"name": "Iraq", "language": "ar", "region": "Middle East", "sites": [
        "iraqinews.com", "alsumaria.tv", "shafaq.com", "rudaw.net", "nrttv.com",
        "almadapaper.net", "kirkuknow.com", "iraq-businessnews.com", "niqash.org", "insideiraq.net"]},
    "syria": {"name": "Syria", "language": "ar", "region": "Middle East", "sites": [
        "sana.sy", "enabbaladi.net", "syriadirect.org", "syrianobserver.com", "al-hal.com",
        "orient-news.net", "baladi-news.com", "syria.tv", "snacksyrian.com", "rozana.fm"]},
    "yemen": {"name": "Yemen", "language": "ar", "region": "Middle East", "sites": [
        "sabanews.net", "almashhadalaraby.com", "almasdaronline.com", "newsyemen.net", "adenalghad.net",
        "yemenakhbar.com", "aljazeera.net/yemen", "almawqeapost.net", "belqees.net", "sahafah24.net"]},
    "palestine": {"name": "Palestine", "language": "ar", "region": "Middle East", "sites": [
        "wafa.ps", "maannews.net", "qudsnet.com", "palestinechronicle.com", "imemc.org",
        "al-ayyam.ps", "alquds.com", "felesteen.ps", "middleeastmonitor.com", "mondoweiss.net"]},
    "israel": {"name": "Israel", "language": "he", "region": "Middle East", "sites": [
        "ynet.co.il", "haaretz.co.il", "maariv.co.il", "globes.co.il", "calcalist.co.il",
        "kan.org.il", "walla.co.il", "timesofisrael.com", "972mag.com", "i24news.tv"]},

    # ===== SOUTH ASIA =====
    "pakistan": {"name": "Pakistan", "language": "en", "region": "South Asia", "sites": [
        "dawn.com", "geo.tv", "thenews.com.pk", "tribune.com.pk", "dunyanews.tv",
        "arynews.tv", "samaa.tv", "brecorder.com", "propakistani.pk", "nayadaur.tv"]},
    "bangladesh": {"name": "Bangladesh", "language": "bn", "region": "South Asia", "sites": [
        "prothomalo.com", "thedailystar.net", "bdnews24.com", "jugantor.com", "ittefaq.com.bd",
        "banglanews24.com", "samakal.com", "dhaka-tribune.com", "newagebd.net", "tbsnews.net"]},
    "sri_lanka": {"name": "Sri Lanka", "language": "si", "region": "South Asia", "sites": [
        "dailymirror.lk", "island.lk", "sundaytimes.lk", "ft.lk", "dailynews.lk",
        "newsfirst.lk", "adaderana.lk", "colombogazette.com", "economynext.com", "groundviews.org"]},
    "nepal": {"name": "Nepal", "language": "ne", "region": "South Asia", "sites": [
        "kantipurdaily.com", "nagariknews.com", "setopati.com", "onlinekhabar.com", "ratopati.com",
        "ekantipur.com", "risingnepaldaily.com", "thehimalayantimes.com", "nepaltimes.com", "recordnepal.com"]},
    "afghanistan": {"name": "Afghanistan", "language": "ps", "region": "South Asia", "sites": [
        "tolonews.com", "pajhwok.com", "1tvnews.af", "arianavews.af", "8am.af",
        "bbc.com/pashto", "azadiradio.com", "killfrogy.com", "etilaatroz.com", "hasht-e-subh.com"]},
    "maldives": {"name": "Maldives", "language": "dv", "region": "South Asia", "sites": [
        "edition.mv", "sun.mv", "mihaaru.com", "avas.mv", "raajje.mv",
        "maldivesindependent.com", "vnews.mv", "dhauru.com", "thepress.mv", "adhadhu.com"]},
    "bhutan": {"name": "Bhutan", "language": "dz", "region": "South Asia", "sites": [
        "kuenselonline.com", "bbs.bt", "businessbhutan.bt", "thebhutanese.bt", "dailybhutan.com",
        "bhutantimes.bt", "bhutantoday.bt", "southasianmonitor.net", "bhutan.com", "yeewong.com"]},

    # ===== EAST & SOUTHEAST ASIA =====
    "japan": {"name": "Japan", "language": "ja", "region": "East Asia", "sites": [
        "nhk.or.jp/news", "asahi.com", "mainichi.jp", "yomiuri.co.jp", "nikkei.com",
        "sankei.com", "kyodonews.net", "jiji.com", "japantimes.co.jp", "tokyoreporter.com"]},
    "south_korea": {"name": "South Korea", "language": "ko", "region": "East Asia", "sites": [
        "chosun.com", "donga.com", "joongang.co.kr", "hani.co.kr", "khan.co.kr",
        "yna.co.kr", "kbs.co.kr", "koreaherald.com", "koreajoongangdaily.joins.com", "ohmynews.com"]},
    "taiwan": {"name": "Taiwan", "language": "zh", "region": "East Asia", "sites": [
        "ltn.com.tw", "udn.com", "chinatimes.com", "ettoday.net", "cna.com.tw",
        "pts.org.tw", "storm.mg", "newtalk.tw", "mirrormedia.mg", "thenewslens.com"]},
    "hong_kong": {"name": "Hong Kong", "language": "zh", "region": "East Asia", "sites": [
        "scmp.com", "thestandard.com.hk", "hk01.com", "mingpao.com", "rthk.hk",
        "bastillepost.com", "hkfp.com", "inmediahk.net", "eyepress.news", "coconuts.co/hongkong"]},
    "singapore": {"name": "Singapore", "language": "en", "region": "Southeast Asia", "sites": [
        "straitstimes.com", "channelnewsasia.com", "todayonline.com", "mothership.sg", "ricemedia.co",
        "businesstimes.com.sg", "zaobao.com.sg", "yahoo.com/sg/news", "mustsharenews.com", "theindependent.sg"]},
    "malaysia": {"name": "Malaysia", "language": "ms", "region": "Southeast Asia", "sites": [
        "thestar.com.my", "nst.com.my", "freemalaysiatoday.com", "malaysiakini.com", "bernama.com",
        "astroawani.com", "bharian.com.my", "says.com", "worldofbuzz.com", "cilisos.my"]},
    "indonesia": {"name": "Indonesia", "language": "id", "region": "Southeast Asia", "sites": [
        "kompas.com", "detik.com", "tempo.co", "tribunnews.com", "cnnindonesia.com",
        "liputan6.com", "tirto.id", "kumparan.com", "idntimes.com", "vice.com/id"]},
    "philippines": {"name": "Philippines", "language": "en", "region": "Southeast Asia", "sites": [
        "inquirer.net", "gmanetwork.com/news", "abs-cbn.com/news", "philstar.com", "manilatimes.net",
        "rappler.com", "cnnphilippines.com", "mb.com.ph", "sunstar.com.ph", "esquiremag.ph"]},
    "thailand": {"name": "Thailand", "language": "th", "region": "Southeast Asia", "sites": [
        "bangkokpost.com", "nationthailand.com", "thaipbsworld.com", "thaienquirer.com", "prachatai.com",
        "thairath.co.th", "dailynews.co.th", "matichon.co.th", "mgronline.com", "thestandard.co"]},
    "vietnam": {"name": "Vietnam", "language": "vi", "region": "Southeast Asia", "sites": [
        "vnexpress.net", "tuoitre.vn", "dantri.com.vn", "nhandan.vn", "vietnamnet.vn",
        "thanhnien.vn", "baomoi.com", "zing.vn", "kenh14.vn", "cafef.vn"]},
    "myanmar": {"name": "Myanmar", "language": "my", "region": "Southeast Asia", "sites": [
        "irrawaddy.com", "myanmar-now.org", "mizzima.com", "dvb.no", "frontier.net.mm",
        "mmtimes.com", "gnlm.com.mm", "bbc.com/burmese", "rfa.org/burmese", "themimu.info"]},
    "cambodia": {"name": "Cambodia", "language": "km", "region": "Southeast Asia", "sites": [
        "phnompenhpost.com", "khmertimeskh.com", "cambodiadaily.com", "voacambodia.com", "cambojanews.com",
        "freshnewsasia.com", "kohsantepheapdaily.com.kh", "cnc.com.kh", "ams.com.kh", "southeast-asia-globe.com"]},
    "laos": {"name": "Laos", "language": "lo", "region": "Southeast Asia", "sites": [
        "vientianetimes.org.la", "kpl.gov.la", "laotiantimes.com", "laosnews.net", "laosstarline.com",
        "rfa.org/lao", "thediplomat.com/tag/laos", "laofocus.com", "muanglao.com", "sabaaidee.com"]},
    "mongolia": {"name": "Mongolia", "language": "mn", "region": "East Asia", "sites": [
        "montsame.mn", "news.mn", "ikon.mn", "eagle.mn", "gogo.mn",
        "theubposts.com", "mongoliaweekly.org", "baabar.mn", "zuunii.mn", "dnn.mn"]},

    # ===== AFRICA =====
    "south_africa": {"name": "South Africa", "language": "en", "region": "Africa", "sites": [
        "news24.com", "iol.co.za", "timeslive.co.za", "dailymaverick.co.za", "ewn.co.za",
        "mg.co.za", "businessday.co.za", "citizen.co.za", "groundup.org.za", "scrollaafrica.com"]},
    "nigeria": {"name": "Nigeria", "language": "en", "region": "Africa", "sites": [
        "punchng.com", "vanguardngr.com", "thenationonlineng.net", "premiumtimesng.com", "guardian.ng",
        "channelstv.com", "thisdaylive.com", "businessday.ng", "sahara-reporters.com", "techcabal.com"]},
    "kenya": {"name": "Kenya", "language": "en", "region": "Africa", "sites": [
        "nation.africa", "standardmedia.co.ke", "the-star.co.ke", "businessdailyafrica.com", "citizen.digital",
        "capitalfm.co.ke", "kbc.co.ke", "tuko.co.ke", "kenyans.co.ke", "pesacheck.org"]},
    "ghana": {"name": "Ghana", "language": "en", "region": "Africa", "sites": [
        "graphic.com.gh", "myjoyonline.com", "ghanaweb.com", "citinewsroom.com", "pulse.com.gh",
        "3news.com", "dailyguidenetwork.com", "businessghana.com", "thebftonline.com", "aikistandard.com"]},
    "egypt": {"name": "Egypt", "language": "ar", "region": "Africa/Middle East", "sites": [
        "ahram.org.eg", "masrawy.com", "youm7.com", "shorouknews.com", "almalnews.com",
        "egyptindependent.com", "madamasr.com", "dailynewsegypt.com", "enterprise.press", "cairo24.com"]},
    "ethiopia": {"name": "Ethiopia", "language": "am", "region": "Africa", "sites": [
        "fanabc.com", "ena.et", "addisstandard.com", "thereporterethiopia.com", "ethiopianmonitor.com",
        "addisfortune.news", "capitalethiopia.com", "baborenews.com", "ahaduradio.com", "addiszeybe.com"]},
    "tanzania": {"name": "Tanzania", "language": "sw", "region": "Africa", "sites": [
        "dailynews.co.tz", "thecitizen.co.tz", "guardian.co.tz", "mwananchi.co.tz", "nipashe.co.tz",
        "ippmedia.com", "jamhurimedia.co.tz", "channelafrica.co.tz", "habarileo.co.tz", "sahihi.co.tz"]},
    "uganda": {"name": "Uganda", "language": "en", "region": "Africa", "sites": [
        "monitor.co.ug", "newvision.co.ug", "independent.co.ug", "observer.ug", "nilepost.co.ug",
        "chimpreports.com", "softpower.ug", "eagle.co.ug", "red-pepper.ug", "dignityforall.net"]},
    "rwanda": {"name": "Rwanda", "language": "en", "region": "Africa", "sites": [
        "newtimes.co.rw", "ktpress.rw", "igihe.com", "umuseke.rw", "taarifa.rw",
        "therwandan.com", "musekewecu.rw", "rwandatoday.africa", "jambonews.net", "greatlaketribune.com"]},
    "senegal": {"name": "Senegal", "language": "fr", "region": "Africa", "sites": [
        "aps.sn", "lequotidien.sn", "lesoleil.sn", "enqueteplus.com", "emedia.sn",
        "dakaractu.com", "seneweb.com", "igfm.sn", "pressafrik.com", "senego.com"]},
    "morocco": {"name": "Morocco", "language": "ar", "region": "Africa", "sites": [
        "hespress.com", "le360.ma", "medias24.com", "telquel.ma", "challenge.ma",
        "map.ma", "snrt.ma", "2m.ma", "h24info.ma", "leconomiste.com"]},
    "tunisia": {"name": "Tunisia", "language": "ar", "region": "Africa", "sites": [
        "tap.info.tn", "leaders.com.tn", "businessnews.com.tn", "nawaat.org", "inkyfada.com",
        "webdo.tn", "turess.com", "webmanagercenter.com", "tunisienumerique.com", "kapitalis.com"]},
    "algeria": {"name": "Algeria", "language": "ar", "region": "Africa", "sites": [
        "aps.dz", "elkhabar.com", "tsa-algerie.com", "interlignes.com", "elwatan.com",
        "liberte-algerie.com", "lexpressiondz.com", "echoroukonline.com", "algerie360.com", "algeriepatriotique.com"]},
    "cameroon": {"name": "Cameroon", "language": "fr", "region": "Africa", "sites": [
        "journalducameroun.com", "cameroon-tribune.cm", "cameroonmagazine.com", "cameroonconcord.com", "camerounweb.com",
        "actucameroun.com", "crtv.cm", "ecomatin.net", "lebledparle.com", "afrik.com/cameroun"]},
    "cote_divoire": {"name": "Côte d'Ivoire", "language": "fr", "region": "Africa", "sites": [
        "abidjan.net", "fratmat.info", "linfodrome.com", "koaci.com", "aip.ci",
        "connectionivoirienne.net", "lexpression.ci", "afrique-sur7.ci", "ivoirebusiness.net", "yeclo.com"]},
    "mozambique": {"name": "Mozambique", "language": "pt", "region": "Africa", "sites": [
        "jornalnoticias.co.mz", "savana.co.mz", "canalmoz.co.mz", "opais.co.mz", "zitamar.com",
        "club-of-mozambique.com", "lsm.co.mz", "verdade.co.mz", "carta.co.mz", "aim.org.mz"]},
    "zimbabwe": {"name": "Zimbabwe", "language": "en", "region": "Africa", "sites": [
        "herald.co.zw", "newsday.co.zw", "sundaymail.co.zw", "chronicle.co.zw", "263chat.com",
        "zimeye.net", "thestandard.co.zw", "bulawayo24.com", "cite.org.zw", "newzimbabwe.com"]},
    "angola": {"name": "Angola", "language": "pt", "region": "Africa", "sites": [
        "jornaldeangola.ao", "angop.ao", "rna.ao", "expansao.co.ao", "novagazeta.co.ao",
        "makaangola.org", "clubk.net", "voa.com/portuguese", "dw.com/pt/angola", "platinaline.com"]},
    "sudan": {"name": "Sudan", "language": "ar", "region": "Africa", "sites": [
        "sudantribune.com", "dabangasudan.org", "alrakoba.net", "altaghyeer.info", "sudaneseonline.com",
        "bbc.com/arabic/topics/sudan", "aljazeera.net/sudan", "ayin.com", "hurriyatsudan.com", "sudanakhbar.com"]},
    "drc": {"name": "DR Congo", "language": "fr", "region": "Africa", "sites": [
        "radiookapi.net", "actualite.cd", "7sur7.cd", "congoindependant.com", "desknewsrdc.net",
        "mediacongo.net", "politico.cd", "cas-info.ca", "scooprdc.net", "groupelavenir.org"]},
    "madagascar": {"name": "Madagascar", "language": "fr", "region": "Africa", "sites": [
        "midi-madagasikara.mg", "lexpressmada.com", "newsmada.com", "moov.mg", "gasypatriote.com",
        "matv.mg", "gazetiko.com", "orange.mg/actu", "madonline.com", "madagate.org"]},

    # ===== LATIN AMERICA =====
    "brazil": {"name": "Brazil", "language": "pt", "region": "Latin America", "sites": [
        "g1.globo.com", "folha.uol.com.br", "estadao.com.br", "uol.com.br", "r7.com",
        "bbc.com/portuguese", "poder360.com.br", "theintercept.com/brasil", "nexojornal.com.br", "agenciabrasil.ebc.com.br"]},
    "mexico": {"name": "Mexico", "language": "es", "region": "Latin America", "sites": [
        "eluniversal.com.mx", "reforma.com", "milenio.com", "jornada.com.mx", "excelsior.com.mx",
        "animalpolitico.com", "aristeguinoticias.com", "sinembargo.mx", "elpais.com/mexico", "proceso.com.mx"]},
    "argentina": {"name": "Argentina", "language": "es", "region": "Latin America", "sites": [
        "clarin.com", "lanacion.com.ar", "infobae.com", "pagina12.com.ar", "ambito.com",
        "perfil.com", "eldestapeweb.com", "cronista.com", "telam.com.ar", "chequeado.com"]},
    "colombia": {"name": "Colombia", "language": "es", "region": "Latin America", "sites": [
        "eltiempo.com", "elespectador.com", "semana.com", "pulzo.com", "rcnradio.com",
        "caracoltv.com", "bluradio.com", "lasillavacia.com", "colombiareports.com", "cerosetenta.uniandes.edu.co"]},
    "chile": {"name": "Chile", "language": "es", "region": "Latin America", "sites": [
        "emol.com", "latercera.com", "biobiochile.cl", "cooperativa.cl", "t13.cl",
        "elmostrador.cl", "ciperchile.cl", "ex-ante.cl", "interferencia.cl", "theclinic.cl"]},
    "peru": {"name": "Peru", "language": "es", "region": "Latin America", "sites": [
        "elcomercio.pe", "larepublica.pe", "gestion.pe", "rpp.pe", "peru21.pe",
        "ojo-publico.com", "idl-reporteros.pe", "convoca.pe", "wayka.pe", "sudaca.pe"]},
    "venezuela": {"name": "Venezuela", "language": "es", "region": "Latin America", "sites": [
        "elnacional.com", "runrun.es", "efectococuyo.com", "talcualdigital.com", "elestimulo.com",
        "armando.info", "prodavinci.com", "caracaschronicles.com", "monitoreamos.com", "lapatilla.com"]},
    "ecuador": {"name": "Ecuador", "language": "es", "region": "Latin America", "sites": [
        "eluniverso.com", "elcomercio.com", "lahora.com.ec", "expreso.ec", "primicias.ec",
        "teleamazonas.com", "ecuavisa.com", "planv.com.ec", "4pelagatos.com", "gk.city"]},
    "uruguay": {"name": "Uruguay", "language": "es", "region": "Latin America", "sites": [
        "elpais.com.uy", "elobservador.com.uy", "lr21.com.uy", "subrayado.com.uy", "montevideo.com.uy",
        "ladiaria.com.uy", "busqueda.com.uy", "sudestada.com.uy", "caras.com.uy", "brecha.com.uy"]},
    "paraguay": {"name": "Paraguay", "language": "es", "region": "Latin America", "sites": [
        "abc.com.py", "ultimahora.com", "lanacion.com.py", "hoy.com.py", "paraguaycom.com",
        "ip.gov.py", "5dias.com.py", "epy.com.py", "surtidosdeportivos.com.py", "elsurti.com"]},
    "bolivia": {"name": "Bolivia", "language": "es", "region": "Latin America", "sites": [
        "lostiempos.com", "eldeber.com.bo", "paginasiete.bo", "la-razon.com", "opinion.com.bo",
        "erbol.com.bo", "abi.bo", "brujuladigital.net", "boliviaentusmanos.com", "oxigenobolivia.com"]},
    "costa_rica": {"name": "Costa Rica", "language": "es", "region": "Central America", "sites": [
        "nacion.com", "crhoy.com", "ameliarueda.com", "elmundo.cr", "semanariouniversidad.com",
        "delfino.cr", "teletica.com", "repretel.com", "monumental.co.cr", "larepublica.net"]},
    "panama": {"name": "Panama", "language": "es", "region": "Central America", "sites": [
        "laestrella.com.pa", "prensa.com", "elsiglo.com.pa", "tvn-2.com", "metrolibre.com",
        "capital.com.pa", "diaadia.com.pa", "panamaamerica.com.pa", "critica.com.pa", "laestrella.com.pa/cafe-estrella"]},
    "guatemala": {"name": "Guatemala", "language": "es", "region": "Central America", "sites": [
        "prensalibre.com", "soy502.com", "elperiodico.com.gt", "lahora.gt", "publinews.gt",
        "republica.gt", "nomada.gt", "plazapublica.com.gt", "agn.gt", "emisorasunidas.com"]},
    "honduras": {"name": "Honduras", "language": "es", "region": "Central America", "sites": [
        "laprensa.hn", "elheraldo.hn", "tiempo.hn", "proceso.hn", "criterio.hn",
        "hondudiario.com", "latribuna.hn", "radiohrn.hn", "pasosdeanimalgrande.com", "contracorriente.red"]},
    "el_salvador": {"name": "El Salvador", "language": "es", "region": "Central America", "sites": [
        "laprensagrafica.com", "elsalvador.com", "elfaro.net", "diariocolatino.com", "revistafactum.com",
        "gatoencerrado.news", "lahuecanoticias.com", "salpress.net", "labrujula.com.sv", "voces.com.sv"]},
    "dominican_republic": {"name": "Dominican Republic", "language": "es", "region": "Caribbean", "sites": [
        "listindiario.com", "diariolibre.com", "elcaribe.com.do", "elnuevodiario.com.do", "hoy.com.do",
        "acento.com.do", "z101digital.com", "noticiassin.com", "cdn.com.do", "conectaconpablocontreras.com"]},
    "cuba": {"name": "Cuba", "language": "es", "region": "Caribbean", "sites": [
        "granma.cu", "cubadebate.cu", "oncubanews.com", "14ymedio.com", "diariodecuba.com",
        "cibercuba.com", "cubanet.org", "eltoquecom", "adncuba.com", "periodismodebarrio.org"]},
    "jamaica": {"name": "Jamaica", "language": "en", "region": "Caribbean", "sites": [
        "jamaicaobserver.com", "jamaica-gleaner.com", "loopjamaica.com", "nationwideradiojm.com", "go-jamaica.com",
        "jamaicans.com", "caribbeannewsglobal.com", "maboracreative.com", "yardflex.com", "dancehallmag.com"]},
    "trinidad": {"name": "Trinidad & Tobago", "language": "en", "region": "Caribbean", "sites": [
        "guardian.co.tt", "trinidadexpress.com", "newsday.co.tt", "looptt.com", "cnc3.co.tt",
        "tv6tnt.com", "i95.5fm.com", "wired868.com", "bfreedmedia.com", "sweetcrudemedia.com"]},
    "haiti": {"name": "Haiti", "language": "fr", "region": "Caribbean", "sites": [
        "lenouvelliste.com", "haitilibre.com", "metropolehaiti.com", "alterpresse.org", "haitistandard.com",
        "ayibopost.com", "juno7.ht", "radiotelevisioncaraibes.com", "rezo-nodwes.com", "haitiantimes.com"]},

    # ===== CENTRAL ASIA =====
    "kazakhstan": {"name": "Kazakhstan", "language": "kk", "region": "Central Asia", "sites": [
        "inform.kz", "tengrinews.kz", "zakon.kz", "vlast.kz", "kursiv.media",
        "azattyq.org", "orda.kz", "the-village-kz.com", "esquire.kz", "masa.media"]},
    "uzbekistan": {"name": "Uzbekistan", "language": "uz", "region": "Central Asia", "sites": [
        "uza.uz", "gazeta.uz", "kun.uz", "daryo.uz", "podrobno.uz",
        "uzreport.news", "kommersant.uz", "spot.uz", "repost.uz", "anhor.uz"]},
    "kyrgyzstan": {"name": "Kyrgyzstan", "language": "ky", "region": "Central Asia", "sites": [
        "kabar.kg", "24.kg", "kloop.kg", "akipress.com", "azattyk.org",
        "knews.kg", "kaktus.media", "bulak.kg", "zanoza.kg", "economist.kg"]},
    "tajikistan": {"name": "Tajikistan", "language": "tg", "region": "Central Asia", "sites": [
        "khovar.tj", "asiaplustj.info", "news.tj", "ozodi.org", "avesta.tj",
        "faraj.tj", "payrav.tj", "tojnews.tj", "vecherka.tj", "cabar.asia/en"]},
    "turkmenistan": {"name": "Turkmenistan", "language": "tk", "region": "Central Asia", "sites": [
        "turkmenistan.gov.tm", "orient.tm", "turkmenportal.com", "business.com.tm", "arzuw.news",
        "azathabar.com", "chrono-tm.org", "turkmen.news", "newscentralasia.net", "gundogar.org"]},

    # ===== OCEANIA =====
    "fiji": {"name": "Fiji", "language": "en", "region": "Oceania", "sites": [
        "fijitimes.com", "fijivillage.com", "fbcnews.com.fj", "fijisun.com.fj", "fijione.tv",
        "islandsbusiness.com", "pacificislandtimes.com", "rnzi.com/tags/fiji", "thejetnewspaper.com", "fijitoday.com"]},
    "papua_new_guinea": {"name": "Papua New Guinea", "language": "en", "region": "Oceania", "sites": [
        "postcourier.com.pg", "thenational.com.pg", "looppng.com", "emtv.com.pg", "pngindustrynews.net",
        "pngfacts.com", "asopa.typepad.com", "devpolicy.org/tag/png", "pacificislandtimes.com/png", "pngblogs.com"]},

    # ===== ADDITIONAL COUNTRIES =====
    "north_korea": {"name": "North Korea", "language": "ko", "region": "East Asia", "sites": [
        "kcna.kp", "rodong.rep.kp", "naenara.com.kp", "uriminzokkiri.com", "dprktoday.com",
        "nknews.org", "dailynk.com", "38north.org", "nkpro.org", "koreajoongangdaily.joins.com/nk"]},
    "libya": {"name": "Libya", "language": "ar", "region": "Africa", "sites": [
        "libyaobserver.ly", "libyaherald.com", "alarabyaljadeed.com/libya", "218tv.net", "alwasat.ly",
        "smc.ly", "bbc.com/arabic/topics/libya", "middleeasteye.net/countries/libya", "libyareview.com", "libyaakhbar.com"]},
    "somalia": {"name": "Somalia", "language": "so", "region": "Africa", "sites": [
        "hirshabelle.com", "garoweonline.com", "caasimada.net", "horseedmedia.net", "radiodalsan.com",
        "bbc.com/somali", "voasomali.com", "goobjoog.com", "keydmedia.net", "somalicurrent.com"]},
    "eritrea": {"name": "Eritrea", "language": "ti", "region": "Africa", "sites": [
        "shabait.com", "tesfanews.net", "eritreahub.org", "madote.com", "asmarino.com",
        "awate.com", "eritreanpress.com", "harnnet.org", "dehai.org", "bbc.com/tigrinya"]},
    "south_sudan": {"name": "South Sudan", "language": "en", "region": "Africa", "sites": [
        "eyeradio.org", "sudanspost.com", "radiotamazuj.org", "juba-monitor.com", "theniles.org",
        "paaborjournal.com", "gurtong.net", "cityreviewss.com", "southsudannation.com", "dabangasudan.org/south-sudan"]},
    "burundi": {"name": "Burundi", "language": "fr", "region": "Africa", "sites": [
        "iwacu-burundi.org", "rpa.bi", "burundidaily.net", "arib.info", "burunditransparence.org",
        "isanganiro.org", "bonesha.bi", "yaga-burundi.com", "jimbere.org", "akeza.net"]},
    "malawi": {"name": "Malawi", "language": "en", "region": "Africa", "sites": [
        "mwnation.com", "nyasatimes.com", "timesmw.com", "malawivoice.com", "zodiakonline.co.mz",
        "faceofmalawi.com", "maravipost.com", "malawi24.com", "mbc.mw", "malawiproject.org"]},
    "zambia": {"name": "Zambia", "language": "en", "region": "Africa", "sites": [
        "daily-mail.co.zm", "zambiadailymail.co.zm", "lusakatimes.com", "znbc.co.zm", "mwebantu.news",
        "diggers.news", "newsdayzambia.com", "smart-eagles.com", "lusaka-star.com", "thezambian.com"]},
    "botswana": {"name": "Botswana", "language": "en", "region": "Africa", "sites": [
        "mmegi.bw", "sundaystandard.info", "thepatriot.co.bw", "dailynews.gov.bw", "botswanaguardian.co.bw",
        "gazette.bw", "weekendpost.co.bw", "thevoicebw.com", "yarona.co.bw", "monitor.co.bw"]},
    "namibia": {"name": "Namibia", "language": "en", "region": "Africa", "sites": [
        "namibian.com.na", "newera.com.na", "observer24.com.na", "confidente.com.na", "republicein.com.na",
        "informante.web.na", "nbc.na", "namibiadailynews.info", "swakopmundmatters.com", "windhoekobserver.com.na"]},
    "mauritius": {"name": "Mauritius", "language": "en", "region": "Africa", "sites": [
        "lexpress.mu", "defimedia.info", "lemauricien.com", "inside.news", "5plus.mu",
        "ionnews.mu", "topfm.mu", "mauritiustimes.com", "businessmag.mu", "scope.mu"]},
    "seychelles": {"name": "Seychelles", "language": "en", "region": "Africa", "sites": [
        "seychellesnewsagency.com", "nation.sc", "todayinseychelles.com", "sbc.sc", "the-seychelles.com",
        "seychelles.news", "virtualseychelles.sc", "buzz.sc", "islandlife.sc", "seychellesweekly.com"]},
}

def get_all_countries():
    """Return combined dictionary of all countries."""
    all_countries = {}
    for key, data in TIER1_COUNTRIES.items():
        all_countries[key] = data
        all_countries[key]["tier"] = 1
    for key, data in TIER2_COUNTRIES.items():
        all_countries[key] = data
        all_countries[key]["tier"] = 2
    return all_countries

def print_summary():
    t1_sites = sum(len(c["sites"]) for c in TIER1_COUNTRIES.values())
    t2_sites = sum(len(c["sites"]) for c in TIER2_COUNTRIES.values())
    total = t1_sites + t2_sites
    print(f"Tier 1 countries: {len(TIER1_COUNTRIES)} ({t1_sites} sites)")
    print(f"Tier 2 countries: {len(TIER2_COUNTRIES)} ({t2_sites} sites)")
    print(f"TOTAL: {len(TIER1_COUNTRIES) + len(TIER2_COUNTRIES)} countries, {total} sites")

if __name__ == "__main__":
    print_summary()
