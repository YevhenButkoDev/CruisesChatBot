# Data Model: AI Chatbot for Cruise Search

This document outlines the key data entities for the AI Chatbot feature, based on the feature specification.

## Entity: Cruise

Represents a single cruise vacation option.

-   **Fields**:
    -   `cruise_id` (string, unique identifier)
    -   `destination` (string)
    -   `itinerary` (object or string)
    -   `sailing_dates` (list of date ranges)
    -   `ship_information` (object or string)
    -   `pricing` (object or string)
-   **Relationships**: None

## Entity: UserIntent

Represents the user's goal in the conversation.

-   **Fields**:
    -   `intent_id` (string, e.g., `find_cruise`, `ask_general_question`)
    -   `description` (string)
-   **Relationships**: A `Conversation` has one `UserIntent`.

## Entity: Conversation

Represents the dialogue between a user and the chatbot.

-   **Fields**:
    -   `conversation_id` (string, unique identifier)
    -   `user_id` (string, optional, for tracking conversations across sessions)
    -   `messages` (list of message objects)
    -   `current_intent` (UserIntent)
    -   `context` (object, to store information like destination and date range)
-   **Relationships**: None
