# API Эндпоинты для Извлечения Данных о Круизах

Данный документ описывает API эндпоинты, которые необходимо создать для замены прямых SQL запросов в системе извлечения данных о круизах. Каждый эндпоинт основан на существующих функциях из `extractor.py` и `agent_tools.py`.

## 1. Получение Активных ID Круизов

### `GET /api/cruises/enabled-ids`

**Описание:** Получает все активные ID круизов из материализованного представления `mv_cruise_info`.

**Параметры запроса:**
- Нет параметров

**Исходный SQL запрос:**
```sql
SELECT m.cruise_id 
FROM mv_cruise_info m
JOIN mv_cruise_date_range_info mcdri on mcdri.cruise_id = m.cruise_id  
WHERE m.enabled = true
    and (mcdri.cruise_date_range_info->'dateRange'->>'begin_date')::date > NOW()::date
```


## 2. Получение Данных о Круизах Пакетами

### `GET /api/cruises/batch-data`

**Описание:** Получает данные о круизах пакетами из материализованного представления `mv_cruise_info`.

**Параметры запроса:**
- `cruise_ids` (array): Массив ID круизов для получения данных

**Пример запроса:**
```
GET /api/cruises/batch-data?cruise_ids=["id1","id2","id3"]
```

**Исходный SQL запрос:**
```sql
SELECT cruise_id, ufl, cruise_info 
FROM mv_cruise_info 
WHERE cruise_id = ANY(%s)
```


## 3. Получение Информации о Датах и Ценах

### `GET /api/cruises/date-price-info`

**Описание:** Получает информацию о датах и ценах из материализованного представления `mv_cruise_date_range_info`.

**Параметры запроса:**
- `cruise_ids` (array): Массив ID круизов для получения информации

**Пример запроса:**
```
GET /api/cruises/date-price-info?cruise_ids=["id1","id2","id3"]
```

**Исходный SQL запрос:**
```sql
SELECT cruise_id, cruise_date_range_id, cruise_date_range_info 
FROM mv_cruise_date_range_info 
WHERE cruise_id = ANY(%s)
```


## 4. Фильтрация Круизов по Диапазону Дат

### `GET /api/cruises/filter-by-date-range`

**Описание:** Получает активные ID круизов, которые попадают в указанный диапазон дат.

**Параметры запроса:**
- `date_from` (string): Начальная дата в формате 'YYYY-MM-DD'
- `date_to` (string): Конечная дата в формате 'YYYY-MM-DD'

**Пример запроса:**
```
GET /api/cruises/filter-by-date-range?date_from=2025-01-01&date_to=2025-12-31
```

**Исходный SQL запрос:**
```sql
SELECT m.cruise_id
FROM mv_cruise_info m
JOIN mv_cruise_date_range_info mcdri 
    ON mcdri.cruise_id = m.cruise_id
WHERE m.enabled = TRUE
  AND (
        (mcdri.cruise_date_range_info->'dateRange'->>'begin_date')::date <= %s
        AND (mcdri.cruise_date_range_info->'dateRange'->>'end_date')::date >= %s
      )
```
