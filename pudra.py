# Вход в ЛК Beeline и получение информации об остатках минут и СМС.
import os
import re
import logging
import html
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError
from retrying import retry

from plugins.max_sender import MaxSender

logger = logging.getLogger(__name__)
TIMEOUT_MS = 10000


@retry(stop_max_attempt_number=3, wait_fixed=10000)
def login(p_page: Page, p_login: str, p_password: str):
    p_page.goto("https://my.beeline.ru/login.xhtml", timeout=TIMEOUT_MS)

    # Проверяем, залогинены ли мы уже.
    try:
        user_name_locator = page.locator("//div[contains(@class,'user-name')]")
        # Ожидаем элемент со статусом "attached" (есть в DOM) или "visible"
        user_name_locator.wait_for(state="visible", timeout=3000)
        logger.info("Уже авторизованы! Пропускаем ввод логина и пароля.")
        return  # Выходим из функции, так как мы уже внутри ЛК
    except PlaywrightTimeoutError:
        logger.info("Сессия не найдена, требуется авторизация...")

    # Заполнение полей логина и пароля
    p_page.locator("#loginFormB2B\\:loginForm\\:login").fill(p_login)
    p_page.locator("#loginFormB2B\\:loginForm\\:passwordPwd").fill(p_password)

    # Клик по кнопке войти (выбираем видимую кнопку внутри формы)
    button = p_page.locator("//button[contains(@id,'loginFormB2B') and not(contains(@style, 'none'))]/span")
    try:
        button.click(timeout=5000)
    except PlaywrightTimeoutError:
        pass

    # Ожидание успешной авторизации (появление имени пользователя)
    # Playwright будет сам пытаться найти этот элемент в течение указанного таймаута
    p_page.locator("//div[contains(@class,'user-name')]").wait_for(state="visible", timeout=25000)


def get_accums(p_page: Page) -> dict:
    accums = {}

    # Находим все блоки с бонусами
    items = p_page.locator('//div[contains(@class ,"bonuses-accums-list")]/div[contains(@class, "accum-restyle")]')
    count = items.count()

    for i in range(count):
        item_text = items.nth(i).inner_text()
        parts = item_text.split('\n')

        if not parts:
            continue

        if "Мобильная связь" in parts[0] and len(parts) > 1:
            matches = re.findall(r"(\d+)\s*мин", parts[1])
            if matches:
                accums['minutes'] = matches[0]

        if "SMS" in parts[0] and len(parts) > 1:
            matches = re.findall(r"(\d+)\s*шт", parts[1])
            if matches:
                accums['sms'] = matches[0]

    return accums


def add_emojii(accum: int) -> str:
    if accum < 1:
        return f'🔴 <b>{accum}</b>'
    elif accum < 100:
        return f'🟡 <b>{accum}</b>'
    else:
        return f'🟢 <b>{accum}</b>'


def get_number_info(p_page: Page, p_number: str, p_url: str) -> str:
    attempts = 0
    accums = {}

    while len(accums) == 0 and attempts < 5:
        try:
            p_page.goto(p_url, timeout=TIMEOUT_MS)
            # Небольшое ожидание для рендеринга JS-виджетов на странице номера
            p_page.wait_for_timeout(2000)
            accums = get_accums(p_page)
        except PlaywrightTimeoutError:
            pass
        attempts += 1

    if 'minutes' not in accums or 'sms' not in accums:
        raise ValueError(f'Не удалось извлечь полную информацию об остатках для номера {p_number}')

    minutes = add_emojii(int(accums['minutes']))
    sms = add_emojii(int(accums['sms']))
    res = f"☎ <b>{p_number}:</b>\nОсталось {minutes} мин.\nОсталось {sms} SMS"
    return res


max_sender = MaxSender(os.environ['PUDRA_MAX_BOT_TOKEN'])
chat_id = int(os.environ['PUDRA_MAX_CHAT_ID'])

# Главный процесс автоматизации
with sync_playwright() as p:
    # Запуск Firefox (можно заменить на p.chromium, если Билайн под ним работает стабильнее)
    context = p.firefox.launch_persistent_context(
        os.environ['PUDRA_DATA_DIR'],
        headless=os.environ['PUDRA_HEADLESS'] == "True",
        timeout=TIMEOUT_MS
    )

    page = context.pages[0]
    try:
        login(page, os.environ['PUDRA_USERNAME'], os.environ['PUDRA_PASSWORD'])

        numbers = {
            "+7 964-296-7425": "https://my.beeline.ru/b/info/subscriberDetail.xhtml?objId=3445773686",
            "+7 963-200-4377": "https://my.beeline.ru/b/info/subscriberDetail.xhtml?objId=3323431140"
        }

        result_list = []
        for number, url in numbers.items():
            result_list.append(get_number_info(page, number, url))

        message = "\n\n".join(result_list)

    except Exception as e:
        # В случае ошибки шлем уведомление и делаем скриншот через встроенный метод Playwright
        max_sender.send_message(chat_id, str(html.escape(str(e))))
        screenshot_path = f"data/error_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.png"
        page.screenshot(path=screenshot_path, full_page=True)
        logger.error(f"Скриншот ошибки сохранен в {screenshot_path}")
        quit(-2)

    try:
        max_sender.send_message(chat_id, message)
    except Exception as e:
        logger.error(f'Error while sending to telegram: {str(e)}')
