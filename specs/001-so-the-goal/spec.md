# Feature Specification: Cruise Info Vector DB Creator

**Feature Branch**: `001-so-the-goal`
**Created**: 2025-10-12
**Status**: Draft
**Input**: User description: "so the goal of this project is to collect data from a postgres db, the goal is to collect data from a material view and create a json with collected data, i will tell you which data to collect, the material view itself is just a view with cruise_id, enabled flag, and cruise_info jsonb field, the goal is to get correct data from cruise_info, so then once data is collected into json file, i need to create a vector db for this data, note that in order to make data more semantic reach i need to exaplin in text details about the data, for example if i will create a chunk with data for cities, i will not just specify cities in comma separated format, but i will mention in text that 'The cruise visits such cities: city1, city2, etc' if for example i need to specify the cruise category 'sea' i will not just mention 'category: sea' i will create a full sentence 'the cruise has 'sea' category which means it goes through the sea', the vector db should be used chroma, also every chunk of data should be a separate cruise info, so in one chunk there should be no othe cruises just 1, i am not sure on which step i need you to tell which data to collect, so ask me by yourself"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Data Extraction (Priority: P1)

As a developer, I want to extract cruise information from a Postgres materialized view and save it as a JSON file.

**Why this priority**: This is the first step in the data processing pipeline.

**Independent Test**: The JSON file is created and contains the correct data from the materialized view.

**Acceptance Scenarios**:

1. **Given** a connection to the Postgres database, **When** the extraction process is run, **Then** a JSON file is created with the cruise data.
2. **Given** the materialized view contains 10 enabled cruises, **When** the extraction process is run, **Then** the JSON file contains 10 cruise records.

---

### User Story 2 - Semantic Transformation (Priority: P2)

As a developer, I want to transform the extracted cruise data into a semantic format by generating descriptive text for each cruise attribute.

**Why this priority**: This step is crucial for creating a meaningful vector database.

**Independent Test**: The transformed data contains descriptive text for each cruise attribute.

**Acceptance Scenarios**:

1. **Given** a JSON file with cruise data, **When** the transformation process is run, **Then** the output contains descriptive text for each cruise attribute.

---

### User Story 3 - Vector DB Creation (Priority: P3)

As a developer, I want to create a Chroma vector database from the semantically enriched cruise data, with each cruise being a separate document.

**Why this priority**: This is the final goal of the project.

**Independent Test**: A Chroma vector database is created and contains the cruise data.

**Acceptance Scenarios**:

1. **Given** the semantically enriched cruise data, **When** the vector DB creation process is run, **Then** a Chroma vector database is created with each cruise as a separate document.

---

### User Story 4 - API Query (Priority: P4)

As a user, I want to be able to query the vector database using a REST API endpoint.

**Why this priority**: This provides a way to interact with the created vector database.

**Independent Test**: The API endpoint returns relevant cruise information for a given query.

**Acceptance Scenarios**:

1. **Given** a running API and a vector database with cruise information, **When** a query is sent to the `/query` endpoint, **Then** the API returns a list of relevant cruise information.

---

### Edge Cases

- What happens when the materialized view is empty?
- How does the system handle errors during database connection?
- What if the `cruise_info` JSONB field is missing some of the expected fields?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST connect to a Postgres database.
- **FR-002**: The system MUST read data from a materialized view named `mv_cruise_info`.
- **FR-003**: The system MUST extract `cruise_id`, `enabled`, and `cruise_info` for each cruise.
- **FR-004**: The system MUST filter out cruises where `enabled` is true.
- **FR-005**: The system MUST extract the following fields from the `cruise_info` JSONB field: `cruise:name_i18n:en`, `cruise:cruise_id`, `cruise:description`, `cruise:simple_itinerary_description`, `rivers(json array)[]:name_i18n:en`, `rivers[]:description_i18n:en`, `portMaybe:name_i18n:en`, `portMaybe:description_i18n:en`, `portMaybe:country_gen_i18n:en`, `itineraries[]:city:name_i18n:en`, `itineraries[]:city:country_name_i18n`, `itineraries[]:city:country_description_i18n`, `itineraries[]:city:description_i18n`, `lastPortMaybe:name_i18n:en`, `lastPortMaybe:country_name_i18n:en`, `lastPortMaybe:description_i18n:en`, `cruiseCategories[]:name_i18n:en`, `cruiseCategories[]:description_i18n:en`, `cruiseCategoryType:name_i18n:en`.
- **FR-006**: The system MUST generate a descriptive text for each extracted field.
- **FR-007**: The system MUST create a single text chunk for each cruise, combining all the descriptive texts.
- **FR-008**: The system MUST save the extracted and transformed data into a JSON file.
- **FR-009**: The system MUST use the generated text chunks to create a Chroma vector database.
- **FR-010**: Each cruise MUST be a separate document in the vector database.
- **FR-011**: The system MUST be written in Python.
- **FR-012**: The system MUST provide a REST API written in FastAPI.
- **FR-013**: The API MUST have a single endpoint named `/query`.
- **FR-014**: The `/query` endpoint MUST accept a text query as input.
- **FR-015**: The `/query` endpoint MUST query the Chroma vector database and return the most relevant cruise information.
- **FR-016**: The system MUST remove any HTML tags from the extracted text fields.
- **FR-017**: If the en localization is not available for a field, the system MUST try the following localizations in order: de, ru, uk, pl, hy.
- **FR-018**: If a non-english value is used, the system MUST translate the value into English using a free Python library.
- **FR-019**: The system MUST fetch data from the materialized view in batches of 10 cruises at a time.
- **FR-020**: The `itineraries` data MUST be included in the metadata of the Chroma DB chunk.
- **FR-021**: The `date_start`, `date_end`, and `price_min` MUST be included in the metadata of the Chroma DB chunk.
- **FR-022**: To get the date and price information, the system MUST join the `mv_cruise_date_range_info` materialized view by `cruise_id`.
- **FR-023**: The date and price information is located in the `cruise_date_range_info` JSONB column.
- **FR-024**: The `price_min` is located at the JSON path `minPrice:2`.
- **FR-025**: The `date_start` is located at the JSON path `dateRange:begin_date`.
- **FR-026**: The `date_end` is located at the JSON path `dateRange:end_date`.
- **FR-027**: The dates MUST be stored in the metadata as a JSON array of objects, with each object having `begin_date` and `end_date` keys.
- **FR-028**: The prices MUST be stored in the metadata as an array of numbers.

### Key Entities *(include if feature involves data)*

- **Cruise**: Represents a cruise with a unique ID, an enabled status, and detailed information in a JSONB field.
- **CruiseInfoChunk**: A text chunk representing a single cruise, containing semantically enriched information about the cruise.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The system can successfully connect to the Postgres database and read from the materialized view.
- **SC-002**: The system correctly extracts and transforms the cruise data into semantic text chunks.
- **SC-003**: A Chroma vector database is successfully created with each cruise as a separate document.