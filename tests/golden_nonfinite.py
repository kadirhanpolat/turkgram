# -*- coding: utf-8 -*-
"""Elle doğrulanmış Türkçe zarf-fiil (ulaç) biçimleri.

Bu tablo MOTORDAN DEĞİL, yalnız dilbilgisinden (nonfinite-spec.md "Ulaç ekleri"
DEĞİŞMEZ tablosu + Türkçe morfofonoloji) türetilmiştir. `nonfinite.py` /
`converb` uygulamasına bakılmadan, bağımsız olarak kurulmuştur.

kind ∈ {arak, ip, inca, madan, eli, dikce, meksizin, esiye}  (SPEC'teki 8 ulaç)

Kritik değişmezler (her hücre elle sağlandı):
  - Ünlü-başlı ek (arak/ip/inca/eli/esiye) → yumuşama + ye_de + kaynaştırma -y-:
      git→gid (giderek/gidip/gidince/gideli/gidesiye), ye→yi (yiyerek/yiyip...),
      oku→okuy- (okuyarak/okuyup/okuyunca/okuyalı/okuyasıya).
  - Ünsüz-başlı ek (madan/dikce/meksizin) → yumuşama YOK, ye_de YOK, -y- YOK:
      gitmeden/gittikçe/gitmeksizin, yemeden/yedikçe, okumadan/okudukça.
  - -Ip / -IncA yüksek ünlüsü 4'lü (yuvarlak duyarlı): okuyup/gülüp/görüp.
  - -AlI / -AsIyA / -mAksIzIn yüksek ünlüsü DÜZ (Iyi: a→ı, e→i): okuyalı/okumaksızın.
  - -DIkçA sertleşme: gittikçe/yaptıkça (t), geldikçe/okudukça (d).
"""

GOLDEN_CONVERB = {
    # --- düz ünsüz çok-heceli ---
    "yapmak": {
        "arak": "yaparak",
        "ip": "yapıp",
        "inca": "yapınca",
        "madan": "yapmadan",
        "eli": "yapalı",
        "dikce": "yaptıkça",      # D=t sertleşme
        "meksizin": "yapmaksızın",  # Iyi=ı
        "esiye": "yapasıya",
    },
    "çalışmak": {
        "arak": "çalışarak",
        "ip": "çalışıp",
        "inca": "çalışınca",
        "madan": "çalışmadan",
        "eli": "çalışalı",
        "dikce": "çalıştıkça",
        "meksizin": "çalışmaksızın",
        "esiye": "çalışasıya",
    },

    # --- ünlü-final (kaynaştırma -y- ünlü-başlı ekte) ---
    "okumak": {
        "arak": "okuyarak",
        "ip": "okuyup",           # I=u (yuvarlak)
        "inca": "okuyunca",       # I=u
        "madan": "okumadan",      # ünsüz-başlı → y YOK
        "eli": "okuyalı",         # Iyi=ı (DÜZ; okuyulı DEĞİL)
        "dikce": "okudukça",      # D=d, ünsüz-başlı → y YOK
        "meksizin": "okumaksızın",  # Iyi=ı, y YOK
        "esiye": "okuyasıya",     # Iyi=ı
    },
    "beklemek": {
        "arak": "bekleyerek",
        "ip": "bekleyip",         # I=i
        "inca": "bekleyince",
        "madan": "beklemeden",
        "eli": "bekleyeli",       # Iyi=i
        "dikce": "bekledikçe",    # D=d
        "meksizin": "beklemeksizin",  # Iyi=i
        "esiye": "bekleyesiye",
    },
    "aramak": {
        "arak": "arayarak",
        "ip": "arayıp",           # I=ı
        "inca": "arayınca",
        "madan": "aramadan",
        "eli": "arayalı",         # Iyi=ı
        "dikce": "aradıkça",      # D=d
        "meksizin": "aramaksızın",
        "esiye": "arayasıya",
    },

    # --- yumuşama (ünlü-başlı ekte t→d; ünsüz-başlıda YOK) ---
    "gitmek": {
        "arak": "giderek",        # gid+erek
        "ip": "gidip",            # gid+ip
        "inca": "gidince",        # gid+ince
        "madan": "gitmeden",      # yumuşama YOK
        "eli": "gideli",          # gid+eli
        "dikce": "gittikçe",      # sertleşme t
        "meksizin": "gitmeksizin",  # yumuşama YOK
        "esiye": "gidesiye",      # gid+esiye
    },
    "etmek": {
        "arak": "ederek",         # ed+erek
        "ip": "edip",
        "inca": "edince",
        "madan": "etmeden",
        "eli": "edeli",
        "dikce": "ettikçe",       # sertleşme t
        "meksizin": "etmeksizin",
        "esiye": "edesiye",
    },

    # --- ye_de (ünlü-başlı ekte ye→yi, de→di; ünsüz-başlıda YOK) ---
    "yemek": {
        "arak": "yiyerek",        # yi+y+erek
        "ip": "yiyip",            # yi+y+ip
        "inca": "yiyince",        # yi+y+ince
        "madan": "yemeden",       # ye_de YOK (ünsüz-başlı)
        "eli": "yiyeli",          # yi+y+eli
        "dikce": "yedikçe",       # ye_de YOK, D=d
        "meksizin": "yemeksizin",  # ye_de YOK
        "esiye": "yiyesiye",      # yi+y+esiye
    },
    "demek": {
        "arak": "diyerek",        # di+y+erek
        "ip": "diyip",
        "inca": "diyince",
        "madan": "demeden",       # ye_de YOK
        "eli": "diyeli",
        "dikce": "dedikçe",       # ye_de YOK, D=d
        "meksizin": "demeksizin",  # ye_de YOK
        "esiye": "diyesiye",
    },

    # --- yuvarlak ünlü (I=ü ama Iyi=i düz) ---
    "görmek": {
        "arak": "görerek",
        "ip": "görüp",            # I=ü
        "inca": "görünce",        # I=ü
        "madan": "görmeden",
        "eli": "göreli",          # Iyi=i (DÜZ)
        "dikce": "gördükçe",      # D=d
        "meksizin": "görmeksizin",  # Iyi=i
        "esiye": "göresiye",      # Iyi=i
    },
    "gülmek": {
        "arak": "gülerek",
        "ip": "gülüp",            # I=ü
        "inca": "gülünce",        # I=ü
        "madan": "gülmeden",
        "eli": "güleli",          # Iyi=i
        "dikce": "güldükçe",      # D=d
        "meksizin": "gülmeksizin",  # Iyi=i
        "esiye": "gülesiye",      # Iyi=i
    },

    # --- tek-heceli düz ---
    "almak": {
        "arak": "alarak",
        "ip": "alıp",             # I=ı
        "inca": "alınca",
        "madan": "almadan",
        "eli": "alalı",           # Iyi=ı
        "dikce": "aldıkça",       # D=d
        "meksizin": "almaksızın",
        "esiye": "alasıya",
    },
    "gelmek": {
        "arak": "gelerek",
        "ip": "gelip",            # I=i
        "inca": "gelince",
        "madan": "gelmeden",
        "eli": "geleli",          # Iyi=i
        "dikce": "geldikçe",      # D=d
        "meksizin": "gelmeksizin",
        "esiye": "gelesiye",
    },
}
