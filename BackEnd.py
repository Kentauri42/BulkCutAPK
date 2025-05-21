from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.metrics import dp
from datetime import datetime, timedelta
import hashlib

# Set window size simulating phone screen size
phone_width_dp = 360
phone_height_dp = 640
Window.size = (dp(phone_width_dp), dp(phone_height_dp))

KV = '''
#:import utils kivy.utils

<SignInScreen>:
    BoxLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1  # Putih
            Rectangle:
                pos: self.pos
                size: self.size
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(16)
        id: signin_layout

        Label:
            text: "Sign In"
            font_size: '28sp'
            color: 0, 0, 0, 1
            size_hint_y: None
            height: self.texture_size[1]

        TextInput:
            id: username_input
            hint_text: "Username"
            multiline: False
            size_hint_y: None
            height: dp(40)

        TextInput:
            id: password_input
            hint_text: "Password"
            multiline: False
            password: True
            size_hint_y: None
            height: dp(40)

        Label:
            id: message_label
            text: ''
            color: 1, 0, 0, 1
            font_size: '14sp'
            size_hint_y: None
            height: self.texture_size[1]

        Button:
            text: "Sign In"
            size_hint_y: None
            height: dp(48)
            background_color: 0.2, 0.6, 0.86, 1
            color: 1, 1, 1, 1
            on_release: root.sign_in()

        Widget:
            size_hint_y: 1

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(8)
            Label:
                text: "Don't have an account?"
                font_size: '14sp'
                color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1]
            Button:
                text: "Sign Up"
                background_color: 0.18, 0.8, 0.44, 1
                color: 1, 1, 1, 1
                size_hint_x: None
                width: dp(80)
                on_release: app.root.current = 'signup'

<SignUpScreen>:
    BoxLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(16)
        id: signup_layout

        Label:
            text: "Sign Up"
            font_size: '28sp'
            color: 0, 0, 0, 1
            size_hint_y: None
            height: self.texture_size[1]

        TextInput:
            id: username_input
            hint_text: "Choose a Username"
            multiline: False
            size_hint_y: None
            height: dp(40)

        TextInput:
            id: password_input
            hint_text: "Choose a Password"
            multiline: False
            password: True
            size_hint_y: None
            height: dp(40)

        TextInput:
            id: password_confirm_input
            hint_text: "Confirm Password"
            multiline: False
            password: True
            size_hint_y: None
            height: dp(40)

        Label:
            id: message_label
            text: ''
            color: 1, 0, 0, 1
            font_size: '14sp'
            size_hint_y: None
            height: self.texture_size[1]

        Button:
            text: "Sign Up"
            size_hint_y: None
            height: dp(48)
            background_color: 0.18, 0.8, 0.44, 1
            color: 1, 1, 1, 1
            on_release: root.sign_up()

        Widget:
            size_hint_y: 1

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(8)
            Label:
                text: "Already have an account?"
                font_size: '14sp'
                color: 0, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1]
            Button:
                text: "Sign In"
                background_color: 0.2, 0.6, 0.86, 1
                color: 1, 1, 1, 1
                size_hint_x: None
                width: dp(80)
                on_release: app.root.current = 'signin'

<UserInfoScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(16)
        padding: dp(24)
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "Your Body Info"
            font_size: '28sp'
            color: 0, 0, 0, 1
            size_hint_y: None
            height: self.texture_size[1]

        TextInput:
            id: weight_input
            hint_text: "Enter your weight (kg)"
            input_filter: 'float'
            multiline: False
            size_hint_y: None
            height: dp(48)

        TextInput:
            id: height_input
            hint_text: "Enter your height (cm)"
            input_filter: 'float'
            multiline: False
            size_hint_y: None
            height: dp(48)

        Label:
            id: info_message
            text: ""
            font_size: '14sp'
            color: 1, 0, 0, 1
            size_hint_y: None
            height: self.texture_size[1]

        Button:
            text: "Save & Continue"
            size_hint_y: None
            height: dp(48)
            background_color: 0.2, 0.6, 0.86, 1
            color: 1,1,1,1
            on_release: root.save_user_info()


        Button:
            text: "Back to Main"
            size_hint_y: None
            height: dp(48)
            background_color: 0.6, 0.6, 0.6, 1
            color: 1, 1, 1, 1
            on_release: app.root.current = 'main'

<MainScreen>:
    BoxLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(16)

        Label:
            text: "Workout App"
            font_size: '28sp'
            color: 0, 0, 0, 1
            size_hint_y: None
            height: self.texture_size[1]

        Label:
            text: "Select an exercise:"
            font_size: '18sp'
            color: 0, 0, 0, 1
            size_hint_y: None
            height: self.texture_size[1]

        GridLayout:
            cols: 3
            spacing: dp(12)
            size_hint_y: None
            height: dp(100)

            Button:
                text: "Leg"
                font_size: '16sp'
                on_release: root.start_exercise("Leg")
                size_hint_y: None
                height: dp(40)
                background_color: 0.2, 0.6, 0.86, 1
                color: 1, 1, 1, 1

            Button:
                text: "Arm"
                font_size: '16sp'
                on_release: root.start_exercise("Arm")
                size_hint_y: None
                height: dp(40)
                background_color: 0.18, 0.8, 0.44, 1
                color: 1, 1, 1, 1

            Button:
                text: "Abs"
                font_size: '16sp'
                on_release: root.start_exercise("Abs")
                size_hint_y: None
                height: dp(40)
                background_color: 0.9, 0.3, 0.3, 1
                color: 1, 1, 1, 1

        Label:
            id: streak_label
            text: root.streak_text
            font_size: '14sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: self.texture_size[1]

        Widget:
            size_hint_y: 1

        Button:
            text: "Sign Out"
            size_hint_y: None
            height: dp(44)
            background_color: 0.8, 0.2, 0.2, 1
            color: 1, 1, 1, 1
            on_release: root.sign_out()

<ExerciseScreen>:
    BoxLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(16)

        Label:
            id: exercise_label
            text: ""
            font_size: '24sp'
            color: 0, 0, 0, 1
            size_hint_y: None
            height: self.texture_size[1]

        Button:
            text: "Complete Exercise"
            size_hint_y: None
            height: dp(48)
            background_color: 0.2, 0.6, 0.86, 1
            color: 1, 1, 1, 1
            on_release: root.complete_exercise()

        Button:
            text: "Back to Home"
            size_hint_y: None
            height: dp(48)
            background_color: 0.4, 0.4, 0.4, 1
            color: 1, 1, 1, 1
            on_release: app.root.current = 'main'

'''

class UserInfoScreen(Screen):

    def save_user_info(self):
        weight = self.ids.weight_input.text.strip()
        height = self.ids.height_input.text.strip()

        if not weight or not height:
            self.ids.message_label.text = "Please enter both weight and height."
            return

        try:
            weight = float(weight)
            height = float(height)
        except ValueError:
            self.ids.message_label.text = "Weight and height must be numbers!"
            return

        # Simpan ke JSON Store
        username = self.manager.app.current_user
        store = self.manager.app.user_store

        if store.exists(username):
            user_data = store.get(username)
            user_data['weight'] = weight
            user_data['height'] = height
            store.put(username, **user_data)

        # Pindah ke halaman utama
        self.manager.current = 'main'
        self.manager.get_screen('main').update_streak()


def hash_password(password: str) -> str:
    """Hash a password string using SHA-256."""
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
        stored_hash = store.get(username).get('password_hash')
        if hash_password(password) == stored_hash:
            self.ids.message_label.text = ""
            # Save logged in user info (optional)
            self.manager.app.current_user = username
            self.manager.current = 'main'
            self.manager.get_screen('main').update_streak()
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

        # Simpan user baru + siapkan kolom berat & tinggi kosong
        store.put(username,
                  password_hash=password_hash,
                  weight=None,
                  height=None)

        # Simpan sebagai user yang sedang login
        self.manager.app.current_user = username

        # Langsung ke halaman User Info
        self.manager.current = 'userinfo'


class MainScreen(Screen):
    streak_text = "Loading streak..."

    def on_enter(self):
        self.update_streak()

    def start_exercise(self, exercise_name):
        exercise_screen = self.manager.get_screen('exercise')
        exercise_screen.exercise_name = exercise_name
        exercise_screen.ids.exercise_label.text = f"Exercise: {exercise_name}"
        self.manager.current = 'exercise'

    def update_streak(self):
        store = self.manager.app.store
        dates = store.get('workout').get('dates', []) if store.exists('workout') else []
        streak_count = self.calculate_streak(dates)
        self.streak_text = f"Current workout streak: {streak_count} day(s)"

        if hasattr(self, 'ids') and 'streak_label' in self.ids:
            self.ids.streak_label.text = self.streak_text

    def calculate_streak(self, dates):
        if not dates:
            return 0
        date_objects = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in dates], reverse=True)
        today = datetime.today().date()
        streak = 0
        current_date = today

        for d in date_objects:
            if d == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif d < current_date:
                if (current_date - d).days > 1:
                    break
                else:
                    current_date -= timedelta(days=1)
                    if d == current_date:
                        streak += 1
                        current_date -= timedelta(days=1)
                    else:
                        break
        return streak

    def sign_out(self):
        # Clear logged in user
        self.manager.app.current_user = None
        # Go to sign in screen on sign out
        self.manager.current = 'signin'

class ExerciseScreen(Screen):
    exercise_name = ""

    def complete_exercise(self):
        store = self.manager.app.store
        today_str = datetime.today().strftime("%Y-%m-%d")

        if not store.exists('workout'):
            store.put('workout', dates=[today_str])
        else:
            dates = store.get('workout').get('dates', [])
            if today_str not in dates:
                dates.append(today_str)
                store.put('workout', dates=dates)

        self.manager.current = 'main'
        self.manager.get_screen('main').update_streak()

class WorkoutApp(App):

    current_user = None

    def build(self):
        self.store = JsonStore("workout_data.json")
        self.user_store = JsonStore("users.json")
        Builder.load_string(KV)

        self.sm = ScreenManager()
        self.sm.app = self

        self.sm.add_widget(SignInScreen(name='signin'))
        self.sm.add_widget(SignUpScreen(name='signup'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(ExerciseScreen(name='exercise'))
        self.sm.add_widget(UserInfoScreen(name='userinfo'))

        # Decide initial screen based on if user accounts exist
        if len(self.user_store) == 0:
            self.sm.current = 'signup'  # No accounts, show sign up
        else:
            self.sm.current = 'signin'  # Accounts exist, show sign in

        return self.sm


if __name__ == '__main__':
    WorkoutApp().run()
