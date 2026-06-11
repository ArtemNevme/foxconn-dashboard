# Foxconn BI Dashboard — Mexico vs Brazil

Интерактивный дашборд для финального проекта по Business Intelligence (Group 3, Advanced
Manufacturing & Assembly). Сравнивает Мексику и Бразилию как площадки для экспансии Foxconn.
Заменяет дашборд из Looker Studio. Данные — гибрид: live из World Bank + IMF API и curated-индексы.

## Запуск локально

```bash
# 1. (один раз) создать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# 2. установить зависимости
pip install -r requirements.txt

# 3. запустить
streamlit run app.py
```

Откроется в браузере на http://localhost:8501

## Деплой (Streamlit Community Cloud)

1. Запушить репозиторий на GitHub (публичный).
2. Зайти на https://share.streamlit.io → **New app** → выбрать репозиторий и `app.py`.
3. Получить публичный URL → вставить в отчёт и разослать.

## Структура

| Путь | Что |
|---|---|
| `app.py` | Точка входа, сайдбар-фильтры, вкладки |
| `lib/api_client.py` | Live-загрузка World Bank + IMF (кэш + резерв) |
| `lib/data_loader.py` | Curated-данные из CSV/Excel |
| `lib/composite.py` | Нормализованный композитный индекс |
| `lib/theme.py`, `lib/components.py` | Стиль и переиспользуемые UI-блоки |
| `views/` | 9 секций дашборда |
| `data/snapshot/` | Резервные CSV из API (worldbank_macro, imf_forecast) |
| `data/curated/` | Данные без API (CPI, рейтинги, EV и т.д.) |
| `ARCHITECTURE.md` | Полная техническая архитектура |
| `PROMPT.md` | Промпт для AI-разработчика |

## Источники данных
- **Live API:** World Bank (WDI), IMF (DataMapper) — ключи не нужны.
- **Curated:** Transparency International (CPI), Heritage (Economic Freedom), S&P/Moody's/Fitch
  (рейтинги), OICA/IEA/CANIETI/Trade.gov (производство, EV, полупроводники). См. `data/curated/Sources.csv`.
