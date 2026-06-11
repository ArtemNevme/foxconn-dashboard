# PROMPT для AI-разработчика — Foxconn BI Dashboard

> Скопируй весь этот файл как задание и **приложи рядом `ARCHITECTURE.md`** (полная техническая
> спецификация) — там детали по каждой секции, схемам данных и методологии композита.

---

## Роль и контекст
Ты — senior Python/Streamlit разработчик. Строишь интерактивный BI-дашборд для учебного финального
проекта (Business Intelligence). Клиент-кейс: консалтинг для Foxconn — сравнение **Мексики и Бразилии**
как площадок для экспансии (направление Advanced Manufacturing & Assembly). Дашборд заменяет ранее
сделанную версию в Google Looker Studio и должен выглядеть профессионально и «вау».

## Цель
Полностью рабочий Streamlit-дашборд из **9 секций**, который:
1. тянет макро-данные **вживую** из World Bank и IMF API;
2. использует curated-данные (без API) из приложенных CSV;
3. никогда не падает при сбое сети (резервный snapshot);
4. деплоится на Streamlit Community Cloud.

## Технологический стек (НЕ менять)
- Python 3.11+
- **Streamlit** (UI), **Plotly** (графики), **pandas** (данные), **requests** (API), **openpyxl**.
- Деплой: Streamlit Community Cloud. (НЕ использовать Vercel / JS / Dash / Flask.)
- Зависимости уже в `requirements.txt`.

---

## Что УЖЕ готово в папке (НЕ пересоздавать)
```
data/Foxconn_Final_Data.xlsx        # исходник, 9 листов
data/snapshot/worldbank_macro.csv   # резерв макро-данных (World Bank), 2015–2024, Mexico+Brazil
data/snapshot/imf_forecast.csv      # резерв прогнозов (IMF), 2015–2026, с колонкой Note=Actual/Forecast
data/curated/CPI_Corruption.csv     # Transparency Intl, 2015–2024
data/curated/Economic_Freedom.csv   # Heritage, 2021–2024
data/curated/WGI_Governance.csv     # World Bank WGI, 2023 (6 показателей)
data/curated/Credit_Ratings.csv     # S&P/Moody's/Fitch/DBRS
data/curated/Manufacturing_EV.csv   # авто/EV/полупроводники/STEM/labor/Foxconn заводы (17 метрик)
data/curated/Comparison.csv         # вход для композита (ВНИМАНИЕ: смешанные шкалы, см. ниже)
data/curated/Sources.csv            # APA-цитаты + URL всех источников
requirements.txt, .gitignore, README.md
.streamlit/config.toml              # тема (зелёный primary)
ARCHITECTURE.md                     # ПОЛНАЯ спецификация — читай её
```
Твоя задача — написать **код**: `app.py`, `lib/*.py`, `views/*.py`.

---

## Слой данных — ГИБРИД (критично)

### Live API (реализовать в `lib/api_client.py`) — эндпоинты проверены, работают, ключи НЕ нужны
**World Bank** (макро, страны `MEX;BRA`, годы 2015–2024):
`https://api.worldbank.org/v2/country/MEX;BRA/indicator/{CODE}?format=json&date=2015:2024&per_page=500`
Коды индикаторов:
| CODE | Колонка |
|---|---|
| NY.GDP.MKTP.KD.ZG | GDP_Growth_Pct |
| FP.CPI.TOTL.ZG | Inflation_CPI_Pct |
| SL.UEM.TOTL.ZS | Unemployment_Pct |
| BX.KLT.DINV.WD.GD.ZS | FDI_Inflows_Pct_GDP |
| NV.IND.MANF.ZS | Manufacturing_Pct_GDP |
| NE.EXP.GNFS.ZS | Exports_Pct_GDP |
| NY.GDP.MKTP.CD | GDP_Current_USD (раздели на 1e9 → млрд) |

Формат ответа: JSON-массив `[meta, [records...]]`; каждая запись имеет
`countryiso3code`, `date`, `value` (может быть `null` — пропускать). Маппинг: MEX→Mexico, BRA→Brazil.

**IMF DataMapper** (прогнозы): `https://www.imf.org/external/datamapper/api/v1/{CODE}/MEX/BRA`
Коды: `NGDP_RPCH` (GDP growth), `PCPIPCH` (инфляция), `LUR` (безработица).
Ответ: `data["values"][CODE][iso3][year] = value`. Годы 2025–2026 = прогноз, остальное = факт.

### Требования к API-слою
- Кэш: `@st.cache_data(ttl=86400)` (тянуть раз в сутки, не на каждый клик).
- **Fallback:** `try` API → при любой ошибке/таймауте загрузить соответствующий CSV из `data/snapshot/`.
  Функции загрузки макро/прогнозов должны возвращать `(DataFrame, source_flag)`,
  где `source_flag ∈ {"LIVE","SNAPSHOT"}`.
- При успешном live-запросе **перезаписывать** snapshot-CSV (чтобы резерв всегда свежий).
- Обрабатывать `None`/пропуски в данных.

### Curated (реализовать в `lib/data_loader.py`)
Грузить из `data/curated/*.csv` через pandas с `@st.cache_data`. Это: CPI, Economic Freedom,
WGI, Credit Ratings, Manufacturing_EV, Comparison, Sources.

---

## Дизайн (реализовать в `lib/theme.py`)
- Цвета стран **постоянны во всём дашборде**: `Mexico = "#006847"` (зелёный), `Brazil = "#FEDD00"` (жёлтый).
- Единый Plotly-layout: прозрачный фон, шрифт sans-serif, легенда снизу, аккуратная сетка.
  Применять ко всем графикам.
- Акценты: тёмно-синий `#0A2540` для текста/карточек; `#1B9E77` (хорошо) / `#D62728` (плохо) для дельт.

## Переиспользуемые компоненты (`lib/components.py`)
- `kpi_card(label, mexico_val, brazil_val, fmt, higher_is_better)` — ряд `st.metric` с подсветкой победителя.
- `section_header(title, subtitle)`.
- `insight_box(markdown_text)` — цветной callout с выводом аналитика.
- `source_badge(kind, label)` — бейдж источника: 🟢 `LIVE · World Bank` / 📄 `Curated · <источник>` /
  🟡 `SNAPSHOT (API недоступен)`.
- `freshness_caption(source_flag, date)` — «Обновлено из World Bank API · <дата>».

---

## Секции (9 вкладок) — детали в ARCHITECTURE.md, раздел 7
1. **Macro Overview** — KPI-ряд + 3 time series (GDP/инфл./безраб., 2015–24) + scatter «Risk vs Return»
   (X=средняя инфляция, Y=средний рост) + GDP USD / Manufacturing %. Данные: **LIVE World Bank**.
2. **Corruption & Economic Freedom** — CPI time series + CPI Rank (инвертировать) + Economic Freedom. Curated.
3. **Governance & Credit** — radar/grouped bar по 6 WGI + таблица рейтингов с цветовой заливкой
   (Investment Grade=зелёный, Junk=красный). Curated.
4. **Manufacturing & Automotive** — бары: Auto_Production, OEM_Plants, Tier1_Suppliers, Auto_Employment,
   Auto_Exports, Capacity_Utilization. Curated.
5. **EV & Semiconductor** — бары EV_Sales/Production/Growth/Charging + 100% stacked + Semiconductor/Electronics.
   ⚠️ Подписать блок как **«EV Production & Export Base»**, НЕ «market» (Бразилия продаёт больше EV в абсолюте).
6. **Foxconn Investment** — bubble scatter (X=Labor_Cost, Y=STEM, size=Foxconn_Plants, color=страна) +
   KPI (3 завода vs 0; −27% труд; +88% STEM). Curated.
7. **Forecast** *(новое)* — time series из IMF: сплошная Actual + **пунктир Forecast 2025–26**;
   переключатель метрики (GDP/инфл./безраб.). Данные: **LIVE IMF**.
8. **Geo Map** *(новое)* — Plotly `choropleth`, zoom на Латинскую Америку, подсвечены MX+BR,
   цвет = выбираемая метрика (Composite / Manufacturing % / GDP Growth), шкала Max=зелёный→Min=красный.
   Нужен ISO-маппинг стран (Mexico→MEX, Brazil→BRA).
9. **Recommendation** — композитный балл (см. ниже) бар MX vs BR + decision matrix из Comparison.csv
   с подсветкой победителя по строке + блок «RECOMMENDED: Mexico» (5 факторов + Primary Risk/Mitigation).

---

## Композитный индекс — ОБЯЗАТЕЛЬНО исправить (`lib/composite.py`)
`Comparison.csv` смешивает шкалы (GDP=0.0143 рядом с EV Growth=180). **Нельзя суммировать напрямую.**
Реализуй взвешенный нормализованный индекс:
1. Для каждой метрики задать направление (higher_better / lower_better).
2. Нормализовать каждую в **0–100** (уже-0–100 как есть; рейтинг → числовой маппинг; остальное → масштаб
   против разумного референс-диапазона, НЕ вырожденный min-max по двум точкам).
3. Применить веса (под Advanced Manufacturing), сумма = 1.0:
   `Manufacturing 0.20, Labor 0.15, STEM 0.15, Credit 0.15, EconFreedom 0.10, FoxconnPlants 0.10, EV_Growth 0.10, CPI 0.05`.
4. Composite = Σ(норм × вес), 0–100, сопоставимый между странами.
5. **Показать веса на дашборде** (прозрачность методологии).

---

## Порядок сборки (делай по шагам, проверяй запуск после каждого)
1. **Каркас:** `app.py` (config, заголовок, сайдбар-фильтры: multiselect стран + слайдер лет, пустые вкладки)
   + `lib/theme.py` + `lib/components.py`. Убедись: `streamlit run app.py` запускается без ошибок.
2. `lib/api_client.py` + `lib/data_loader.py` (с кэшем и fallback). Проверь, что live-данные грузятся
   и при «выключенном» интернете подхватывается snapshot.
3. **Секция 1 (Macro)** целиком — как эталон стиля. Покажи бейдж LIVE и плашку свежести.
4. Секции 2–6 по тому же паттерну.
5. `lib/composite.py` + Секция 9 (Recommendation).
6. Секции 7 (Forecast) и 8 (Geo Map).
7. Полировка: insight-боксы, источники из Sources.csv, README-обновление.

## Стандарты кода
- Чистый, читаемый код; функции с понятными именами; комментарии где неочевидно (рус/англ — на выбор).
- Никаких хардкодов чисел в графиках — всё из данных.
- Все сетевые вызовы в `try/except` с fallback. Дашборд НЕ должен падать при сбое API.
- Каждая секция — отдельная функция `render(filters, data)` в своём файле `views/`.

## Критерий готовности
- `streamlit run app.py` открывает дашборд с 9 рабочими вкладками.
- Фильтры стран/лет влияют на графики.
- Макро и прогнозы грузятся из API (бейдж LIVE); при отключённом интернете — из snapshot (бейдж SNAPSHOT).
- Композит считается через нормализацию (не сырой Comparison).
- Гео-карта и forecast-пунктир работают.
- Готов к пушу на GitHub → Streamlit Cloud (см. README).
