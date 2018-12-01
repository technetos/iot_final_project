-- Your SQL goes here
create table files (
  id SERIAL PRIMARY KEY NOT NULL,
  account_id UUID UNIQUE NOT NULL,
  fname TEXT NOT NULL UNIQUE,
  content TEXT NOT NULL
);
