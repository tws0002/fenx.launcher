# Studio Pipeline Starter

Use this starter to start any application on studio, farm or freelancer workstation.

## Зачем это приложение

- Создает TrayIcon для запуска приложения на студии
- Авторизация пользователей
- Объявление переменных окружения для конкретного софта в разных режимах
- Возможно добавить любое приложение для старта
- Интегрирован CGRU Afanasy
- Интегрирован генератор меню для Maya, Nuke, Houdini

## Tray Menu Applications

Используется для старта приложений в специальном окружении под пайплайн
В подменю Applications собираются все доступные приложения.
Есть опции запуска приложений.

1. Левый клик - запускает приложение

2. Левый клик+Ctrl - создает ярлык на рабочем столе

3. Левый клик+Shift - добавляет приложение в главное меню

4. Левый клик+Shift в главное меню - удаляет приложение из главного меню


## Настройка приложений

Для добавления нового приложения нужно создать модуль приложения в папке app_wrappers.

#### Обязательные условия:
- простое название (`nuke`, `maya`, `houdini`)
- переопределить атрибуты класса:
    - `app_name` (Общее название приложения. Можно использовать `__name__.rsplit('.')[-1]`)
    - `bin_name` (Имя файла основного executable)
    - `cmd_name` (Имя файла командной строки)
- Реализовать класс с именем `Application` унаследованный от `app_wrappers._base.BaseApplication`.
- переопределить метод `get_apps` который возвращает список инстансов класса Application. Список используется в меню.

#### Необязательные условия:
- если у приложения нестандартные режимы (см `config.MODS_NAMES`) нужно переопределить
метод `generate_mods` который вернет список инстансов класса `Application.Mod` (см `cgru` или `nuke`). В противном случае режимы
будут генерироваться автоматически из `config.APP_MODS` по имени приложения. Так же потребуется переопределить метод
`start` чтобы правильно запускать модифицированные режимы (см `cgru` или `nuke`). В start не забываем вызвать `define_envs`.
- сделать иконки по имени приложения и режимов и положить в папку icons. Если иконки там присутствуют и имя совпадает
с именем приложения или режима то она будет использоваться.
- переопределить метод `define_envs` если требуется объявления специальный переменных. Обязательно нужно вызвать дефолтный `define_envs`

## Настройка авторизации

1. Чтобы задействовать свой модуль авторизации нужно создать его например в папке `utils\auth` и прописать в конфиг параметр
`AUTH_PLUGIN` включая имя класса , например `utils.auth.cuctom_auth.AuthClass`.

2. наследовать класс авторизации нужно от `utils.auth._baseAuth.AuthClass`

3. необходимо переопределить следующие методы:
    - login

     процесс авторизации, возвращает bool

    - logout

     процесс удаления авторизации, возвращает bool

    - get_user_groups

     возвращает список имён групп в которых состоит юзер для ограничения доступа

    - user_info

     возвращает словарь с данными о юзере. Например:

```python
data = dict(
    id=000,
    full_name='User name',
    username='username',
    email='user@mail.com',
    groups=self.get_user_groups(000)
    )
```


## Конфигурационный файл

В корне приложения находится файл `config.json`, он является рутовым конфигом для данного приложения, но не для пайплайна в целом.
Рутовый пайплайновый конфиг находится в корне папки пайплайна и подгружается через include.
В конфиге пайплайна находятся опции обязательные для всего пайплайна:
```
PIPELINE_LOCATION - путь к корню папки пайплайна. По умолчанию $CONFIG_FILE_DIR (папка текущего скрипта)
PROJECTS_LOCATION - путь к корню проектов
SOFTWARE_LOCATIONS - список путей для поиска приложений
AUTH_MODULE - модуль для авторизации. Если не указать то авторизация отключается
MODS_NAMES - красивые имена стандартных режимов приложения для меню
GROUP_TO_MODE_REMAP - переименование групп из полученных в подходящие для стартера
APP_MODS - режимы доступные для приложения по имени приложения
```
В конфиге стартера опции нужные только для стартера, для отображения в меню
```
ICONS - пути к иконкам по имени
MODS_ICONS - иконки для режимов
HELP_URL - путь который открывается после выбора пункта меню Help
RESENTLY_APPLICATIONS - количество запененных приложений
```

## Application Starter

Для запуска приложения в специальном окружении пайплайна используется файл `start_app.cmd`.
Допустимые аргументы:

- `-app --application`  : имя приложения (maya, houdini, nuke)
- `-ver --version`      : версия приложения. Если не указать то откроется самая последняя версия
- `-mod --mode`         : режим запуска (model, vfx, amin...). Если не указать то используется `default`. Так же включается режим `default` если у текущего залогиненного юзера нет доступа указанному режиму
- `-vrb --verbose`      : отображать детали загрузки в консоли

### Стандартные переменные

Во время старта приложения по умолчанию создаются следующие переменные:

- `STUDIO_NAME` - пайплайн-имя студии
- `APP_VERSION` - пайплайн-версия текущего приложения
- `PIPELINE_MODE` - режим в котором запущено приложение
- `PIPELINE_APP_MODS` - все режимы, которые поддерживает приложение. Копируется из конфига. Например `anim,rig,render,layout`
- `PIPELINE_USER` - имя юзера от которого запущено приложение. Этот юзер должен быть залогинен. Если не залогинен то режим переключается в `default`
- `PIPELINE_LOCATION` - корневая папка пайплайна
- `APPLICATION_PATH` - корневая папка пайплайна для текущего приложения

### Другие аргументы

Все остальные аргументы отправятся в комманд приложения


#### Дополнительные аргументы

Конфигурационный файл поддерживает аргумент `-log_level` который переопределяет параметр `LOG_LEVEL` записанный в json файле конфигурации.

### Кастомизация

#### Стили

Для изменения стиля меню можно создать файл `\tray_menu\widgets\custom_menu.css` и добавить свой стиль. Он будет применён после основного.

В конфиге также можно настроить размер шрифта и иконок

`MENU_ICON_SIZE` - Размер иконок. По умолчанию `26`

`MENU_ICON_FONT_SIZE` - Размер шрифта. По умолчанию `"18px"`
