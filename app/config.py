class Config:
    DEBUG: bool
    HOST: str = '127.0.0.1'
    PORT: int = '8080'
    DATABASE_USER = 'postgres'
    DATABASE_PASSWORD = 'example'
    DATABASE_URI: str = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@localhost:5432/postgres'
