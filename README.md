# Sprint_n_final_clean

API автотесты для сервиса «Доска».

## Запуск

```bash
pip3 install -r requirements.txt
pytest tests -v
```

В проекте оставлены только реальные endpoint'ы, подтверждённые через DevTools:
- регистрация: `/api/users` и `/api/register`
- логин: `/api/auth/login` и `/api/login`
- создание объявления: `POST /api/create-listing`
- получение объявления: `GET /api/listings/{id}`
- обновление объявления: `PATCH /api/update-offer/{id}`
- удаление объявления: `DELETE /api/listings/{id}`
