-- Создание отдельной схемы для контента
CREATE SCHEMA IF NOT EXISTS content;

-- Создание таблицы, в которой будут содержаться жанры фильмов
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

-- Создание таблицы, в которой будет содержаться информация о фильмах
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title VARCHAR (255) NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating FLOAT,
    type TEXT NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
); 

-- Создание таблицы, в которой будут содержаться участники фильмов
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name VARCHAR (255) NOT NULL,
    birth_date DATE,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

-- Создание таблицы, связывающей жанры и фильмы
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created_at timestamp with time zone,
    CONSTRAINT unique_genre_film_work UNIQUE (film_work_id, genre_id),
    FOREIGN KEY (film_work_id) REFERENCES content.film_work (id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (genre_id) REFERENCES content.genre (id) DEFERRABLE INITIALLY DEFERRED
);

-- Создание таблицы, связывающей персоны и фильмы
CREATE TABLE content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role VARCHAR (50) NOT NULL,
    created_at timestamp with time zone,
    CONSTRAINT unique_role_person_film_work UNIQUE (film_work_id, person_id, role),
    FOREIGN KEY (film_work_id) REFERENCES content.film_work (id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (person_id) REFERENCES content.person (id) DEFERRABLE INITIALLY DEFERRED
);