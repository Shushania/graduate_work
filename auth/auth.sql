CREATE TABLE public.users (
    id uuid PRIMARY KEY,
    login TEXT NOT NULL,
    password TEXT NOT NULL,
    creation_date DATE,
    is_superuser Bool
);

CREATE TABLE public.roles (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE public.users_roles (
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES public.users (id)
    ON DELETE CASCADE,
    role_id uuid NOT NULL REFERENCES public.roles (id)
    ON DELETE CASCADE
);

CREATE TABLE public.user_history (
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES public.users (id)
    ON DELETE CASCADE,
    user_agent TEXT,
    ip_address TEXT,
    auth_datetime timestamp with time zone
);