# Foxconn BI Dashboard — Архитектура

**Проект:** Интерактивный дашборд «Foxconn: Mexico vs Brazil» (замена Looker Studio)
**Заказчик (учебный):** Foxconn / Group 3 / Advanced Manufacturing & Assembly
**Цель:** Воспроизвести 7 секций Looker Studio + закрыть пробелы по лабам (гео-карта, прогноз) + починить методологию композита.

---

## 1. Технологический стек

| Слой | Выбор | Почему |
|---|---|---|
| Язык | Python 3.11+ | Минимум кода, вся аналитика в pandas |
| UI-фреймворк | **Streamlit** | Повторяет референс препода; один скрипт уже работает |
| Данные | pandas + openpyxl | Читаем существующий `Foxconn_Final_Data.xlsx` напрямую |
| Графики | **Plotly** (`plotly.express` / `graph_objects`) | Интерактив (hover, zoom, легенда), экспорт PNG, нативная интеграция со Streamlit |
| Карта | Plotly `choropleth` (Natural Earth) | Не требует API-ключа, работает офлайн, цвет = метрика |
| Хостинг | **Streamlit Community Cloud** | Бесплатно, публичный URL, деплой из GitHub в 3 клика |

> Альтернатива под Vercel: Next.js + Plotly.js + статический `data.json`. Отдельный план при необходимости.

---

## 2. Структура проекта

```
foxconn-dashboard/
├── app.py                      # Точка входа: конфиг страницы, сайдбар, роутинг по вкладкам
├── data/
│   └── Foxconn_Final_Data.xlsx # Источник (9 листов)
├── data/snapshot/              # авто-резерв последних API-данных (CSV)
├── lib/
│   ├── api_client.py           # ➕ Live-загрузка World Bank + IMF, кэш + snapshot-резерв
│   ├── data_loader.py          # Загрузка curated-листов из Excel, @st.cache_data
│   ├── theme.py                # Цвета стран, палитра, шрифты, Plotly-layout по умолчанию
│   ├── composite.py            # ИСПРАВЛЕННЫЙ нормализованный композитный индекс
│   └── components.py           # KPI-карточка, заголовок секции, insight-бокс, footer-источник
├── views/
│   ├── overview.py             # Секция 1: Макро-обзор
│   ├── governance.py           # Секция 2+3: Коррупция/Свобода + Governance/Рейтинги
│   ├── manufacturing.py        # Секция 4: Производство и автопром
│   ├── ev_semi.py              # Секция 5: EV и полупроводники
│   ├── foxconn.py              # Секция 6: Анализ Foxconn
│   ├── forecast.py             # ➕ НОВОЕ: Прогноз IMF 2025–2026 + трендлайн
│   ├── geomap.py               # ➕ НОВОЕ: Гео-карта Латинской Америки
│   └── recommendation.py       # Секция 7: Композит + матрица решения
├── .streamlit/
│   └── config.toml             # Тема (цвета, шрифт), настройки сервера
├── requirements.txt
└── README.md                   # Как запустить + ссылка на деплой
```

---

## 3. Слой данных — ГИБРИД: Live API + Curated + резерв

Данные приходят из двух источников, объединяются в единые DataFrame:

### 3.1 Live API (`lib/api_client.py`) — проверено рабочими запросами
| Данные | API | Ключ | Статус |
|---|---|---|---|
| GDP, инфляция, безработица, FDI, manufacturing %, экспорт %, GDP USD | World Bank WDI `api.worldbank.org/v2` | не нужен | ✅ тест пройден, совпадает с Excel |
| Прогнозы GDP/инфл./безраб. 2025–26 | IMF DataMapper `imf.org/external/datamapper/api/v1` | не нужен | ✅ тест пройден |
| WGI (governance) | World Bank, отдельная база/коды | не нужен | ⚠️ найти актуальный эндпоинт |

Коды индикаторов World Bank: `NY.GDP.MKTP.KD.ZG` (GDP growth), `FP.CPI.TOTL.ZG` (инфляция),
`SL.UEM.TOTL.ZS` (безработица), `BX.KLT.DINV.WD.GD.ZS` (FDI), `NV.IND.MANF.ZS` (manufacturing %),
`NE.EXP.GNFS.ZS` (экспорт %), `NY.GDP.MKTP.CD` (GDP USD). Страны: `MEX;BRA`. IMF: `NGDP_RPCH` и др.

```python
@st.cache_data(ttl=86400)              # тянем раз в сутки, не на каждый клик
def fetch_worldbank(indicator, countries=("MEX","BRA"), start=2015, end=2024) -> pd.DataFrame: ...
@st.cache_data(ttl=86400)
def fetch_imf(indicator, countries=("MEX","BRA")) -> pd.DataFrame: ...

def get_macro() -> pd.DataFrame:
    try:
        df = _assemble_from_worldbank(...)   # live
        _save_snapshot(df, "macro")          # обновляем резерв
        return df, "LIVE"
    except Exception:
        return _load_snapshot("macro"), "SNAPSHOT"   # резерв — демо не падает
```

### 3.2 Curated (нет публичного API) — из Excel/CSV
CPI (Transparency Intl), Economic Freedom (Heritage), Credit Ratings (S&P/Moody's/Fitch),
вся отраслевая Foxconn-специфика (OICA, IEA, CANIETI, STEM, labor, заводы). Грузятся из
`Foxconn_Final_Data.xlsx` как раньше. Каждая — с APA-цитатой из листа `Sources`.

### 3.3 Надёжность (критично для живой защиты)
- Каждый успешный API-вызов пишет **snapshot CSV** в `data/snapshot/`.
- При сбое сети/API дашборд автоматически берёт последний snapshot → **демо не ломается**.
- На графиках — **бейдж источника**: 🟢 `LIVE · World Bank` / 📄 `Curated · Heritage 2024` / 🟡 `SNAPSHOT (API недоступен)`.
- Плашка свежести: «Обновлено из World Bank API · <дата>».

### 3.4 Curated-листы Excel (схемы)
Каждый лист → функция-загрузчик с кэшем. Схемы (из реального файла):

| Лист | Ключевые колонки | Назначение |
|---|---|---|
| `Macro_Economic` | Country, Year(2015–24), GDP_Growth_Pct, Inflation_CPI_Pct, Unemployment_Pct, FDI_Inflows_Pct_GDP, Manufacturing_Pct_GDP, Exports_Pct_GDP, GDP_Current_USD_Billions | Секции 1, гео-карта |
| `CPI_Corruption` | Country, Year(2015–24), CPI_Score, CPI_Rank | Секция 2 |
| `Economic_Freedom` | Country, Year(2021–24), Economic_Freedom_Score, Overall_Rank | Секция 2 |
| `WGI_Governance` | Country, Year(2023), 6 показателей (Voice…Control_of_Corruption) | Секция 3 (radar/grouped bar) |
| `Credit_Ratings` | Country, Rating_Agency, Rating, Outlook, Grade_Category | Секция 3 (таблица) |
| `Manufacturing_EV` | Country + 17 метрик (Auto_*, EV_*, Semiconductor, STEM, Foxconn_Plants, Labor_Cost) | Секции 4, 5, 6 |
| `IMF_WEO_Forecast` | Country, Year(2020–26), GDP/Infl/Unemp, Note(Actual/Forecast) | ➕ Секция Прогноз |
| `Comparison` | Metric, Mexico, Brazil | Вход для композита (требует нормализации!) |
| `Sources` | Source_Name, Data_Type, Citation_APA, URL | Футер «Sources» / вкладка About |

**API загрузчика:**
```python
@st.cache_data
def load_macro() -> pd.DataFrame: ...
@st.cache_data
def load_manufacturing() -> pd.DataFrame: ...
# ... по одной на лист
@st.cache_data
def load_all() -> dict[str, pd.DataFrame]: ...   # единая точка
```
Кэш `@st.cache_data` означает: Excel читается один раз, дальше — из памяти.

---

## 4. Глобальные фильтры (сайдбар, `app.py`)

- **Выбор стран** — multiselect `[Mexico, Brazil]` (по умолчанию обе). Фильтрует все графики.
- **Диапазон лет** — slider `2015–2024` (для time-series секций).
- **Брендинг** — логотип/заголовок Foxconn, подпись «Group 3 · BI · June 2026».
- Фильтры пробрасываются в каждую `view`-функцию как аргументы → единый источник правды для состояния.

---

## 5. Дизайн-система (`lib/theme.py`)

```python
COUNTRY_COLORS = {"Mexico": "#006847",  # зелёный (флаг MX)
                  "Brazil": "#FEDD00"}  # жёлтый (флаг BR)
ACCENT = "#0A2540"      # тёмно-синий фон карточек
GOOD = "#1B9E77"; BAD = "#D62728"  # для дельт/индикаторов
```
- Единый `PLOTLY_LAYOUT` (шрифт, прозрачный фон, сетка, легенда снизу) применяется ко всем графикам через `fig.update_layout(**PLOTLY_LAYOUT)`.
- `.streamlit/config.toml`: тёмная/светлая тема, primaryColor, шрифт.
- Цвет страны постоянен во ВСЁМ дашборде (Мексика всегда зелёная) — ключ к читаемости.

---

## 6. Библиотека компонентов (`lib/components.py`)

| Компонент | Сигнатура | Где |
|---|---|---|
| `kpi_card(label, mx_val, br_val, fmt, better)` | ряд `st.metric` с подсветкой победителя | верх каждой секции |
| `section_header(title, subtitle)` | заголовок + разделитель | каждая view |
| `insight_box(markdown)` | цветной callout с выводом аналитика | под графиками |
| `source_footer(sources)` | мелкая подпись «Source: …» (APA) | низ графика |
| `country_filter_apply(df, countries)` | фильтрация по выбранным странам | везде |

---

## 7. Секции (детально)

### Секция 1 — Macro Overview (`overview.py`)
- **KPI-ряд:** GDP Growth 2024, Inflation 2024, Unemployment 2024, Manufacturing %GDP (Mexico vs Brazil, с дельтой).
- **3× Time series** (2015–2024): GDP Growth / Inflation / Unemployment, по линии на страну. → навык Лаб 4.
- **Scatter «Risk vs Return»:** X = средняя инфляция (стабильность), Y = средний GDP-рост, по стране. → навык Лаб 6.
- **Stacked area / bar:** GDP Current USD + Manufacturing %.
- Insight: «Мексика — ниже безработица и больше manufacturing; Бразилия — больше абсолютная экономика и волатильнее».

### Секция 2 — Corruption & Economic Freedom (`governance.py`, часть 1)
- Time series CPI_Score (2015–24) + бар CPI_Rank (ниже=лучше, инвертировать ось).
- Бар/линия Economic Freedom (2021–24), аннотации 63.2 / 53.2.
- Insight: честно — Бразилия чище по CPI, Мексика свободнее по Heritage.

### Секция 3 — Governance & Credit (`governance.py`, часть 2)
- **Radar / grouped bar** по 6 WGI-показателям (2023). Radar = «форма» управления (аналог threat-profile из Лаб 7).
- **Таблица Credit_Ratings** с цветовой заливкой Grade_Category (Investment Grade=зелёный, Junk=красный) → навык heatmap-таблицы из Лаб 2.
- Insight: Мексика — Investment Grade у всех 4 агентств; Бразилия — спекулятивный.

### Секция 4 — Manufacturing & Automotive (`manufacturing.py`)
- Бары: Auto_Production, OEM_Plants, Tier1_Suppliers, Auto_Employment, Auto_Exports, Capacity_Utilization. → навык Лаб 1/3.
- ⚠️ Использовать согласованное число Auto_Exports (см. раздел 9).

### Секция 5 — EV & Semiconductor (`ev_semi.py`)
- Бары EV_Sales / EV_Production / EV_Growth / Charging_Stations.
- **100% stacked** «EV market composition». → навык Лаб 7.
- Semiconductor_Exports, Electronics_Mfg.
- ⚠️ Подписать блок как **«EV Production & Export Base»**, не «market» (Бразилия продаёт больше — см. раздел 9).

### Секция 6 — Foxconn Investment (`foxconn.py`)
- **Bubble scatter:** X = Labor_Cost_Hourly, Y = STEM_Graduates, размер = Foxconn_Plants, цвет = страна. → навык Лаб 4.
- KPI: 3 завода MX vs 0 BR; 27% дешевле труд; 88% больше STEM.

### ➕ Секция — Forecast (`forecast.py`) *(новое, закрывает Лаб 8)*
- Time series из `IMF_WEO_Forecast`: сплошная линия Actual (2020–24) + **пунктир Forecast (2025–26)**.
- Метрики переключаются: GDP Growth / Inflation / Unemployment (radio/selectbox).
- Insight: прогноз восстановления MX 0.56%→1.64%, BR замедление.

### ➕ Секция — Geo Map (`geomap.py`) *(новое, закрывает Лаб 3/4)*
- **Plotly choropleth**, zoom = Латинская Америка, подсвечены Mexico + Brazil.
- Цвет = выбираемая метрика (Composite Score / Manufacturing % / GDP Growth). Селектор метрики сверху.
- Шкала Max=зелёный … Min=красный (как в Лаб 3).
- Hover-тултип со сводкой по стране.

### Секция 7 — Recommendation (`recommendation.py`)
- **Композитный балл (исправленный, см. раздел 8)** — бар Mexico vs Brazil.
- **Decision matrix** — таблица из `Comparison` с подсветкой победителя по строке.
- Большой вывод: «RECOMMENDED: Mexico» + 5 ключевых факторов + Primary Risk/Mitigation.

---

## 8. Исправление композита (`lib/composite.py`) — критично

**Проблема:** лист `Comparison` смешивает шкалы (GDP=0.0143 vs EV Growth=180). Прямое суммирование некорректно.

**Решение — взвешенный нормализованный индекс (как Лаб 3):**
1. Для каждой метрики задать **направление** (`higher_better` / `lower_better`).
2. Нормализовать каждую метрику в **0–100** по индикатор-специфичной шкале:
   - уже 0–100 (CPI, Economic Freedom) → как есть;
   - кредитный рейтинг → маппинг в числовую шкалу (BBB→x, BB→y);
   - остальные → min-max против **референс-диапазона** (не только двух стран, чтобы не было вырожденных 0/1), либо peer-benchmark.
3. Применить **веса**, согласованные с фокусом «Advanced Manufacturing & Assembly»:
   ```python
   WEIGHTS = {
       "Manufacturing_Pct_GDP": 0.20, "Labor_Cost": 0.15, "STEM": 0.15,
       "Foxconn_Plants": 0.10, "Credit_Rating": 0.15, "Economic_Freedom": 0.10,
       "EV_Growth": 0.10, "CPI": 0.05,
   }  # сумма = 1.0
   ```
4. Composite = Σ(норм_метрика × вес) → балл 0–100, **сопоставимый между странами**.
5. Веса вынести в конфиг и **показать на дашборде** (прозрачность методологии = защита на Q&A).

---

## 9. Чек-лист корректности данных (исправить до сборки)
1. **Auto Exports:** согласовать Excel (BR 15.2 / MX 177.9) с отчётом (12 / 176). Выбрать одно число + источник.
2. **EV-нарратив:** на дашборде формулировать как production/export base; не утверждать, что Мексика — больший EV-рынок.
3. **Композит:** считать только через `lib/composite.py` (нормализация), не суммировать сырой `Comparison`.
4. **Источники по годам:** подписывать World Bank vs IMF там, где числа за один год расходятся.
5. **WGI = 2023:** в подписях указывать год явно.

---

## 10. requirements.txt
```
streamlit>=1.40
pandas>=2.2
plotly>=5.24
openpyxl>=3.1
requests>=2.32   # вызовы World Bank / IMF API
```

---

## 11. Деплой (Streamlit Community Cloud)
1. `git init`, запушить репозиторий на GitHub (публичный).
2. share.streamlit.io → New app → выбрать репозиторий + `app.py`.
3. Получить публичный URL вида `https://foxconn-mx-br.streamlit.app` → вставить в отчёт и разослать.
4. Данные едут в репозитории (`data/*.xlsx`) — внешних ключей/секретов нет.

---

## 12. Порядок сборки (milestones)
1. **Каркас:** `app.py` + `data_loader.py` + `theme.py` + сайдбар-фильтры → пустые вкладки. *(проверяем, что запускается)*
2. **Секция 1 (Macro)** целиком — как эталон стиля/компонентов.
3. Размножаем паттерн на секции 2–6.
4. **Composite fix** + Секция 7.
5. **Новое:** Forecast + Geo map.
6. Полировка темы, insight-боксы, источники, README.
7. Деплой на Streamlit Cloud.

---

## 13. Оценка сложности
- **Технически:** низкая-средняя. Данные крошечные, БД не нужна, всё в pandas.
- **Время:** рабочий каркас + 1 секция — пара часов; полная версия — ~1 день вайб-кодинга.
- **Главные риски:** (а) причёсывание стиля под референс; (б) корректная нормализация композита; (в) маппинг названий стран для choropleth (ISO-коды).
