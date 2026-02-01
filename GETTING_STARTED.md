# Начало работы с проектом DreamTeams

Пошаговая инструкция для начала работы над проектом (Windows).
Я создал для каждого из команды задачу по ознакомлению с проектом, после того, как прочтете инструкцию, отметьте это в таск-трекере (Todoist)

## Шаг 1. Регистрация на GitHub

1. Перейдите на https://github.com
2. Зарегистрируйтесь и подтвердите email, ознакомьтесь с платформой
3. Пришлите тимлиду ссылку на свой гитхаб профиль для добавления вас в приватный репозиторий
4. Дождитесь добавления в приватный репозиторий
5. Перейдите на страницу [репозитория](https://github.com/lubaskinc0de/dreamteams)

## Шаг 2. Установка необходимых программ

Установите следующие программы по порядку:

1. **Git** (система контроля версий кода)
   - Скачайте: https://git-scm.com/download/win
   - Инструкция по установке: https://git-scm.com/book/ru/v2/Введение-Установка-Git

2. **Docker Desktop** (для запуска проекта в изолированном окружении)
   - Скачайте: https://www.docker.com/products/docker-desktop
   - Инструкция: https://docs.docker.com/desktop/install/windows-install/
   - После установки перезагрузите компьютер и запустите программу Docker Desktop

3. **Just** (инструмент для упрощения ввода команд)
   - Скачайте последнюю версию (используйте инструкции по установке): https://github.com/casey/just

4. **VS Code** (редактор кода)
   - Скачайте: https://code.visualstudio.com/
   - Установите необходимые расширения для упрощения работы с кодом: Python, Ruff, GitLens, Mypy, Python, Pylance, Yaml

## Шаг 3. Изучение основ Git

**Обязательно** ознакомьтесь с главами 1-3 Pro Git Book на русском:
- https://git-scm.com/book/ru/v2

Это займет 1-2 часа, но сэкономит вам десятки часов в будущем.

Минимум, который нужно понимать:
- Что такое коммит, ветка, remote
- Команды: `clone`, `add`, `commit`, `push`, `pull`, `checkout`
- Как работает `.gitignore`

## Шаг 4. Клонирование репозитория

1. Откройте **Git Bash**, либо же просто откройте терминал на рабочем столе и вводите команды

2. Перейдите в папку, где хотите разместить проект:
   ```bash
   cd ~/Desktop  # или любая другая папка
   ```

3. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/USERNAME/dreamteams.git
   cd dreamteams
   ```

4. Настройте Git:
   ```bash
   git config --global user.name "Ваше Имя"
   git config --global user.email "your.email@example.com"
   ```

## Шаг 5. Первый запуск проекта
0. Подготовьте рабочее окружении, введите следующие команды в терминал vscode (должен быть открыт корень проекта)
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser # ВАЖНО: выполните эту команду отдельно в программе PowerShell, чтобы можно было активировать виртуальное окружение
pip install uv  # устанавливаем более быструю альтернативу pip
uv venv  # создаем виртуальное окружение для установки пакетов
.venv\Scripts\activate.bat # активируем его
just dev-environment  # устанавливаем пакеты
```

1. Убедитесь, что **Docker Desktop запущен** (иконка в трее)

2. В терминале VSCode выполните:
   ```bash
   just up
   ```
   Первый запуск займет 10-15 минут - Docker скачает все необходимые образы.

3. Откройте в браузере:
   - **API документация**: http://localhost/docs
   - **Главная страница**: http://localhost/

4. Остановите проект (когда закончите работу):
   ```bash
   just down
   ```

## Шаг 6. Структура проекта

### Backend (Python)

```
src/dreamteams/
├── entities/        # Доменные модели (User, Organizer, Competition)
│                    # Не импортирует другие слои
├── application/     # Бизнес-логика (use cases / interactors)
│                    # Не импортирует adapters, presentation, bootstrap
├── adapters/        # Работа с БД, внешними API
│                    # Не импортирует presentation, bootstrap
├── presentation/    # HTTP API (FastAPI роутеры)
│                    # Не импортирует bootstrap
└── bootstrap/       # Запуск приложения, DI, конфигурация
```

**Важно**: слои имеют строгие правила импортов (почитайте про модули и пакеты в языке python), которые проверяются `import-linter`, направление зависимостей в коде регламентируется правилами Чистой Архитектуры - кратко почитайте про это.

## Шаг 7. Внесение изменений

### 7.1. Создание ветки для задачи

**Всегда** создавайте отдельную ветку для своих изменений:

```bash
# Убедитесь, что находитесь на актуальной dev
git checkout dev  # перейти в ветку dev - тут идет вся работа
git pull  # подтянуть последние изменения кода из репозитория

# Создайте новую ветку (название описывает задачу)
git checkout -b feature/add-user-avatar
# или
git checkout -b fix/competition-date-validation
```

### 7.2. Где менять код

**Для новой функциональности:**

1. **Доменная модель** → `src/dreamteams/entities/`
2. **Бизнес-логика (интерактор)** → `src/dreamteams/application/{feature}/`
3. **Работа с БД** → `src/dreamteams/adapters/db/gateway/` и `models/`
4. **HTTP API** → `src/dreamteams/presentation/fast_api/routers/`
5. **Тесты** → ``tests//`` (вам следует ознакомиться с pytest)

### 7.3. Стиль кода и проверки

Проект использует строгие правила:

**Python:**
- **Форматирование**: Ruff (автоформат)
- **Типизация**: mypy в strict режиме
- **Архитектура**: import-linter (проверяет зависимости между слоями)

**Перед коммитом ОБЯЗАТЕЛЬНО**:

```bash
# Автоматически исправить форматирование и простые ошибки
just lint

# Запустить тесты
just test
```

**Если `just lint` выдает ошибки:**
- Ruff ошибки: изучите вывод, исправьте код
- mypy ошибки: добавьте типы, исправьте несоответствия типов
- import-linter: вы импортируете слой, который нельзя импортировать (см. `.importlinter`)

**Правила типизации:**
- Все функции должны иметь типы аргументов и возвращаемого значения
- Не используйте `Any` без крайней необходимости

**Правило архитектуры (важно!):**
- `entities` НЕ импортирует ничего из других слоев
- `application` НЕ импортирует `adapters`, `presentation`, `bootstrap`
- `adapters` НЕ импортирует `presentation`, `bootstrap`
- Нарушение = тест не пройдет

### 7.4. Тестирование

**Запуск всех тестов:**
```bash
just test  # Интеграционные тесты в Docker
```

**Запуск конкретного теста:**
```bash
# Сначала установите окружение локально
just dev-environment

# Запустите unit-тесты
just test-unit

# Или запустите конкретный тест
pytest tests/integration/manage_profile/test_update_profile.py -v
```

**Пишите тесты для новой функциональности:**
- Используйте фабрики из `tests/common/factory/`
- Смотрите примеры в `tests/integration/`

### 7.5. Коммиты

**Правила коммитов:**

**Формат сообщения коммита:**
```
<тип>(<область>): краткое описание

Примеры:
feat(user): add avatar upload functionality
fix(competition): fix date validation bug
refactor(auth): simplify JWT token validation
test(profile): add tests for profile update
docs(readme): update installation instructions
```

**Типы коммитов:**
- `feat` - новая функциональность
- `fix` - исправление бага
- `refactor` - рефакторинг без изменения функциональности
- `test` - добавление/изменение тестов
- `docs` - документация
- `style` - форматирование кода

### 7.6. Отправка на GitHub

```bash
# Отправить ветку на GitHub
git push origin feature/add-user-avatar
```

### 7.7. Создание Pull Request

1. Откройте GitHub в браузере: https://github.com/USERNAME/dreamteams
2. Появится уведомление "Compare & pull request" - нажмите
3. Заполните описание PR
4. Нажмите "Create pull request"
5. Дождитесь прохождения CI (GitHub Actions) - зеленая галочка
6. Дождитесь ревью и внесите правки, если потребуется

## Шаг 8. Синхронизация с основной веткой

Периодически обновляйте свою ветку:

```bash
# Переключитесь на dev
git checkout dev

# Получите последние изменения
git pull origin

# Вернитесь в свою ветку
git checkout feature/add-user-avatar

# Влейте изменения из master
git rebase dev

# Если есть конфликты - разрешите их и продолжите:
# 1. Откройте файлы с конфликтами в VS Code
# 2. Разрешите конфликты
# 3. git add .
# 4. git rebase --continue
```

## Частые проблемы

**mypy ошибки "Missing type annotation"**
- Добавьте типы ко всем функциям: `def foo(x: int) -> str:`
- Изучите документацию mypy: https://mypy.readthedocs.io/

**import-linter ошибки**
- Вы нарушаете архитектурные правила
- Проверьте файл `.importlinter` - там описаны запрещенные импорты
- Перенесите код в правильный слой

## Полезные ссылки

**Обязательно к изучению:**
- **Git Book (русский)**: https://git-scm.com/book/ru/v2 - главы 1-3
- **GitHub Flow**: https://docs.github.com/ru/get-started/quickstart/github-flow

**Документация технологий:**
- **Python typing**: https://docs.python.org/3/library/typing.html
- **FastAPI**: https://fastapi.tiangolo.com/ru/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Dishka (DI)**: https://dishka.readthedocs.io/
- **Pytest**: https://docs.pytest.org/

**Clean Architecture:**
- Статья на Хабре: https://habr.com/ru/company/mobileup/blog/335382/
- Книга "Clean Architecture" (Роберт Мартин)

## Чеклист перед отправкой кода

- [ ] Код отформатирован: `just lint` прошел без ошибок
- [ ] Все тесты проходят: `just test` успешен
- [ ] Добавлены тесты для новой функциональности
- [ ] Типы указаны везде (mypy strict mode)
- [ ] Не нарушены правила архитектуры (import-linter)
- [ ] Коммит имеет понятное сообщение
- [ ] PR имеет описание изменений
