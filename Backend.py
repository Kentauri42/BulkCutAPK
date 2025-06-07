from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty
from datetime import datetime, timedelta
import hashlib
from kivy.factory import Factory
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView # For dynamic creation
from kivy.uix.gridlayout import GridLayout # For dynamic creation

# Set window size simulating phone screen size
# Keep phone_height_dp as is, the ScrollView in MainScreen will handle overflow.
phone_width_dp = 360
phone_height_dp = 740
Window.size = (dp(phone_width_dp), dp(phone_height_dp))

class MenuDietScreen(Screen):
    pass

class MyScreenManager(ScreenManager):
    pass

class UserInfoScreen(Screen):
    bmi_value = NumericProperty(0)
    bmi_category = StringProperty("")

    def save_user_info(self):
        weight_str = self.ids.weight_input.text.strip()
        height_str = self.ids.height_input.text.strip()

        if not weight_str or not height_str:
            self.ids.info_message.text = "Please enter both weight and height."
            self.ids.info_message.color = (1,0,0,1)
            return

        try:
            weight = float(weight_str)
            height = float(height_str)
            if weight <= 0 or height <=0:
                self.ids.info_message.text = "Weight and height must be positive numbers."
                self.ids.info_message.color = (1,0,0,1)
                return
        except ValueError:
            self.ids.info_message.text = "Weight and height must be valid numbers!"
            self.ids.info_message.color = (1,0,0,1)
            return

        username = self.manager.app.current_user
        store = self.manager.app.user_store

        if store.exists(username):
            user_data = store.get(username)
            user_data['weight'] = weight
            user_data['height'] = height
            store.put(username, **user_data)
        
        self.ids.info_message.text = "Info saved successfully!"
        self.ids.info_message.color = (0, 0.6, 0.2, 1)

        self.manager.current = 'main'

    def update_bmi_bar(self, *args):
        try:
            weight = float(self.ids.weight_input.text)
            height = float(self.ids.height_input.text)
            if weight > 0 and height > 0:
                bmi = weight / ((height / 100) ** 2)
                self.bmi_value = bmi
                if bmi < 18.5:
                    self.bmi_category = "Underweight"
                elif bmi < 23:
                    self.bmi_category = "Normal"
                elif bmi < 27.5:
                    self.bmi_category = "Overweight"
                else:
                    self.bmi_category = "Obese"
            else:
                self.bmi_value = 0
                self.bmi_category = ""
        except Exception:
            self.bmi_value = 0
            self.bmi_category = ""

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class SignInScreen(Screen):
    def sign_in(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text

        if not username or not password:
            self.ids.message_label.text = "Please enter both username and password."
            return

        store = self.manager.app.user_store
        if not store.exists(username):
            self.ids.message_label.text = "User not found."
            return
        
        user_data = store.get(username)
        stored_hash = user_data.get('password_hash')
        
        if hash_password(password) == stored_hash:
            self.ids.message_label.text = ""
            self.manager.app.current_user = username
            
            if user_data.get('weight') is None or user_data.get('height') is None:
                self.manager.current = 'userinfo'
            else:
                self.manager.current = 'main'
        else:
            self.ids.message_label.text = "Incorrect password."

class SignUpScreen(Screen):
    def sign_up(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text
        password_confirm = self.ids.password_confirm_input.text

        if not username or not password or not password_confirm:
            self.ids.message_label.text = "All fields are required."
            return

        if password != password_confirm:
            self.ids.message_label.text = "Passwords do not match."
            return

        store = self.manager.app.user_store
        if store.exists(username):
            self.ids.message_label.text = "Username already taken."
            return

        password_hash = hash_password(password)
        store.put(username,
                  password_hash=password_hash,
                  weight=None,
                  height=None,
                  last_login_streak_date=None,
                  workout_dates=[]) 

        self.manager.app.current_user = username
        self.manager.current = 'userinfo'

class MainScreen(Screen):
    streak_text = StringProperty("Loading streak...")
    bmi_value = NumericProperty(0)

    EATING_PLANS = {
        "underweight": {
            "pagi": [
                {"name": "Nasi Uduk Komplit", "image": "images/und1.png", "desc": "Kalori & protein tinggi."},
                {"name": "Smoothie Pisang & Selai Kacang", "image": "images/und2.png", "desc": "Padat kalori, mudah dicerna."},
            ],
            "siang": [
                {"name": "Soto Daging Santan", "image": "images/und3.png", "desc": "Kuah kental, daging, perkedel."},
                {"name": "Pasta Carbonara", "image": "images/und4.png", "desc": "Smoked beef/ayam, telur, keju."},
            ],
            "malam": [
                {"name": "Martabak Telur Spesial", "image": "images/und5.png", "desc": "Isi daging cincang, daun bawang."},
                {"name": "Susu Full Cream & Cookies", "image": "images/und6.png", "desc": "Camilan malam penambah kalori."},
            ]
        },
        "normal": {
            "pagi": [
                {"name": "Bubur Ayam Komplit", "image": "images/nor1.png", "desc": "Porsi seimbang, nutrisi lengkap."},
                {"name": "Roti Gandum & Alpukat Telur", "image": "images/nor2.png", "desc": "Serat, protein, lemak sehat."},
            ],
            "siang": [
                {"name": "Gado-Gado Lontong", "image": "images/nor3.png", "desc": "Sayuran, tahu, tempe, telur, lontong."},
                {"name": "Ikan Kembung Bakar & Nasi Merah", "image": "images/nor4.png", "desc": "Bumbu minimalis, sambal, lalapan."},
            ],
            "malam": [
                {"name": "Tumis Brokoli Ayam Fillet", "image": "images/nor5.png", "desc": "Porsi ringan, protein & serat."},
                {"name": "Buah Potong & Yoghurt Plain", "image": "images/nor6.png", "desc": "Hindari makan berat dekat tidur."},
            ]
        },
        "overweight": {
            "pagi": [
                {"name": "Oatmeal & Buah Beri", "image": "images/ovr1.png", "desc": "Plain oatmeal, buah beri, madu."},
                {"name": "Dada Ayam Rebus & Salad", "image": "images/ovr2.png", "desc": "Ayam suwir, mix green salad."},
            ],
            "siang": [
                {"name": "Sop Bening Sayur & Tahu Sutra", "image": "images/ovr3.png", "desc": "Wortel, buncis, kembang kol."},
                {"name": "Tumis Kangkung Udang & Nasi Kongbap", "image": "images/ovr4.png", "desc": "Kangkung, sedikit udang, nasi biji."},
            ],
            "malam": [
                {"name": "Sup Krim Jamur Rendah Lemak", "image": "images/ovr5.png", "desc": "Gunakan susu skim, tanpa krim."},
                {"name": "Apel Panggang Kayu Manis", "image": "images/ovr6.png", "desc": "Camilan malam rendah kalori."},
            ]
        },
        "obese": {
            "pagi": [
                {"name": "Yoghurt Plain & Chia Seed Pepaya", "image": "images/obs1.png", "desc": "Rendah kalori, tinggi serat."},
                {"name": "Smoothie Hijau (Sayur & Buah)", "image": "images/obs2.png", "desc": "Bayam, timun, nanas/apel hijau."},
            ],
            "siang": [
                {"name": "Pepes Tahu Jamur (Tanpa Nasi)", "image": "images/obs3.png", "desc": "Protein nabati, kukus."},
                {"name": "Salad Sayur & Kacang Merah Rebus", "image": "images/obs4.png", "desc": "Dressing cuka apel."},
            ],
            "malam": [
                {"name": "Sayur Bening Bayam & Oyong", "image": "images/obs5.png", "desc": "Sangat rendah kalori, hindari nasi."},
                {"name": "Agar-agar Plain dengan Buah", "image": "images/obs6.png", "desc": "Tanpa gula, isi buah segar."},
            ]
        },
        "unknown": {
            "pagi": [{"name": "Lengkapi Data TB/BB", "image": "atlas://data/images/defaulttheme/dialog_warning", "desc": "Untuk rekomendasi menu."}],
            "siang": [{"name": "Cek Kembali Data Anda", "image": "atlas://data/images/defaulttheme/dialog_information", "desc": "Pastikan terisi benar."}],
            "malam": [{"name": "Data Tidak Lengkap", "image": "atlas://data/images/defaulttheme/dialog_error", "desc": "Tidak bisa memberi saran."}]
        }
    }

    def on_enter(self):
        self.update_greeting_and_body_info()
        self.update_streak()
        self.update_food_gallery()

    def calculate_bmi(self, weight_kg, height_cm):
        if not isinstance(weight_kg, (int, float)) or not isinstance(height_cm, (int, float)): return None
        if weight_kg <= 0 or height_cm <= 0: return None
        height_m = height_cm / 100.0
        try: return weight_kg / (height_m * height_m)
        except ZeroDivisionError: return None

    def get_bmi_category(self, bmi_value):
        if bmi_value is None: return "unknown"
        if bmi_value < 18.5: return "underweight"
        elif 18.5 <= bmi_value <= 22.9: return "normal"
        elif 23.0 <= bmi_value <= 27.4: return "overweight"
        elif bmi_value >= 27.5: return "obese"
        return "unknown"

    def update_food_gallery(self):
        app = App.get_running_app()
        username = app.current_user
        food_sections_container = self.ids.food_sections_container # This is the vertical GridLayout
        food_sections_container.clear_widgets()

        if not username:
            self.ids.bmi_info_label.text = "Login untuk melihat rekomendasi."
            # Optionally add a placeholder to food_sections_container
            no_login_label = Label(text="Silakan login untuk melihat rencana makan.", size_hint_y=None, height=dp(50))
            food_sections_container.add_widget(no_login_label)
            return

        user_data = app.user_store.get(username)
        weight = user_data.get('weight')
        height = user_data.get('height')

        bmi_value = self.calculate_bmi(weight, height)
        bmi_category_key = self.get_bmi_category(bmi_value)
        bmi_category_display = bmi_category_key.replace("_", " ").capitalize()

        if bmi_value is not None:
            self.ids.bmi_info_label.text = f"BMI Anda: {bmi_value:.1f} ({bmi_category_display})"
        else:
            self.ids.bmi_info_label.text = "BMI: Data TB/BB tidak lengkap."

        plan_for_category = self.EATING_PLANS.get(bmi_category_key, self.EATING_PLANS["unknown"])
        meal_times = ["pagi", "siang", "malam"] 

        for meal_time_key in meal_times:
            section_label = Label(
                text=meal_time_key.capitalize(),
                font_size='16sp', bold=True, color=(0.1, 0.1, 0.2, 1),
                size_hint_y=None, height=dp(35), halign='left', padding_x=dp(5)
            )
            food_sections_container.add_widget(section_label)

            horizontal_scroll = ScrollView(
                size_hint_y=None, height=dp(130), # dp(120) for card + dp(10) for padding/bar
                do_scroll_x=True, do_scroll_y=False, bar_width=dp(4),
                effect_cls='ScrollEffect' # Default effect
            )
            
            meal_card_row_layout = GridLayout(
                rows=1, size_hint_x=None, spacing=dp(8), padding=[dp(5), 0, dp(5), 0] #LR padding
            )
            meal_card_row_layout.bind(minimum_width=meal_card_row_layout.setter('width'))


            meals_in_section = plan_for_category.get(meal_time_key, [])
            if not meals_in_section:
                placeholder_card = Factory.MealCard() # Use MealCard for consistent look
                placeholder_card.ids.meal_name.text = f"Belum ada menu {meal_time_key}"
                placeholder_card.ids.meal_desc.text = "Cek kembali nanti."
                placeholder_card.ids.meal_image.source = 'atlas://data/images/defaulttheme/clock'
                meal_card_row_layout.add_widget(placeholder_card)
            else:
                for meal_data in meals_in_section:
                    meal_card = Factory.MealCard()
                    meal_card.ids.meal_name.text = meal_data.get("name", "N/A")
                    meal_card.ids.meal_desc.text = meal_data.get("desc", "")
                    meal_card.ids.meal_image.source = meal_data.get("image", 'atlas://data/images/defaulttheme/image-missing')
                    meal_card_row_layout.add_widget(meal_card)
            
            horizontal_scroll.add_widget(meal_card_row_layout)
            food_sections_container.add_widget(horizontal_scroll)


    def update_greeting_and_body_info(self):
        app = App.get_running_app()
        if app.current_user:
            self.ids.greeting_label.text = f"Hai, {app.current_user}!"
            user_data = app.user_store.get(app.current_user)
            weight = user_data.get('weight')
            height = user_data.get('height')
            if weight is not None: self.ids.bb_display.text = f"{weight:.1f}"
            else: self.ids.bb_display.text = "N/A"
            if height is not None: self.ids.tb_display.text = f"{height:.1f}"
            else: self.ids.tb_display.text = "N/A"
            # Update BMI value for the bar
            bmi = self.calculate_bmi(weight, height)
            self.bmi_value = bmi if bmi else 0
        else:
            self.ids.greeting_label.text = "Hai, Guest!"
            self.ids.bb_display.text = "N/A"; self.ids.tb_display.text = "N/A"
            self.bmi_value = 0

    def start_exercise(self, exercise_name):
        exercise_screen = self.manager.get_screen('exercise')
        exercise_screen.exercise_name = exercise_name
        exercise_screen.ids.exercise_label.text = f"Mulai: {exercise_name}"
        self.manager.current = 'exercise'

    def update_streak(self):
        store = self.manager.app.store
        data = store.get('workout') if store.exists('workout') else {}
        dates = data.get('dates', [])
        streak_count = self.calculate_streak(dates)
        self.streak_text = f"Current workout streak: {streak_count} day(s)"

    def calculate_streak(self, dates_str):
        if not dates_str: return 0
        unique_dates_str = sorted(list(set(dates_str)), reverse=True)
        try: date_objects = [datetime.strptime(d_str, "%Y-%m-%d").date() for d_str in unique_dates_str]
        except ValueError: return 0
        if not date_objects: return 0
        today = datetime.today().date()
        current_streak = 0; expected_date = today
        for workout_date in date_objects:
            if workout_date == expected_date:
                current_streak += 1
                expected_date -= timedelta(days=1)
            elif workout_date < expected_date:
                if current_streak == 0 and workout_date != today - timedelta(days=1): return 0
                break
        if current_streak == 0 and (not date_objects or date_objects[0] != today) : return 0
        return current_streak

    def sign_out(self):
        self.manager.app.current_user = None
        self.manager.current = 'signin'

class ExerciseScreen(Screen):
    exercise_name = StringProperty("")
    def complete_exercise(self):
        store = self.manager.app.store; today_str = datetime.today().strftime("%Y-%m-%d")
        workout_data = store.get('workout') if store.exists('workout') else {'dates': []}
        if today_str not in workout_data['dates']:
            workout_data['dates'].append(today_str)
            store.put('workout', **workout_data)
        self.manager.current = 'main'

class WorkoutApp(App):
    current_user = None
    def build(self):
        self.store = JsonStore("workout_data.json")
        self.user_store = JsonStore("users.json")    
        Builder.load_file("Frontend.kv")
        self.sm = ScreenManager()
        self.sm.app = self
        self.sm.add_widget(SignInScreen(name='signin'))
        self.sm.add_widget(SignUpScreen(name='signup'))
        self.sm.add_widget(UserInfoScreen(name='userinfo'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(ExerciseScreen(name='exercise'))
        self.sm.current = 'signup' if not self.user_store.keys() else 'signin'
        return self.sm

if __name__ == '__main__':
    WorkoutApp().run()
