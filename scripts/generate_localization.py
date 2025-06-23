import csv, unicodedata, re
from pathlib import Path

def slugify(name:str)->str:
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii','ignore').decode('ascii')
    name = name.lower()
    name = name.replace('&','and')
    name = re.sub(r'[^a-z0-9]+','_', name)
    name = re.sub(r'_+','_', name)
    return name.strip('_')

LANGS = {
    'english': 'l_english',
    'braz_por': 'l_braz_por',
    'french': 'l_french',
    'german': 'l_german',
    'polish': 'l_polish',
    'spanish': 'l_spanish',
    'turkish': 'l_turkish',
    'japanese': 'l_japanese',
    'russian': 'l_russian',
    'korean': 'l_korean',
    'simp_chinese': 'l_simp_chinese',
}

BASE = Path('VanillaReferenceFiles/localization')

# load vanilla translations if available
vanilla = {lang:{} for lang in LANGS}
for lang,tag in LANGS.items():
    file = BASE / lang / f'companies_{tag}.yml'
    if file.exists():
        for line in file.read_text(encoding='utf-8').splitlines():
            m = re.match(r'\s*(company_[^:]+):\s+"(.*)"', line)
            if m:
                k,v=m.groups()
                vanilla[lang][k]=v

# additional manual translations for certain languages
JP_EXTRA = {
    'asahi_glass_company': '旭硝子',
    'furukawa_zaibatsu': '古河財閥',
    'ishikawajima_shipyard': '石川島造船所',
    'japan_steel_works': '日本製鋼所',
    'kawasaki_dockyard': '川崎造船所',
    'kinkozan_sobei': '錦光山宗兵衛',
    'mitsubishi_zaibatsu': '三菱財閥',
    'mitsui_zaibatsu': '三井財閥',
    'nippon_denki_kabushiki': '日本電気株式会社',
    'nippon_kogaku_kogyo_nikk': '日本光学工業',
    'nippon_yusen_kaisha': '日本郵船会社',
    'oji_paper': '王子製紙',
    'showa_denko': '昭和電工',
    'minamimanshu_tetsudo': '南満洲鉄道',
    'sumitomo_zaibatsu': '住友財閥',
    'toyota_jido_shokki_kk': '豊田自動織機株式会社',
    'toyota_zaibatsu': '豊田財閥',
    'yasuda_zaibatsu': '安田財閥',
    'yawata_steel_works': '八幡製鉄所',
    'tokyo_electric_light_company': '東京電灯株式会社',
    'osaka_electric_light_company': '大阪電灯株式会社',
}

RU_EXTRA = {
    'baltic_shipyard': 'Балтийский завод',
    'branobel': 'БраНобель',
    'dobrolyot': 'Добролёт',
    'faberge': 'Фаберже',
    'izhevsk_arms_plant': 'Ижевский оружейный завод',
    'moscow_irrigation_company': 'Московская ирригационная компания',
    'new_russia_company_ltd': 'Компания "Новая Россия"',
    'obukhov_steel_works': 'Обуховский сталелитейный завод',
    'putilov_works': 'Путиловский завод',
    'russian_steam_navigation_company_ropit': 'Русское общество пароходства и торговли',
    'russian_american_company': 'Российско-американская компания',
    'russo_baltic_wagon_works': 'Русско-Балтийский вагонный завод',
    'savva_morozov_and_sons': 'Савва Морозов и сыновья',
    'state_bank_of_the_russian_empire': 'Государственный банк Российской империи',
    'tula_arms_plant': 'Тульский оружейный завод',
    'pa_smirnov': 'П. А. Смирнов',
    'st_petersburg_electric_lighting_company': 'Санкт-Петербургское общество электрического освещения',
    'moscow_electric_lighting_company': 'Московское общество электрического освещения',
}

def get_translation(slug,name,lang):
    key=f'company_{slug}'
    # prefer vanilla translation if available
    text = vanilla.get(lang,{}).get(key)
    if text:
        return text
    # apply manual overrides for certain languages
    if lang == 'japanese' and slug in JP_EXTRA:
        return JP_EXTRA[slug]
    if lang == 'russian' and slug in RU_EXTRA:
        return RU_EXTRA[slug]
    return name

CSV_PATH = Path('companies.csv')

rows=[]
with CSV_PATH.open(encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Company'].startswith('#'): continue
        rows.append(row)

# ensure output directories
for lang in LANGS:
    out_dir = Path('localization')/lang
    out_dir.mkdir(parents=True, exist_ok=True)

for lang,tag in LANGS.items():
    out_file = Path('localization')/lang/f'real_companies_{tag}.yml'
    with out_file.open('w', encoding='utf-8') as f:
        f.write(f'{tag}:\n')
        for row in rows:
            name=row['Company']
            slug=slugify(name)
            trans=get_translation(slug,name,lang)
            # escape quotes
            trans=trans.replace('"','\"')
            f.write(f' company_{slug}: "{trans}"\n')
