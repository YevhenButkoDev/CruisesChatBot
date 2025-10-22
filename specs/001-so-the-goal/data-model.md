# Data Model

**Date**: 2025-10-12

## Entities

### Cruise

Represents a cruise with a unique ID, an enabled status, and detailed information in a JSONB field.

**Attributes**:

-   `cruise_id`: string (unique identifier)
-   `enabled`: boolean
-   `cruise_info`: JSONB

### CruiseInfoChunk

A text chunk representing a single cruise, containing semantically enriched information about the cruise.

**Attributes**:

-   `cruise_id`: string
-   `chunk_text`: string
