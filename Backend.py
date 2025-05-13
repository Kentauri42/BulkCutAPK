from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from datetime import datetime, timedelta

KV = '''
<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)

        Label:
            text: "Workout App"
            font_size: '32sp'
            size_hint_y: None
            height: self.texture_size[1]

        Label:
            text: "Select an exercise:"
            font_size: '20sp'
            size_hint_y: None
            height: self.texture_size[1]

        GridLayout:
            cols: 3
            spacing: dp(20)
            size_hint_y: None
            height: dp(150)

            Button:
                text: "Leg"
                font_size: '18sp'
                on_release: root.start_exercise("Leg")

            Button:
                text: "Arm"
                font_size: '18sp'
                on_release: root.start_exercise("Arm")

            Button:
                text: "Abs"
                font_size: '18sp'
                on_release: root.start_exercise("Abs")

        Label:
            id: streak_label
            text: root.streak_text
            font_size: '16sp'
            size_hint_y: None
            height: self.texture_size[1]


<ExerciseScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)

        Label:
            id: exercise_label
            text: ""
            font_size: '28sp'

        Button:
            text: "Complete Exercise"
            size_hint_y: None
            height: dp(50)
            on_release: root.complete_exercise()

        Button:
            text: "Back to Home"
            size_hint_y: None
            height: dp(50)
            on_release: app.root.current = 'main'
'''

class MainScreen(Screen):
    streak_text = "Loading streak..."

    def on_enter(self):
        # Update streak text when entering the main screen
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

        # Also update the UI label if exists
        if hasattr(self, 'ids') and 'streak_label' in self.ids:
            self.ids.streak_label.text = self.streak_text

    def calculate_streak(self, dates):
        if not dates:
            return 0
        # Convert stored string dates back to date objects for processing
        date_objects = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in dates], reverse=True)
        today = datetime.today().date()

        streak = 0
        current_date = today

        for d in date_objects:
            if d == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif d < current_date:
                # If a date is before the expected current_date, streak breaks
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

        # After marking exercise complete, go back to main screen and update streak
        self.manager.current = 'main'
        self.manager.get_screen('main').update_streak()


class WorkoutApp(App):
    def build(self):
        self.store = JsonStore("workout_data.json")
        self.sm = ScreenManager()
        self.sm.app = self
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(ExerciseScreen(name='exercise'))

        return Builder.load_string(KV)


if __name__ == '__main__':
    WorkoutApp().run()
