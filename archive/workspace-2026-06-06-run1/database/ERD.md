# Entity-Relationship Diagram Overview

The persistence layer for the Wilder backend is designed to be simple, clean, and pragmatic. Given the requirements from the product specification, the data model is centered around a single core entity: `Location`.

## Entities

### `Location`

This entity represents a geographical place that can be displayed on the website. It contains all the necessary attributes to be shown as a "Featured Location," a pin on the "Interactive Map," or both.

**Attributes:**

*   `id`: A unique identifier for the location.
*   `name`: The display name of the location (e.g., "Whispering Pines Forest").
*   `description`: An evocative sentence describing the location.
*   `image_url`: The path to a representative image.
*   `latitude`: The geographical latitude for placing a pin on the map.
*   `longitude`: The geographical longitude for placing a pin on the map.
*   `is_featured`: A boolean flag to determine if the location should be prominently displayed in the "Featured Locations" section.
*   `created_at`: The timestamp when the record was created.
*   `updated_at`: The timestamp of the last modification.

## Relationships

In the current design, there is only one table, `locations`. Therefore, there are no inter-table relationships. This flat structure is highly efficient for the current scope, allowing for fast queries to fetch all necessary data for the frontend in a single request.

## Schema Diagram

```
+------------------+
|    locations     |
+------------------+
| id (PK)          |
| name             |
| description      |
| image_url        |
| latitude         |
| longitude        |
| is_featured      |
| created_at       |
| updated_at       |
+------------------+
```
