backend/
└── app/
    ├── main.py
    │
    ├── core/
    │   ├── config.py
    │   ├── database.py
    │   └── security.py
    │
    ├── models/
    │   ├── __init__.py
    │   ├── users/
    │   │   └── user.py
    │   ├── roles/
    │   │   └── role.py
    │   ├── permissions/
    │   │   └── permission.py
    │   └── authentication/
    │
    ├── schemas/
    │   ├── __init__.py
    │   ├── users/
    │   │   └── user.py
    │   ├── roles/
    │   │   └── role.py
    │   ├── permissions/
    │   │   └── permission.py
    │   └── authentication/
    │       └── login.py
    │
    ├── api/
    │   ├── __init__.py
    │   └── routes/
    │       ├── __init__.py
    │       ├── users/
    │       │   └── user.py
    │       ├── roles/
    │       │   └── role.py
    │       ├── permissions/
    │       │   └── permission.py
    │       └── authentication/
    │           └── auth.py
    │
    └── services/
        ├── __init__.py
        ├── users/
        │   └── user.py
        ├── roles/
        │   └── role.py
        ├── permissions/
        │   └── permission.py
        └── authentication/
            └── auth.py

models/       → structure DB
schemas/      → données API
routes/       → endpoints HTTP
services/     → logique métier