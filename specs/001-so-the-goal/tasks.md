# Tasks: Cruise Info Vector DB Creator

**Input**: Design documents from `/specs/001-so-the-goal/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in `src/` and `tests/`.
- [X] T002 Create `requirements.txt` and add all dependencies from `plan.md`.
- [X] T003 [P] Configure `ruff` for linting and formatting.
- [X] T004 [P] Create a `.env` file to store database credentials.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [X] T005 Implement a module in `src/data_extraction/db.py` to connect to the Postgres database using `psycopg2-binary` and load credentials from the `.env` file.

---

## Phase 3: User Story 1 - Data Extraction

**Goal**: Extract cruise information from a Postgres materialized view and save it as a JSON file.

**Independent Test**: A JSON file is created and contains the correct data from the materialized view.

- [X] T006 [US1] In `src/data_extraction/extractor.py`, implement a function to fetch all `cruise_id`s from the `mv_cruise_info` materialized view where `enabled` is true.
- [X] T007 [US1] In `src/data_extraction/extractor.py`, implement a function to fetch cruise data in batches of 10 from `mv_cruise_info` using the fetched `cruise_id`s.
- [X] T008 [US1] In `src/data_extraction/extractor.py`, implement a function to fetch date and price information from `mv_cruise_date_range_info` for a given list of `cruise_id`s.
- [X] T009 [US1] In `src/data_extraction/extractor.py`, implement a main function to orchestrate the data extraction and save the final data to a JSON file named `cruise_data.json`.

---

## Phase 4: User Story 2 - Semantic Transformation & Data Cleaning

**Goal**: Transform the extracted cruise data into a semantic format by generating descriptive text for each cruise attribute and cleaning the data.

**Independent Test**: The transformed data contains descriptive text for each cruise attribute and is clean.

- [X] T010 [US2] In `src/transformation/cleaner.py`, implement a function to remove HTML tags from a given text using `BeautifulSoup`.
- [X] T011 [US2] In `src/transformation/translator.py`, implement a function to translate a given text to English using `googletrans`. It should handle cases where the `en` localization is not available and try other localizations.
- [X] T012 [US2] In `src/transformation/semantic.py`, implement a function to generate a descriptive text for each cruise attribute based on the rules in `spec.md`.
- [X] T013 [US2] In `src/transformation/transformer.py`, implement a main function to orchestrate the data cleaning, translation, and semantic transformation.

---

## Phase 5: User Story 3 - Vector DB Creation

**Goal**: Create a Chroma vector database from the semantically enriched cruise data, with each cruise being a separate document.

**Independent Test**: A Chroma vector database is created and contains the cruise data.

- [X] T014 [US3] In `src/vector_db/creator.py`, implement a function to initialize a Chroma DB client.
- [X] T015 [US3] In `src/vector_db/creator.py`, implement a function to create a new collection in Chroma DB.
- [X] T016 [US3] In `src/vector_db/creator.py`, implement a function to add a single cruise document to the collection, including the `itineraries`, `dates`, and `prices` in the metadata.
- [X] T017 [US3] In `src/vector_db/main.py`, implement a main function to orchestrate the vector database creation process.

---

## Phase 6: User Story 4 - API Query

**Goal**: Query the vector database using a REST API endpoint.

**Independent Test**: The API endpoint returns relevant cruise information for a given query.

- [X] T018 [US4] In `src/api/main.py`, implement a FastAPI endpoint `/query` that accepts a POST request with a `query` field.
- [X] T019 [US4] In `src/api/main.py`, implement a function to query the Chroma vector database using the provided query.
- [X] T020 [US4] In `src/api/main.py`, implement the logic to return the query results in the format specified in `openapi.yaml`.

---

## Phase 7: Main Orchestration

- [X] T021 In `src/main.py`, implement the main orchestration logic to call the data extraction, transformation, and vector DB creation modules in the correct order.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T022 [P] Add comprehensive docstrings to all functions and modules.
- [ ] T023 [P] Add unit tests for all modules in the `tests/unit` directory.
- [ ] T024 [P] Add integration tests for the data extraction and API endpoints in the `tests/integration` directory.
- [ ] T025 Run `ruff check .` and `ruff format .` to ensure code quality.
