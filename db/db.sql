CREATE DATABASE erpdb;

\c erpdb;

CREATE TABLE user_ (
  id_user SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  first_name VARCHAR(50),
  email VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ,
  last_login_at TIMESTAMPTZ
);

CREATE TABLE roles (
  id_role SERIAL PRIMARY KEY,
  libelle VARCHAR(50) NOT NULL,
  description VARCHAR(50)
);

CREATE TABLE permissions (
  id_permission SERIAL PRIMARY KEY,
  code VARCHAR(50) NOT NULL,
  description VARCHAR(50)
);

CREATE TABLE user_roles (
  id_user INT NOT NULL,
  id_role INT NOT NULL,
  PRIMARY KEY (id_user, id_role),
  FOREIGN KEY (id_user) REFERENCES user_(id_user) ON DELETE CASCADE,
  FOREIGN KEY (id_role) REFERENCES roles(id_role) ON DELETE CASCADE
);

CREATE TABLE role_permissions (
  id_role INT NOT NULL,
  id_permission INT NOT NULL,
  PRIMARY KEY (id_role, id_permission),
  FOREIGN KEY (id_role) REFERENCES roles(id_role) ON DELETE CASCADE,
  FOREIGN KEY (id_permission) REFERENCES permissions(id_permission) ON DELETE CASCADE
);