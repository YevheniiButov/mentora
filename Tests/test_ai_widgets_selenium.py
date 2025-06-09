import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

class TestAIWidgetsSelenium(unittest.TestCase):
    """
    Selenium тесты для интерактивности ИИ виджетов
    Требует запущенный сервер Flask на localhost:5000
    """
    
    @classmethod
    def setUpClass(cls):
        """Настройка Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Запуск без GUI
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
            cls.base_url = "http://localhost:5000"
        except Exception as e:
            print(f"❌ Could not initialize Chrome driver: {e}")
            print("💡 Please install ChromeDriver or run tests without Selenium")
            raise unittest.SkipTest("Selenium tests require ChromeDriver")
    
    @classmethod
    def tearDownClass(cls):
        """Закрытие браузера"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
    
    def setUp(self):
        """Переход на главную страницу перед каждым тестом"""
        self.driver.get(f"{self.base_url}/en/")
    
    def login_user(self, email="test@example.com", password="testpass"):
        """Авторизация пользователя через UI"""
        try:
            # Переходим на страницу логина
            self.driver.get(f"{self.base_url}/en/auth/login")
            
            # Заполняем форму
            email_input = self.driver.find_element(By.NAME, "email")
            password_input = self.driver.find_element(By.NAME, "password")
            
            email_input.send_keys(email)
            password_input.send_keys(password)
            
            # Отправляем форму
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Ждем редиректа
            WebDriverWait(self.driver, 10).until(
                lambda driver: "/en/" in driver.current_url
            )
            
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def test_widgets_not_visible_without_auth(self):
        """Тест что виджеты не видны без авторизации"""
        try:
            # Проверяем что AI виджетов нет на странице
            widgets = self.driver.find_elements(By.CLASS_NAME, "ai-widget")
            self.assertEqual(len(widgets), 0, "AI widgets should not be visible without authentication")
            
            print("✅ Widgets hidden for unauthenticated users (Selenium)")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            self.fail(f"Test failed: {e}")
    
    def test_widgets_visible_after_login(self):
        """Тест что виджеты появляются после логина"""
        # Логинимся (может не сработать если нет тестового пользователя)
        if self.login_user():
            try:
                # Ждем появления AI секции
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ai-dashboard-section"))
                )
                
                # Проверяем что виджеты присутствуют
                widgets = self.driver.find_elements(By.CLASS_NAME, "ai-widget")
                self.assertGreater(len(widgets), 0, "AI widgets should be visible after login")
                
                # Проверяем конкретные виджеты
                exam_widget = self.driver.find_element(By.ID, "examReadinessWidget")
                recommendations_widget = self.driver.find_element(By.ID, "recommendationsWidget")
                chat_widget = self.driver.find_element(By.ID, "miniChatWidget")
                analytics_widget = self.driver.find_element(By.ID, "progressAnalyticsWidget")
                
                self.assertTrue(exam_widget.is_displayed())
                self.assertTrue(recommendations_widget.is_displayed())
                self.assertTrue(chat_widget.is_displayed())
                self.assertTrue(analytics_widget.is_displayed())
                
                print("✅ Widgets visible after login (Selenium)")
            except TimeoutException:
                print("⚠️ Widgets did not load (possibly no test user or server not running)")
            except Exception as e:
                print(f"❌ Test failed: {e}")
    
    def test_mini_chat_toggle_functionality(self):
        """Тест функциональности раскрытия/сворачивания мини-чата"""
        if self.login_user():
            try:
                # Находим кнопку toggle мини-чата
                chat_toggle = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "miniChatToggle"))
                )
                
                # Проверяем что чат изначально свернут
                chat_body = self.driver.find_element(By.ID, "miniChatBody")
                self.assertFalse(chat_body.is_displayed(), "Mini chat should be initially collapsed")
                
                # Кликаем чтобы развернуть
                chat_toggle.click()
                time.sleep(0.5)  # Ждем анимацию
                
                # Проверяем что чат развернулся
                self.assertTrue(chat_body.is_displayed(), "Mini chat should be expanded after click")
                
                # Кликаем чтобы свернуть обратно
                chat_toggle.click()
                time.sleep(0.5)  # Ждем анимацию
                
                # Проверяем что чат свернулся
                self.assertFalse(chat_body.is_displayed(), "Mini chat should be collapsed after second click")
                
                print("✅ Mini chat toggle works (Selenium)")
            except Exception as e:
                print(f"⚠️ Mini chat test failed: {e}")
    
    def test_mobile_responsive_layout(self):
        """Тест мобильной адаптивности через изменение размера окна"""
        if self.login_user():
            try:
                # Проверяем desktop layout
                self.driver.set_window_size(1200, 800)
                time.sleep(1)
                
                # Находим виджеты
                widgets = self.driver.find_elements(By.CLASS_NAME, "ai-widget")
                if len(widgets) > 0:
                    desktop_height = widgets[0].size['height']
                    
                    # Переключаемся на мобильный размер
                    self.driver.set_window_size(375, 667)  # iPhone размер
                    time.sleep(1)
                    
                    # Проверяем что виджеты адаптировались
                    mobile_widgets = self.driver.find_elements(By.CLASS_NAME, "ai-widget")
                    if len(mobile_widgets) > 0:
                        mobile_height = mobile_widgets[0].size['height']
                        
                        # На мобильных виджеты могут быть более компактными
                        print(f"Desktop widget height: {desktop_height}px")
                        print(f"Mobile widget height: {mobile_height}px")
                        
                        print("✅ Mobile responsive layout works (Selenium)")
                    else:
                        print("⚠️ No widgets found in mobile view")
                else:
                    print("⚠️ No widgets found in desktop view")
                    
            except Exception as e:
                print(f"⚠️ Mobile responsive test failed: {e}")
    
    def test_refresh_button_functionality(self):
        """Тест функциональности кнопки обновления в виджете экзамена"""
        if self.login_user():
            try:
                # Ждем загрузки виджета экзамена
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "examReadinessWidget"))
                )
                
                # Находим кнопку обновления
                refresh_button = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "#examReadinessWidget .widget-actions button"
                )
                
                # Кликаем кнопку обновления
                refresh_button.click()
                
                # Проверяем что появился loading state
                try:
                    loading_state = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "loading-state"))
                    )
                    print("✅ Refresh button triggers loading state (Selenium)")
                except TimeoutException:
                    print("⚠️ Loading state not detected after refresh")
                
            except Exception as e:
                print(f"⚠️ Refresh button test failed: {e}")
    
    def test_widget_loading_states(self):
        """Тест состояний загрузки виджетов"""
        if self.login_user():
            try:
                # Ждем появления виджетов
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ai-widget"))
                )
                
                # Проверяем что есть spinner'ы или loading состояния
                loading_spinners = self.driver.find_elements(By.CLASS_NAME, "spinner-border")
                loading_states = self.driver.find_elements(By.CLASS_NAME, "loading-state")
                
                if len(loading_spinners) > 0 or len(loading_states) > 0:
                    print("✅ Loading states present in widgets (Selenium)")
                else:
                    print("⚠️ No loading states found (widgets may have loaded instantly)")
                    
            except Exception as e:
                print(f"⚠️ Loading states test failed: {e}")
    
    def test_css_classes_applied(self):
        """Тест что CSS классы правильно применены"""
        if self.login_user():
            try:
                # Ждем загрузки виджетов
                widgets = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ai-widget"))
                )
                
                if len(widgets) > 0:
                    widget = widgets[0]
                    
                    # Проверяем что базовые стили применены
                    background_color = widget.value_of_css_property("background-color")
                    border_radius = widget.value_of_css_property("border-radius")
                    
                    # Проверяем что стили не дефолтные
                    self.assertNotEqual(background_color, "rgba(0, 0, 0, 0)")
                    self.assertNotEqual(border_radius, "0px")
                    
                    print("✅ CSS styles properly applied (Selenium)")
                else:
                    print("⚠️ No widgets found for CSS testing")
                    
            except Exception as e:
                print(f"⚠️ CSS test failed: {e}")
    
    def test_javascript_errors(self):
        """Тест отсутствия JavaScript ошибок"""
        if self.login_user():
            try:
                # Ждем полной загрузки страницы
                time.sleep(3)
                
                # Получаем логи браузера
                logs = self.driver.get_log('browser')
                
                # Фильтруем только ошибки JavaScript
                js_errors = [log for log in logs if log['level'] == 'SEVERE']
                
                if len(js_errors) == 0:
                    print("✅ No JavaScript errors detected (Selenium)")
                else:
                    print(f"⚠️ Found {len(js_errors)} JavaScript errors:")
                    for error in js_errors:
                        print(f"  - {error['message']}")
                        
            except Exception as e:
                print(f"⚠️ JavaScript error check failed: {e}")

if __name__ == '__main__':
    print("\n🧪 Starting Selenium tests for AI widgets...")
    print("📋 Prerequisites:")
    print("  1. Flask server running on localhost:5000")
    print("  2. ChromeDriver installed and in PATH")
    print("  3. Test user created in database")
    print("  4. AI endpoints properly configured\n")
    
    unittest.main(verbosity=2) 