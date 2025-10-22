# Tasks: AI Chatbot for Cruise Search

**Input**: Design documents from `/specs/002-this-is-a/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/

**Tests**: Included as requested by the "Independent Test" sections in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for the new chatbot feature.

- [x] T-pre-001 [P] Create a virtual environment named `venv`
- [x] T-pre-002 [P] Downgrade NumPy to a version compatible with chromadb
- [x] T000 [P] Install dependencies from `requirements.txt`
- [x] T001 [P] Create a new directory `src/chatbot` for the new chatbot logic.
- [x] T002 [P] Create an empty `src/chatbot/__init__.py` file.
- [x] T003 [P] Create an empty `src/chatbot/models.py` file for Pydantic models.
- [x] T004 [P] Create an empty `src/chatbot/services.py` file for the conversation logic.
- [x] T005 [P] Create an empty `tests/unit/test_chatbot_service.py` file.
- [x] T006 [P] Create an empty `tests/integration/test_api.py` file.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

- [x] T007 [US1] In `src/chatbot/models.py`, define the Pydantic models from the OpenAPI spec: `ChatMessage`, `ChatResponse`, and `Cruise`.
- [x] T008 [US1] In `src/api.py`, add a new placeholder `/chat` endpoint that imports and calls a function from `src/chatbot/services.py`.

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Find a Cruise with Specific Dates (Priority: P1) 🎯 MVP

**Goal**: A user can ask the chatbot to find a cruise for a specific destination and date, and the chatbot will return relevant results.

**Independent Test**: A user can start a conversation, provide a destination and date, and receive a list of cruises.

### Tests for User Story 1 ⚠️

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] In `tests/unit/test_chatbot_service.py`, write a unit test to verify that the chatbot correctly identifies the user's intent to "find_cruise".
- [x] T010 [P] [US1] In `tests/unit/test_chatbot_service.py`, write a unit test to verify that the chatbot asks for a destination if the intent is "find_cruise".
- [x] T011 [P] [US1] In `tests/unit/test_chatbot_service.py`, write a unit test to verify that the chatbot asks for a date range after a destination is provided.

### Implementation for User Story 1

- [x] T012 [US1] In `src/chatbot/services.py`, implement the basic conversation flow: receive a message, identify the "find_cruise" intent, and respond by asking for a destination.
- [x] T013 [US1] In `src/chatbot/services.py`, enhance the conversation flow to ask for a date range after the destination is provided.
- [x] T014 [US1] In `src/chatbot/services.py`, implement the logic to query the ChromaDB using the collected destination and date range.
- [x] T015 [US1] In `src/api.py`, update the `/chat` endpoint to pass the user's message to the chatbot service and return the response.

### Integration Tests for User Story 1 ⚠️

- [x] T016 [US1] In `tests/integration/test_api.py`, write an integration test that simulates a full conversation for finding a cruise via the `/chat` endpoint.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Find a Cruise with Flexible Dates (Priority: P2)

**Goal**: A user can find a cruise for a specific destination without providing a date, and the chatbot will search for cruises in the next year.

**Independent Test**: A user can provide a destination and indicate that the date is not important, and the chatbot will return relevant cruises for the next year.

### Tests for User Story 2 ⚠️

- [x] T017 [P] [US2] In `tests/unit/test_chatbot_service.py`, add a test case to verify that if the user doesn't specify a date, the chatbot searches for cruises in the next year.

### Implementation for User Story 2

- [x] T018 [US2] In `src/chatbot/services.py`, modify the conversation logic to handle cases where the user indicates a flexible date, defaulting the search to the next calendar year.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Ask a General Question (Priority: P3)

**Goal**: A user can ask a general question and receive a direct answer from the chatbot.

**Independent Test**: A user can ask "What is the luggage allowance?" and receive a correct, predefined answer.

### Tests for User Story 3 ⚠️

- [x] T019 [P] [US3] In `tests/unit/test_chatbot_service.py`, add a test case to verify that the chatbot can answer a general question.

### Implementation for User Story 3

- [x] T020 [US3] In `src/chatbot/services.py`, implement a simple mechanism to identify and answer general questions from a predefined set of Q&A pairs.

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [x] T021 [P] Add robust error handling to the `/chat` endpoint for scenarios like the vector database being unavailable.
- [x] T022 [P] Review and refine all chatbot responses for clarity and user-friendliness.
- [ ] T023 Run `ruff check .` and `ruff format .` to ensure code quality and consistency.
- [ ] T024 Validate the feature by following the steps in `quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup.
- **User Stories (Phases 3-5)**: Depend on Foundational. User stories can be implemented sequentially (P1 -> P2 -> P3) or in parallel if resources allow.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Parallel Opportunities

- Within Phase 1, all tasks are parallelizable.
- Within each user story's testing phase, tests for different aspects can be written in parallel.
- Once the Foundational phase is complete, work on different user stories can happen in parallel.
