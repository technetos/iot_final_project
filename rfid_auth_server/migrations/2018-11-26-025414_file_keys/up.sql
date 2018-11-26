-- YOUR SQL GOES HERE
create table file_keys (
  id SERIAL PRIMARY KEY NOT NULL,
  account_id UUID UNIQUE NOT NULL,
  fname TEXT NOT NULL UNIQUE,
  key TEXT NOT NULL
);
