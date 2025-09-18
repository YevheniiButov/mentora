# Настройка DMARC записи для улучшения доставляемости email

## Что такое DMARC?

DMARC (Domain-based Message Authentication, Reporting and Conformance) - это стандарт аутентификации email, который помогает защитить ваш домен от фишинга и улучшает доставляемость писем.

## Зачем нужен DMARC?

1. **Защита от фишинга** - предотвращает использование вашего домена для отправки поддельных писем
2. **Улучшение доставляемости** - почтовые провайдеры (Gmail, Outlook) больше доверяют доменам с DMARC
3. **Отчеты о доставляемости** - получаете информацию о том, как обрабатываются ваши письма

## Пошаговая настройка DMARC для bigmentor.nl

### Шаг 1: Настройка SPF записи

Сначала убедитесь, что у вас есть SPF запись:

```
Тип: TXT
Имя: bigmentor.nl
Значение: v=spf1 include:_spf.resend.com ~all
```

### Шаг 2: Настройка DKIM

DKIM уже настроен автоматически через Resend. Проверьте в панели Resend:
1. Перейдите в раздел "Domains"
2. Выберите ваш домен bigmentor.nl
3. Убедитесь, что DKIM статус показывает "Verified"

### Шаг 3: Создание DMARC записи

Добавьте следующую TXT запись в DNS вашего домена:

```
Тип: TXT
Имя: _dmarc.bigmentor.nl
Значение: v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@bigmentor.nl; ruf=mailto:dmarc-failures@bigmentor.nl; fo=1; adkim=r; aspf=r;
```

### Объяснение параметров DMARC:

- `v=DMARC1` - версия протокола
- `p=quarantine` - политика для писем, не прошедших проверку (помещать в спам)
- `rua=mailto:dmarc-reports@bigmentor.nl` - email для получения агрегированных отчетов
- `ruf=mailto:dmarc-failures@bigmentor.nl` - email для получения отчетов о неудачных проверках
- `fo=1` - формат отчетов
- `adkim=r` - строгость проверки DKIM (relaxed)
- `aspf=r` - строгость проверки SPF (relaxed)

### Шаг 4: Создание email адресов для отчетов

Создайте следующие email адреса:
- `dmarc-reports@bigmentor.nl` - для получения агрегированных отчетов
- `dmarc-failures@bigmentor.nl` - для получения отчетов о неудачах

### Шаг 5: Постепенное ужесточение политики

**Фаза 1 (1-2 недели):** `p=quarantine`
```
v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@bigmentor.nl; ruf=mailto:dmarc-failures@bigmentor.nl; fo=1; adkim=r; aspf=r;
```

**Фаза 2 (после анализа отчетов):** `p=reject`
```
v=DMARC1; p=reject; rua=mailto:dmarc-reports@bigmentor.nl; ruf=mailto:dmarc-failures@bigmentor.nl; fo=1; adkim=r; aspf=r;
```

## Проверка настройки

### Онлайн инструменты для проверки:

1. **MXToolbox DMARC Checker:**
   - https://mxtoolbox.com/dmarc.aspx
   - Введите: bigmentor.nl

2. **DMARC Analyzer:**
   - https://www.dmarcanalyzer.com/
   - Введите: bigmentor.nl

3. **Google Admin Toolbox:**
   - https://toolbox.googleapps.com/apps/checkmx/
   - Введите: bigmentor.nl

### Ожидаемый результат:

После правильной настройки вы должны увидеть:
- ✅ SPF: Pass
- ✅ DKIM: Pass  
- ✅ DMARC: Pass

## Мониторинг и отчеты

### Агрегированные отчеты (RUA)

Еженедельно вы будете получать XML отчеты на `dmarc-reports@bigmentor.nl` с информацией о:
- Количестве отправленных писем
- Проценте успешных проверок
- Источниках отправки

### Отчеты о неудачах (RUF)

В реальном времени получаете уведомления о письмах, которые не прошли проверку DMARC.

## Рекомендации по улучшению доставляемости

### 1. Использование поддомена

Рассмотрите возможность использования поддомена для email:
- `mail.bigmentor.nl` или `noreply.bigmentor.nl`
- Это защитит основной домен от проблем с репутацией

### 2. Настройка в Resend

В панели Resend:
1. Перейдите в "Domains"
2. Выберите ваш домен
3. Включите "Enforce DMARC"
4. Отключите "Click Tracking" (уже сделано в коде)
5. Отключите "Open Tracking" (уже сделано в коде)

### 3. Регулярный мониторинг

- Еженедельно проверяйте DMARC отчеты
- Следите за репутацией домена в Google Postmaster Tools
- Мониторьте жалобы на спам

## Troubleshooting

### Проблема: DMARC не работает

**Решение:**
1. Проверьте правильность DNS записи
2. Убедитесь, что SPF и DKIM настроены
3. Подождите 24-48 часов для распространения DNS

### Проблема: Письма попадают в спам

**Решение:**
1. Временно измените политику на `p=none`
2. Проанализируйте отчеты
3. Исправьте проблемы с SPF/DKIM
4. Постепенно ужесточайте политику

### Проблема: Не получаете отчеты

**Решение:**
1. Проверьте, что email адреса для отчетов существуют
2. Проверьте папку "Спам"
3. Убедитесь, что DNS запись корректна

## Дополнительные ресурсы

- [DMARC.org - официальная документация](https://dmarc.org/)
- [Google Postmaster Tools](https://postmaster.google.com/)
- [Microsoft SNDS](https://sendersupport.olc.protection.outlook.com/snds/)
- [Resend DMARC Documentation](https://resend.com/docs/deliverability/dmarc)

---

**Важно:** После настройки DMARC подождите 24-48 часов и проверьте статус в Resend Dashboard. Все рекомендации должны перейти в категорию "DOING GREAT".
