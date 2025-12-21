/**
 * UI text constants for the application
 * This file serves as a centralized location for all UI strings
 * and will be replaced with i18n translation keys in the future
 *
 * Structure follows the planned i18n locale file format
 */
export const UI_TEXT = {
  common: {
    loading: "Загрузка...",
    submit: "Отправить",
    cancel: "Отмена",
    save: "Сохранить",
    delete: "Удалить",
    edit: "Редактировать",
    close: "Закрыть",
    back: "Назад",
    next: "Далее",
    confirm: "Подтвердить",
    personalAccount: "Личный кабинет",
  },

  nav: {
    home: "Главная",
    profile: "Профиль",
    register: "Регистрация",
    brand: "Посуточник",
    brandSubtitle: "Автоматизация аренды",
  },

  home: {
    headline: "Автоматизация краткосрочной аренды",
    title: "Посуточник",
    description:
      "Платформа для автоматизации управления краткосрочной арендой для частных арендодателей. Решает проблему двойного бронирования, синхронизируя календари с популярными площадками.",
    registerButton: "Зарегистрироваться как арендодатель",
    profileButton: "Перейти в профиль",
    featuresTitle: "Основные возможности",
    featuresDescription:
      "Всё необходимое для эффективного управления краткосрочной арендой",
    features: {
      calendar: {
        title: "Синхронизация календарей",
        description:
          "Автоматическая синхронизация с популярными площадками для предотвращения двойного бронирования",
        badge: "Всегда актуально",
      },
      telegram: {
        title: "Telegram-бот",
        description:
          "Персональный бот для каталога квартир, приема заявок и онлайн-оплаты",
        badge: "Мгновенные уведомления",
      },
      automation: {
        title: "Автоматизация процессов",
        description:
          "Автоматическая отправка инструкций и уведомлений о выезде",
        badge: "Экономия времени",
      },
    },
    stats: {
      protection: {
        value: "100%",
        label: "Защита от двойного бронирования",
      },
      availability: {
        value: "24/7",
        label: "Автоматическая обработка заявок",
      },
      sync: {
        value: "Мгновенно",
        label: "Синхронизация календарей",
      },
    },
  },

  profile: {
    title: "Профиль пользователя",
    description: "Управляйте своей информацией и настройками",
    headline: "Личный кабинет",
    loadingProfile: "Загрузка профиля...",
    landlordBadge: "Арендодатель",
    userBadge: "Пользователь",
    notRegistered: {
      title: "Вы еще не зарегистрированы как арендодатель",
      description:
        "Зарегистрируйтесь, чтобы начать управлять своими объектами недвижимости и получать заявки от арендаторов",
      button: "Зарегистрироваться как арендодатель",
    },
    registered: {
      title: "Вы зарегистрированы как арендодатель",
      description:
        "Вы можете управлять своими объектами недвижимости и получать заявки от арендаторов",
    },
    fields: {
      landlordName: "Имя арендодателя",
      phoneNumber: "Номер телефона",
      contactEmail: "Email для контактов",
      landlordId: "ID арендодателя",
      userId: "ID пользователя",
    },
  },

  register: {
    title: "Регистрация арендодателя",
    description: "Заполните данные для начала работы с платформой",
    headline: "Новый пользователь",
    goToProfile: "Перейти в профиль",
  },

  form: {
    organizerName: {
      label: "Имя организатора",
      placeholder: "IT-компания или университет",
      hint: "Укажите название организации или ваше имя",
      required: "Имя организатора обязательно",
      maxLength: "Имя не должно превышать 70 символов",
    },
    phoneNumber: {
      label: "Номер телефона",
      placeholder: "+7 (999) 123-45-67",
      hint: "Российский номер в формате +7XXXXXXXXXX",
      invalid: "Введите корректный российский номер телефона (+7XXXXXXXXXX)",
    },
    submitButton: {
      register: "Зарегистрироваться",
      registering: "Регистрация...",
    },
    dataProtection: "Все данные защищены и не передаются третьим лицам",
  },

  errors: {
    UNAUTHORIZED: "Пожалуйста, войдите в систему",
    USER_NOT_FOUND: "Пользователь не найден",
    AUTH_USER_ALREADY_EXISTS: "Вы уже зарегистрированы как арендодатель",
    VALIDATION_ERROR: "Проверьте правильность заполнения формы",
    ACCESS_DENIED: "Доступ запрещен",
    INTERNAL_SERVER_ERROR: "Внутренняя ошибка сервера. Попробуйте позже",
    NETWORK_ERROR: "Ошибка сети. Проверьте интернет-соединение",
    UNKNOWN_ERROR: "Произошла неизвестная ошибка",
  },

  toast: {
    registrationSuccess: {
      title: "Регистрация успешна!",
      description: "Добро пожаловать в Посуточник",
    },
    profileUpdated: {
      title: "Профиль обновлен",
      description: "Ваши данные успешно сохранены",
    },
  },

  footer: {
    platformName: "Посуточник",
    platformDescription: "Платформа для управления краткосрочной арендой",
    version: "v1.0.0",
    copyright: "© 2025 Все права защищены",
    support: "Поддержка",
    documentation: "Документация",
  },

  theme: {
    light: "Светлая тема",
    dark: "Темная тема",
    system: "Системная",
    toggle: "Переключить тему",
  },
} as const;

/**
 * Type helper for getting nested text values
 */
export type UITextPath = string;
