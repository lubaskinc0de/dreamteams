# API Integration

## URLs

**API Base:** `/api`
**OAuth Base:** `/oauth2`

---

## Authentication

### Check Status

**GET** `/oauth2/auth`

Проверяет аутентифицирован ли пользователь.

**Responses:**
- `200` — пользователь аутентифицирован
- `401` — не аутентифицирован

### Sign In

Перенаправить пользователя на `/oauth2/sign_in?rd={redirect_url}`

**Parameters:**
- `rd` — URL для редиректа после успешной аутентификации

**Пример:** `/oauth2/sign_in?rd=/`

**Процесс:**
1. Пользователь нажимает "Войти"
2. Редирект на `/oauth2/sign_in?rd=/`
3. Бекенд обрабатывает OAuth flow с Keycloak
4. После успешной аутентификации редирект на URL из параметра `rd`

### Sign Out

**GET** `/oauth2/sign_out?rd={redirect_url}`

**Parameters:**
- `rd` — URL для редиректа после выхода

---

## Endpoints

### Register as Organizer

**POST** `/api/organizers/`

**Auth:** required

**Request:**
```json
{
  "organizer_name": "string",
  "phone_number": "string"
}
```

**Validation:**
- `organizer_name` — максимум 70 символов
- `phone_number` — российский формат `+7XXXXXXXXXX`

**Response 200:**
```json
{
  "organizer_id": "uuid",
  "user_id": "uuid"
}
```

**Errors:**
- `401 UNAUTHORIZED` — не аутентифицирован
- `409 AUTH_USER_ALREADY_EXISTS` — уже зарегистрирован как организатор
- `409 ORGANIZER_ALREADY_EXISTS` — телефон или email уже используется
- `422 VALIDATION_ERROR` — невалидные данные

**Notes:**
- `contact_email` берется автоматически из email аутентифицированного пользователя

---

### View Profile

**GET** `/api/users/me`

**Auth:** required

**Response 200:**
```json
{
  "user_id": "uuid",
  "organizer": {
    "id": "uuid",
    "user_id": "uuid",
    "organizer_name": "string",
    "phone_number": "string",
    "contact_email": "string",
    "logo": "string | null"
  } | null
}
```

**Errors:**
- `401 UNAUTHORIZED` — не аутентифицирован
- `404 USER_HAS_NO_ROLE` — пользователь не имеет роли

**Notes:**
- `organizer` = `null` если пользователь не зарегистрирован как организатор
- В данный момент доступна только роль организатора

---

## Error Format

Все ошибки имеют единый формат:

```json
{
  "code": "ERROR_CODE",
  "message": "Описание ошибки"
}
```

### Error Codes

| HTTP | Code | Описание |
|------|------|----------|
| 401 | `UNAUTHORIZED` | Не аутентифицирован |
| 404 | `USER_HAS_NO_ROLE` | Нет назначенной роли |
| 409 | `AUTH_USER_ALREADY_EXISTS` | Уже зарегистрирован |
| 409 | `ORGANIZER_ALREADY_EXISTS` | Телефон/email занят |
| 422 | `VALIDATION_ERROR` | Невалидные данные |

