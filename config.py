import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_DEFAULT_SECRET_KEY = 'mq-professional-intranet-secure-token-2026'


class Config:
    DATABASE_URL = os.environ.get('DATABASE_URL', '')  # PostgreSQL (Neon) em produção
    DATABASE = os.environ.get('SQLITE_PATH', os.path.join(BASE_DIR, 'intranet.db'))  # SQLite em dev local
    USE_POSTGRES = bool(DATABASE_URL)

    IS_PRODUCTION = os.environ.get('FLASK_ENV', 'development') == 'production'
    DEBUG = not IS_PRODUCTION
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5080))

    SECRET_KEY = os.environ.get('SECRET_KEY', _DEFAULT_SECRET_KEY)

    # Cookies de sessão endurecidos em produção (HTTPS na Vercel)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = IS_PRODUCTION


if Config.IS_PRODUCTION and Config.SECRET_KEY == _DEFAULT_SECRET_KEY:
    # A chave padrão está no repositório: com ela qualquer pessoa forja uma sessão de admin.
    raise RuntimeError('SECRET_KEY não configurada. Defina a variável de ambiente SECRET_KEY em produção.')
