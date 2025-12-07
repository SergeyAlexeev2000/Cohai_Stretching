# app/api/v1/admin_leads.py

"""
Backward-compatibility shim.

Старый модуль, оставленный для совместимости с кодом и тестами,
которые импортируют `app.api.v1.admin_leads`.

Настоящая реализация теперь лежит в `app.api.v1.admin.admin_leads`.
"""

from .admin.admin_leads import *  # noqa: F401,F403
