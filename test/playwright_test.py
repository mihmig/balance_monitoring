import logging
from datetime import datetime
import time
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)
user_data_dir = "firefox_profile"  # Папка для профиля

# Использование context manager 'with' гарантирует корректное закрытие всего и вся
with sync_playwright() as p:
    browser_context = p.firefox.launch_persistent_context(
        user_data_dir,
        headless=False
    )

    # Рекомендуется брать именно первый лист, как у вас,
    # так как лаунч персистентного контекста всегда открывает пустую вкладку
    page = browser_context.pages[0]
    page.goto("https://azs.tatneft.ru/cabinet")
    # Небольшая пауза, чтобы страница и куки успели полностью прогрузиться/обновиться
    # page.wait_for_timeout(2000)
    page.reload()

    # 1. Извлекаем баланс бонусной карты
    # Берём только целую часть. Мы можем нацелиться на текстовый узел внутри блока,
    # но проще забрать весь текст и обрезать его по первому встреченному разделителю (запятой).
    balance_text = page.locator(".card__balance").inner_text()
    # Очищаем от пробелов и берем всё, что до запятой
    balance_integer = balance_text.strip().split(",")[0].strip()
    logger.info(f"Баланс: {balance_integer}")

    # 2. Извлекаем статус трат:
    # Достаем фразу "Потрачено в..."
    status_title = page.locator(".status >> span").inner_text()

    # Достаем сумму
    spend_value = page.locator(".status__spend").inner_text()
    # Заменяем неразрывные пробелы (\xa0), если они будут мешать выводу, и убираем лишние пустоты
    spend_value_clean = spend_value.replace("\xa0", " ").strip()

    logger.info(f"Статус: {status_title.strip()}")
    logger.info(f"Сумма: {spend_value_clean}")

    page.screenshot(path=f"data/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')}.png")

    # Закрываем контекст внутри блока with
    browser_context.close()

    # Даем Firefox 1 секунду на то, чтобы физически дозаписать куки на диск
    time.sleep(1)