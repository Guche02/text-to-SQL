import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="D:\\Internship\\text-to-SQL\\application\\chroma")
collection = client.get_or_create_collection("sql_data")

embedder = SentenceTransformer("all-MiniLM-L6-v2")

schemas = [
    {
        "id": "table_actor",
        "text": """Table: actor
Purpose: Stores information about actors.
Columns:
- actor_id (SMALLINT UNSIGNED, Primary Key, Auto-increment) → Unique ID for each actor.
- first_name (VARCHAR, 45, NOT NULL) → Actor's first name.
- last_name (VARCHAR, 45, NOT NULL) → Actor's last name.
- last_update (TIMESTAMP, NOT NULL) → Last update timestamp of the actor's record.""",
        "metadata": {"type": "table", "name": "actor"}
    },
    {
        "id": "table_address",
        "text": """Table: address
Purpose: Stores address details for customers and locations.
Columns:
- address_id (SMALLINT UNSIGNED, Primary Key, Auto-increment) → Unique address identifier.
- address (VARCHAR, 50, NOT NULL) → Street address.
- address2 (VARCHAR, 50) → Secondary street address.
- district (VARCHAR, 20, NOT NULL) → District name.
- city_id (SMALLINT UNSIGNED, Foreign Key) → References city.city_id, linking the address to a city.
- postal_code (VARCHAR, 10) → Postal code.
- phone (VARCHAR, 20, NOT NULL) → Contact phone number.
- last_update (TIMESTAMP, NOT NULL) → Last update timestamp of the address.""",
        "metadata": {"type": "table", "name": "address"}
    },
    {
        "id": "table_category",
        "text": """Table: category
Purpose: Stores categories for films.
Columns:
- category_id (TINYINT UNSIGNED, Primary Key, Auto-increment) → Unique category ID.
- name (VARCHAR, 25, NOT NULL) → Category name (e.g., Action, Comedy).
- last_update (TIMESTAMP, NOT NULL) → Last update timestamp of the category.""",
        "metadata": {"type": "table", "name": "category"}
    },
    {
        "id": "table_city",
        "text": """Table: city
Purpose: Stores city details.
Columns:
- city_id (SMALLINT UNSIGNED, Primary Key, Auto-increment) → Unique city ID.
- city (VARCHAR, 50, NOT NULL) → Name of the city.
- country_id (SMALLINT UNSIGNED, Foreign Key) → References country.country_id, linking the city to a country.
- last_update (TIMESTAMP, NOT NULL) → Last update timestamp of the city.""",
        "metadata": {"type": "table", "name": "city"}
    },
    {
        "id": "table_country",
        "text": """Table: country
Purpose: Stores country details.
Columns:
- country_id (SMALLINT UNSIGNED, Primary Key, Auto-increment) → Unique country ID.
- country (VARCHAR, 50, NOT NULL) → Name of the country.
- last_update (TIMESTAMP, NOT NULL) → Last update timestamp of the country.""",
        "metadata": {"type": "table", "name": "country"}
    },
    {
        "id": "table_customer",
        "text": """Table: customer
Purpose: Stores customer details.
Columns:
- customer_id (SMALLINT UNSIGNED, Primary Key, Auto-increment) → Unique customer ID.
- store_id (TINYINT UNSIGNED, Foreign Key) → References store.store_id, linking to the store.
- first_name (VARCHAR, 45, NOT NULL) → Customer's first name.
- last_name (VARCHAR, 45, NOT NULL) → Customer's last name.
- email (VARCHAR, 50) → Customer's email address.
- address_id (SMALLINT UNSIGNED, Foreign Key) → References address.address_id, linking to the address.
- active (BOOLEAN, NOT NULL) → Indicates if the customer is active.
- create_date (DATETIME, NOT NULL) → Date the customer was created.
- last_update (TIMESTAMP) → Last update timestamp of the customer.""",
        "metadata": {"type": "table", "name": "customer"}
    },
    {
        "id": "table_film",
        "text": """Table: film
Purpose: Stores film details.
Columns:
- film_id (SMALLINT UNSIGNED, Primary Key, Auto-increment) → Unique film ID.
- title (VARCHAR, 128, NOT NULL) → Film's title.
- description (TEXT) → Description of the film.
- release_year (YEAR) → Year of release.
- language_id (TINYINT UNSIGNED, Foreign Key) → References language.language_id, linking to the language.
- original_language_id (TINYINT UNSIGNED, Foreign Key) → References language.language_id for the original language.
- rental_duration (TINYINT UNSIGNED, NOT NULL) → Rental duration in days.
- rental_rate (DECIMAL, 4,2) → Rental rate of the film.
- length (SMALLINT UNSIGNED) → Length of the film in minutes.
- replacement_cost (DECIMAL, 5,2) → Cost to replace the film.
- rating (ENUM, 'G', 'PG', 'PG-13', 'R', 'NC-17') → Film's rating.
- special_features (SET, 'Trailers', 'Commentaries', 'Deleted Scenes', 'Behind the Scenes') → Special features of the film.
- last_update (TIMESTAMP) → Last update timestamp of the film.""",
        "metadata": {"type": "table", "name": "film"}
    },
    {
        "id": "table_film_actor",
        "text": """Table: film_actor
Purpose: Links actors to films.
Columns:
- actor_id (SMALLINT UNSIGNED, Foreign Key) → References actor.actor_id, linking to the actor.
- film_id (SMALLINT UNSIGNED, Foreign Key) → References film.film_id, linking to the film.
- last_update (TIMESTAMP) → Last update timestamp of the film-actor record.""",
        "metadata": {"type": "table", "name": "film_actor"}
    },
    {
        "id": "table_language",
        "text": """Table: language
Purpose: Stores language details for the films.
Columns:
- language_id (TINYINT UNSIGNED, Primary Key, Auto-increment) → Unique ID for each language.
- name (CHAR, 20, NOT NULL) → Name of the language.
- last_update (TIMESTAMP, NOT NULL, Default CURRENT_TIMESTAMP) → Last time the language record was updated.""",
        "metadata": {"type": "table", "name": "language"}
    },
    {
        "id": "table_payment",
        "text": """Table: payment
Purpose: Stores payment transaction details.
Columns:
- payment_id (SMALLINT UNSIGNED, Primary Key, Auto-increment) → Unique ID for each payment.
- customer_id (SMALLINT UNSIGNED, Foreign Key) → References customer.customer_id, linking payment to a customer.
- staff_id (TINYINT UNSIGNED, Foreign Key) → References staff.staff_id, linking payment to a staff member.
- rental_id (INT, Foreign Key, NULL) → References rental.rental_id, linking payment to a rental.
- amount (DECIMAL, 5, 2, NOT NULL) → Amount of the payment.
- payment_date (DATETIME, NOT NULL) → Date and time when the payment was made.
- last_update (TIMESTAMP, Default CURRENT_TIMESTAMP) → Last time the payment record was updated.""",
        "metadata": {"type": "table", "name": "payment"}
    },
    {
        "id": "table_rental",
        "text": """Table: rental
Purpose: Stores rental transaction details.
Columns:
- rental_id (INT, Primary Key, Auto-increment) → Unique rental transaction identifier.
- rental_date (DATETIME, NOT NULL) → Date and time when the rental occurred.
- inventory_id (MEDIUMINT UNSIGNED, Foreign Key) → References inventory.inventory_id, linking rental to inventory.
- customer_id (SMALLINT UNSIGNED, Foreign Key) → References customer.customer_id, linking rental to a customer.
- return_date (DATETIME, NULL) → Date and time when the rental was returned.
- staff_id (TINYINT UNSIGNED, Foreign Key) → References staff.staff_id, linking rental to staff.
- last_update (TIMESTAMP, NOT NULL, Default CURRENT_TIMESTAMP) → Last time the rental record was updated.""",
        "metadata": {"type": "table", "name": "rental"}
    },
    {
        "id": "table_staff",
        "text": """Table: staff
Purpose: Stores information about staff members.
Columns:
- staff_id (TINYINT UNSIGNED, Primary Key, Auto-increment) → Unique ID for each staff member.
- first_name (VARCHAR, 45, NOT NULL) → First name of the staff member.
- last_name (VARCHAR, 45, NOT NULL) → Last name of the staff member.
- address_id (SMALLINT UNSIGNED, Foreign Key) → References address.address_id, linking staff to an address.
- picture (BLOB, NULL) → Profile picture of the staff member.
- email (VARCHAR, 50, NULL) → Email address of the staff member.
- store_id (TINYINT UNSIGNED, Foreign Key) → References store.store_id, linking staff to a store.
- active (BOOLEAN, NOT NULL, Default TRUE) → Status of the staff member's employment.
- username (VARCHAR, 16, NOT NULL) → Username for staff member login.
- password (VARCHAR, 40, NULL) → Password for staff member login.
- last_update (TIMESTAMP, NOT NULL, Default CURRENT_TIMESTAMP) → Last time the staff record was updated.""",
        "metadata": {"type": "table", "name": "staff"}
    },
    {
        "id": "table_store",
        "text": """Table: store
Purpose: Stores information about film rental stores.
Columns:
- store_id (TINYINT UNSIGNED, Primary Key, Auto-increment) → Unique ID for each store.
- manager_staff_id (TINYINT UNSIGNED, Foreign Key) → References staff.staff_id, linking store to its manager.
- address_id (SMALLINT UNSIGNED, Foreign Key) → References address.address_id, linking store to an address.
- last_update (TIMESTAMP, NOT NULL, Default CURRENT_TIMESTAMP) → Last time the store record was updated.""",
        "metadata": {"type": "table", "name": "store"}
    },
    {
        "id": "view_customer_list",
        "text": """View: customer_list
Purpose: Provides a list of customers along with their address, city, country, and store details.
Columns:
- ID (customer_id) → Unique customer ID.
- name → Concatenated first and last name of the customer.
- address → Address of the customer.
- zip code → Postal code of the customer.
- phone → Customer's contact number.
- city → City of the customer.
- country → Country of the customer.
- notes → Status of the customer (active or inactive).
- SID → Store ID to which the customer is linked.""",
        "metadata": {"type": "view", "name": "customer_list"}
    },
    {
        "id": "view_film_list",
        "text": """View: film_list
Purpose: Provides a list of films along with their categories, rental rate, and actors.
Columns:
- FID → Film ID.
- title → Title of the film.
- description → Description of the film.
- category → Category of the film.
- price → Rental price of the film.
- length → Length of the film.
- rating → Rating of the film.
- actors → List of actors in the film.""",
        "metadata": {"type": "view", "name": "film_list"}
    },
    {
        "id": "view_nicer_but_slower_film_list",
        "text": """View: nicer_but_slower_film_list
Purpose: Provides a formatted list of films with actor names capitalized.
Columns:
- FID → Film ID.
- title → Title of the film.
- description → Description of the film.
- category → Category of the film.
- price → Rental price of the film.
- length → Length of the film.
- rating → Rating of the film.
- actors → List of actors in the film with properly capitalized names.""",
        "metadata": {"type": "view", "name": "nicer_but_slower_film_list"}
    },
    {
        "id": "view_staff_list",
        "text": """View: staff_list
Purpose: Provides a list of staff members with associated details.
Columns:
- ID (INT) → Staff ID.
- name (VARCHAR) → Full name of the staff member.
- address (VARCHAR) → Address of the staff member.
- zip code (VARCHAR) → Postal code of the address.
- phone (VARCHAR) → Contact number of the staff member.
- city (VARCHAR) → City of the staff member's address.
- country (VARCHAR) → Country of the staff member's address.
- SID (INT) → Store ID where the staff is working.""",
        "metadata": {"type": "view", "name": "staff_list"}
    },
    {
        "id": "view_sales_by_store",
        "text": """View: sales_by_store
Purpose: Provides total sales per store, including store location and manager details.
Columns:
- store (VARCHAR) → Store location combining city and country.
- manager (VARCHAR) → Full name of the store manager.
- total_sales (DECIMAL) → Total sales made by the store.""",
        "metadata": {"type": "view", "name": "sales_by_store"}
    },
    {
        "id": "view_sales_by_film_category",
        "text": """View: sales_by_film_category
Purpose: Provides total sales for each film category.
Columns:
- category (VARCHAR) → Film category name.
- total_sales (DECIMAL) → Total sales for that category.""",
        "metadata": {"type": "view", "name": "sales_by_film_category"}
    },
    {
        "id": "view_actor_info",
        "text": """View: actor_info
Purpose: Provides detailed information about actors, including their films and categories.
Columns:
- actor_id (INT) → Unique actor ID.
- first_name (VARCHAR) → First name of the actor.
- last_name (VARCHAR) → Last name of the actor.
- film_info (TEXT) → List of film categories and the films in those categories.""",
        "metadata": {"type": "view", "name": "actor_info"}
    }
]

for schema in schemas:
    embedding = embedder.encode(schema["text"]).tolist()  # Convert text to embedding
    collection.add(
        ids=[schema["id"]],
        embeddings=[embedding],
        metadatas=[schema["metadata"]],
        documents=[schema["text"]]
    )

print("Schema updated successfully!")