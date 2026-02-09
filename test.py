from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ListProperty

Window.size = (800, 800)

class Ring(Widget):
    contacts = ListProperty([])
    # Словарь для хранения текста, привязанного к крестикам
    cross_texts = {}

    def __init__(self, outer_w, outer_h, text, label_offset=(0, 0), **kwargs):
        super().__init__(**kwargs)
        self.outer_w = outer_w * 3
        self.outer_h = outer_h * 3
        self.label_offset = label_offset

        with self.canvas:
            self.color = Color(1, 1, 1, 1)
            self.line = Line(width=4)

        self.label = Label(
            text=text, font_size=20, color=(1, 1, 1, 1),
            size_hint=(None, None), size=(self.outer_w, self.outer_h)
        )
        self.add_widget(self.label)

        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.bind(size=self.update_position)
        Window.bind(on_mouse_down=self.on_mouse_down)
        self.update_position()

    def update_position(self, *args):
        self.cx = Window.width / 2
        self.cy = Window.height / 2
        self.line.ellipse = (
            self.cx - self.outer_w / 2,
            self.cy - self.outer_h / 2,
            self.outer_w,
            self.outer_h
        )
        self.label.pos = (
            self.cx - self.outer_w / 2 + self.label_offset[0],
            self.cy - self.outer_h / 2 + self.label_offset[1]
        )

        for cross, dx, dy in self.contacts:
            cross.pos = (
                self.cx + dx * (self.outer_w / 2) - cross.width / 2,
                self.cy + dy * (self.outer_h / 2) - cross.height / 2
            )

    def inside_ellipse(self, x, y):
        dx = x - self.cx
        dy = y - self.cy
        return (dx ** 2) / (self.outer_w / 2) ** 2 + (dy ** 2) / (self.outer_h / 2) ** 2 <= 1

    def on_mouse_pos(self, window, pos):
        if self.inside_ellipse(*pos):
            self.color.rgba = (1, 0, 0, 1)
            self.label.color = (1, 0.3, 0.3, 1)
        else:
            self.color.rgba = (1, 1, 1, 1)
            self.label.color = (1, 1, 1, 1)

    def on_mouse_down(self, window, x, y, button, modifiers):
        # Правая кнопка — добавляем крестик
        if button == "right" and self.inside_ellipse(x, y):
            dx = (x - self.cx) / (self.outer_w / 2)
            dy = (y - self.cy) / (self.outer_h / 2)

            cross = Label(
                text="X", font_size=20, color=(1, 0, 0, 1),
                size_hint=(None, None), size=(20, 20)
            )
            self.add_widget(cross)
            self.contacts.append([cross, dx, dy])
            self.update_position()
            # Инициализируем текст для нового крестика
            self.cross_texts[cross] = ""

        # Левая кнопка — проверяем клик по крестику
        elif button == "left":
            for cross, dx, dy in self.contacts:
                # Проверяем, попал ли клик в крестик
                if (cross.x <= x <= cross.right and
                    cross.y <= y <= cross.top):
                    self.show_text_input_popup(cross)
                    return

    def show_text_input_popup(self, cross):
        # Создаём поп ап с полем ввода
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        ti = TextInput(
            text=self.cross_texts[cross],  # Подставляем сохранённый текст
            size_hint_y=None,
            height=100,
            multiline=True
        )
        box.add_widget(ti)

        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        save_btn = Button(text="Сохранить", size_hint=(None, None), size=(100, 40))
        close_btn = Button(text="Закрыть", size_hint=(None, None), size=(100, 40))
        btn_box.add_widget(save_btn)
        btn_box.add_widget(close_btn)
        box.add_widget(btn_box)

        popup = Popup(
            title="Введите текст для крестика",
            content=box,
            size_hint=(None, None),
            size=(400, 300),
            auto_dismiss=False
        )

        # Обработчик сохранения
        def save_text(instance):
            self.cross_texts[cross] = ti.text
            popup.dismiss()

        # Обработчик закрытия
        def close_popup(instance):
            popup.dismiss()

        save_btn.bind(on_release=save_text)
        close_btn.bind(on_release=close_popup)

        popup.open()

class CirclesApp(App):
    def build(self):
        root = Widget()
        saved_sessions = []  # Храним все сессии: [(вопрос, ответ), ...]

        # ---------- Кольца ----------
        rings = [
            (250, 150, "Круг Развития", (210, 120)),
            (200, 120, "Круг Продуктивности", (150, 70)),
            (150, 80, "Круг Взглядов", (150, 30)),
            (100, 50, "Близкий Круг", (100, 0)),
        ]
        for r in rings:
            root.add_widget(Ring(*r))

        # ---------- Screen1 (Досье) ----------
        screen1 = Widget()
        with screen1.canvas:
            Color(0, 0, 0, 0.95)
            screen1.rect = Rectangle(pos=(0, 0), size=Window.size)
        screen1.opacity = 0
        root.add_widget(screen1)

        answers_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        answers_layout.bind(minimum_height=answers_layout.setter('height'))
        scroll_answers = ScrollView(size_hint=(None, None), size=(700, 600), pos=(50, 120))
        scroll_answers.add_widget(answers_layout) 
        screen1.add_widget(scroll_answers)

        # ---------- Screen2 (Опросник) ----------
        screen2 = Widget()
        with screen2.canvas:
            Color(0, 0, 0, 0.95)
            screen2.rect = Rectangle(pos=(0, 0), size=Window.size)
        screen2.opacity = 0
        root.add_widget(screen2)

        content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        questions = ["Как тебя зовут?", "Чего ты хочешь достичь?", "Что сейчас мешает?",
                    "Твоя главная цель?", "Что важно?"] * 5

        inputs = []
        for q in questions:
            content.add_widget(Label(text=q, size_hint_y=None, height=25))
            ti = TextInput(size_hint_y=None, height=30, multiline=False)
            content.add_widget(ti)
            inputs.append(ti)

        scroll = ScrollView(size_hint=(None, None), size=(700, 600), pos=(50, 100))
        scroll.add_widget(content)
        screen2.add_widget(scroll)

        save_btn = Button(text="Сохранить", size_hint=(None, None), size=(120, 40), pos=(50, 40))
        screen2.add_widget(save_btn)

        # ---------- Функция: открыть поп ап с ответами ----------
        def show_session_popup(session_index):
            session = saved_sessions[session_index]
            box = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))

            # Поля ввода для редактирования
            editable_fields = []
            for q, a in session:
                box.add_widget(Label(text=q, size_hint_y=None, height=25, halign='left'))
                ti = TextInput(text=a, size_hint_y=None, height=30)
                box.add_widget(ti)
                editable_fields.append(ti)

            scroll = ScrollView()
            scroll.add_widget(box)

            btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
            save_changes_btn = Button(text="Сохранить изменения", size_hint=(None, None), size=(150, 40))
            delete_btn = Button(text="Удалить", size_hint=(None, None), size=(100, 40))
            close_btn = Button(text="Закрыть", size_hint=(None, None), size=(100, 40))

            btn_box.add_widget(save_changes_btn)
            btn_box.add_widget(delete_btn)
            btn_box.add_widget(close_btn)

            popup_content = BoxLayout(orientation='vertical')
            popup_content.add_widget(scroll)
            popup_content.add_widget(btn_box)

            popup = Popup(
                title="Редактирование сессии",
                content=popup_content,
                size_hint=(None, None),
                size=(650, 600),
                auto_dismiss=False
            )

            # Обработчик сохранения изменений
            def save_changes(instance):
                # Обновляем данные в saved_sessions
                for i, (q, _) in enumerate(session):
                    saved_sessions[session_index][i] = (q, editable_fields[i].text)
                # Пересоздаём кнопку в Screen1 с новым первым ответом
                first_answer = saved_sessions[session_index][0][1]
                btn = answers_layout.children[session_index]  # Получаем кнопку по индексу
                btn.text = first_answer
                popup.dismiss()

            # Обработчик удаления сессии
            def delete_session(instance):
                saved_sessions.pop(session_index)
                answers_layout.remove_widget(answers_layout.children[session_index])
                popup.dismiss()

            # Обработчик закрытия
            def close_popup(instance):
                popup.dismiss()

            save_changes_btn.bind(on_release=save_changes)
            delete_btn.bind(on_release=delete_session)
            close_btn.bind(on_release=close_popup)

            popup.open()

        # ---------- Функция сохранения новой сессии ----------
        def saveanswers(instance):
            # Собираем заполненные ответы
            session = []
            for q, inp in zip(questions, inputs):
                if inp.text.strip():
                    session.append((q, inp.text.strip()))

            if not session:
                return  # Не сохраняем пустые сессии

            saved_sessions.append(session)

            # Создаём кнопку для Screen1 (отображаем первый ответ)
            first_answer = session[0][1]
            btn = Button(
                text=first_answer,
                size_hint_y=None,
                height=40,
                background_normal="",
                background_color=(0.2, 0.6, 1, 0.8),
                color=(1, 1, 1, 1)
            )
            # Привязываем открытие поп апа с передачей индекса сессии
            btn.bind(on_release=lambda instance: show_session_popup(len(saved_sessions) - 1))
            answers_layout.add_widget(btn)

            # Очищаем поля ввода
            for inp in inputs:
                inp.text = ""

        save_btn.bind(on_release=saveanswers)

        # ---------- Навигация между экранами ----------
        dossier = Button(text="Досье", size_hint=(None, None), size=(100, 40), pos=(10, 10))
        plus = Button(text="+", size_hint=(None, None), size=(60, 40), pos=(10, 750))
        close = Button(text="Закрыть", size_hint=(None, None), size=(100, 40), pos=(690, 750))
        root.add_widget(dossier)
        root.add_widget(plus)
        root.add_widget(close)
        plus.opacity = close.opacity = 0

        dossier.bind(on_release=lambda x: (
            setattr(screen1, "opacity", 1),
            setattr(plus, "opacity", 1),
            setattr(close, "opacity", 1)
        ))

        plus.bind(on_release=lambda x: (
            setattr(screen2, "opacity", 1),
            setattr(plus, "opacity", 0)
        ))

        close.bind(on_release=lambda x: (
            setattr(screen1, "opacity", 0),
            setattr(screen2, "opacity", 0),
            setattr(plus, "opacity", 0),
            setattr(close, "opacity", 0)
        ))

        return root

if __name__ == "__main__":
    CirclesApp().run()
