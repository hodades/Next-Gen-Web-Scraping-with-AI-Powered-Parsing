from playwright.sync_api import Playwright, sync_playwright
import random
import time
import os

def random_delay():
    delay = random.uniform(1, 3)
    time.sleep(delay)

def run(playwright: Playwright) -> None:
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    temp_profile_dir = r"C:\Users\AmirB\AppData\Local\Temp\Chrome_Playwright_Profile"

    try:
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=temp_profile_dir,
            executable_path=chrome_path,
            headless=False,
            args=[
                "--no-first-run",
                "--disable-extensions",
                "--disable-plugins-discovery",
                "--disable-web-security"
            ]
        )
        print("✅ Chrome lancé avec profil temporaire")
    except Exception as e:
        print(f"❌ Erreur de lancement : {e}")
        return

    page = browser.pages[0] if browser.pages else browser.new_page()

    try:
        # Aller sur le site
        page.goto("https://everywatch.com", wait_until="networkidle")
        random_delay()

        # Clic sur bouton login
        page.get_by_text("Log in", exact=True).click()
        random_delay()

        # Email
        page.get_by_placeholder("Email").fill("")
        random_delay()

        # Mot de passe
        page.get_by_placeholder("Password").fill("")
        random_delay()

        # Clic sur "Log in"
        page.get_by_role("button", name="Log in", exact=True).click()
        print("🔐 Connexion en cours...")
        time.sleep(5)

        print("✅ Connexion réussie. Navigateur maintenu ouvert.")
        page.pause()  # Tu peux continuer manuellement ou récupérer les cookies

    except Exception as e:
        print(f"❌ Erreur durant le login : {e}")
    finally:
        print("ℹ️ Le navigateur reste ouvert. Fermez-le manuellement quand fini.")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
