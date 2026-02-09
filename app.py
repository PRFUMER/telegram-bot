from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ListProperty
from kivy.uix.widget import Widget
import time
import json
import os

Window.size = (800, 800)

# ----------------------- Класс кольца -----------------------
class Ring(Widget):
    contacts = ListProperty([])
    cross_texts = {}
    last_click_time = {}
    double_click_interval = 0.4  # секунды для двойного клика

    def __init__(self, outer_w, outer_h, text, label_offset=(0,0), **kwargs):
        super().__init__(**kwargs)
        self.outer_w = outer_w * 3
        self.outer_h = outer_h * 3
        self.label_offset = label_offset

        with self.canvas:
            self.color = Color(1,1,1,1)
            self.line = Line(width=4)
        self.label = Label(text=text, font_size=20, color=(1,1,1,1),
                           size_hint=(None,None), size=(self.outer_w,self.outer_h))
        self.add_widget(self.label)

        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.bind(size=self.update_position)
        Window.bind(on_mouse_down=self.on_mouse_down)
        self.update_position()

    def update_position(self, *args):
        self.cx = Window.width / 2
        self.cy = Window.height / 2
        self.line.ellipse = (self.cx - self.outer_w/2, self.cy - self.outer_h/2, self.outer_w, self.outer_h)
        self.label.pos = (self.cx - self.outer_w/2 + self.label_offset[0],
                          self.cy - self.outer_h/2 + self.label_offset[1])
        for cross, dx, dy in self.contacts:
            cross.pos = (self.cx + dx*(self.outer_w/2) - cross.width/2,
                         self.cy + dy*(self.outer_h/2) - cross.height/2)

    def inside_ellipse(self, x, y):
        dx = x - self.cx
        dy = y - self.cy
        return (dx**2)/(self.outer_w/2)**2 + (dy**2)/(self.outer_h/2)**2 <= 1

    def on_mouse_down(self, window, x, y, button, modifiers):
        if button == "right":
            for cross, dx, dy in self.contacts:
                if cross.x <= x <= cross.right and cross.y <= y <= cross.top:
                    self.show_text_input_popup(cross)
                    return
            if self.inside_ellipse(x,y):
                dx = (x - self.cx)/(self.outer_w/2)
                dy = (y - self.cy)/(self.outer_h/2)
                cross = Label(text="X", font_size=20, color=(1,0,0,1),
                              size_hint=(None,None), size=(20,20))
                self.add_widget(cross)
                self.contacts.append([cross, dx, dy])
                self.cross_texts[cross] = ""
                self.update_position()
        elif button == "left":
            for cross, dx, dy in self.contacts:
                if cross.x <= x <= cross.right and cross.y <= y <= cross.top:
                    now = time.time()
                    last = self.last_click_time.get(cross, 0)
                    if now - last < self.double_click_interval:
                        self.remove_widget(cross)
                        self.contacts = [c for c in self.contacts if c[0] != cross]
                        if cross in self.cross_texts:
                            del self.cross_texts[cross]
                        if hasattr(self, 'tooltip'):
                            self.remove_widget(self.tooltip)
                            del self.tooltip
                        self.update_position()
                    else:
                        self.show_text_input_popup(cross)
                    self.last_click_time[cross] = now
                    return

    def show_text_input_popup(self, cross):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        ti = TextInput(text=self.cross_texts[cross], size_hint_y=None, height=100, multiline=True)
        box.add_widget(ti)

        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        save_btn = Button(text="Сохранить", size_hint=(None,None), size=(100,40))
        close_btn = Button(text="Закрыть", size_hint=(None,None), size=(100,40))
        btn_box.add_widget(save_btn)
        btn_box.add_widget(close_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Введите текст для крестика", content=box, size_hint=(None,None),
                      size=(400,300), auto_dismiss=False)

        def save_text(instance):
            self.cross_texts[cross] = ti.text
            popup.dismiss()
        def close_popup(instance):
            popup.dismiss()
        save_btn.bind(on_release=save_text)
        close_btn.bind(on_release=close_popup)
        popup.open()

    def on_mouse_pos(self, window, pos):
        if self.inside_ellipse(*pos):
            self.color.rgba = (1,0,0,1)
            self.label.color = (1,0.3,0.3,1)
        else:
            self.color.rgba = (1,1,1,1)
            self.label.color = (1,1,1,1)

        hovered = False
        for cross, dx, dy in self.contacts:
            if cross.x <= pos[0] <= cross.right and cross.y <= pos[1] <= cross.top:
                hovered = True
                if not hasattr(self, 'tooltip'):
                    self.tooltip = Label(
                        text=self.cross_texts[cross],
                        size_hint=(None,None),
                        size=(120,30),
                        color=(1,0,0,1),
                        pos=(cross.center_x - 60, cross.top + 5)
                    )
                    self.add_widget(self.tooltip)
                else:
                    self.tooltip.text = self.cross_texts[cross]
                    self.tooltip.pos = (cross.center_x - 60, cross.top + 5)
                break
        if not hovered and hasattr(self, 'tooltip'):
            self.remove_widget(self.tooltip)
            del self.tooltip

    def save_state(self):
        """Возвращает словарь с данными кольца для сохранения"""
        return {
            'outer_w': self.outer_w / 3,  # сохраняем исходные размеры
            'outer_h': self.outer_h / 3,
            'text': self.label.text,
            'label_offset': self.label_offset,
            'contacts': [
                {
                    'dx': dx,
                    'dy': dy,
                    'text': self.cross_texts[cross]
                }
                for cross, dx, dy in self.contacts
            ]
        }

    @classmethod
    def load_from_state(cls, state, **kwargs):
        """Создаёт кольцо из сохранённого состояния"""
        ring = cls(
            state['outer_w'],
            state['outer_h'],
            state['text'],
            state['label_offset'],
            **kwargs
        )
        # Восстанавливаем крестики
        for item in state['contacts']:
            cross = Label(text="X", font_size=20, color=(1,0,0,1),
                         size_hint=(None,None), size=(20,20))
            ring.add_widget(cross)
            ring.contacts.append([cross, item['dx'], item['dy']])
            ring.cross_texts[cross] = item['text']
        ring.update_position()
        return ring

# ----------------------- Основное приложение -----------------------
class CirclesApp(App):
    icon = "/home/anwar/Downloads/Python-3.9.25/Python/Python Basics/Icon.png"

    def build(self):
        root = FloatLayout()
        # … (остальной код остаётся без изменений)
        # ----------------------- Загрузка сессий из файла -----------------------
        try:
            with open("sessions.json", "r", encoding="utf-8") as f:
                self.saved_sessions = json.load(f)
        except FileNotFoundError:
            self.saved_sessions = []

        # ----------------------- Загрузка колец из файла -----------------------
        try:
            with open("rings.json", "r", encoding="utf-8") as f:
                rings_data = json.load(f)
            # Создаём кольца из сохранённых данных
            for ring_state in rings_data:
                ring = Ring.load_from_state(ring_state)
                root.add_widget(ring)
        except FileNotFoundError:
            # Если файла нет — создаём стандартные кольца
            rings = [
                (250,150,"Круг Развития",(210,120)),
                (200,120,"Круг Продуктивности",(150,70)),
                (150,80,"Круг Взглядов",(150,30)),
                (100,50,"Близкий Круг",(100,0)),
            ]
            for r in rings:
                root.add_widget(Ring(*r))

        # ----------------------- Screen1 -----------------------
        screen1 = FloatLayout()
        screen1_bg = Widget()
        with screen1_bg.canvas:
            Color(0,0,0,0.95)
            Rectangle(pos=(0,0), size=Window.size)
        screen1.add_widget(screen1_bg)
        screen1.opacity = 0
        root.add_widget(screen1)

        self.answers_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.answers_layout.bind(minimum_height=self.answers_layout.setter('height'))
        scroll_answers = ScrollView(size_hint=(None,None), size=(700,600), pos=(50,120))
        scroll_answers.add_widget(self.answers_layout)
        screen1.add_widget(scroll_answers)

        open_all_btn = Button(text="Открыть все ответы", size_hint=(None,None), size=(180,40), pos=(220,10))
        screen1.add_widget(open_all_btn)

        # Заполняем answers_layout из сохранённых сессий
        for session in self.saved_sessions:
            btn = Button(text=session[0][1], size_hint_y=None, height=40,
                         background_color=(0.2,0.6,1,0.8), color=(1,1,1,1))
            self.answers_layout.add_widget(btn)
            btn.bind(on_release=lambda inst, s=session, b=btn: self.show_session_popup(s,b))

        # ----------------------- Screen2 -----------------------
        screen2 = FloatLayout()
        screen2_bg = Widget()
        with screen2_bg.canvas:
            Color(0,0,0,0.95)
            Rectangle(pos=(0,0), size=Window.size)
        screen2.add_widget(screen2_bg)
        screen2.opacity = 0
        root.add_widget(screen2)

        self.questions = ["Как тебя зовут?", "Чего ты хочешь достичь?", "Что сейчас мешает?",
                         "Твоя главная цель?", "Что важно?"] * 2
        self.inputs = []

        content = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        for q in self.questions:
            content.add_widget(Label(text=q, size_hint_y=None, height=25))
            ti = TextInput(size_hint_y=None, height=30)
            content.add_widget(ti)
            self.inputs.append(ti)

        scroll = ScrollView(size_hint=(None,None), size=(700,600), pos=(50,100))
        scroll.add_widget(content)
        screen2.add_widget(scroll)

        save_btn = Button(text="Сохранить", size_hint=(None,None), size=(120,40), pos=(50,40))
        screen2.add_widget(save_btn)

        # ----------------------- Popup редактирования сессии -----------------------
        def show_session_popup(session, btn):
            box = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))
            editable_fields = []

            for q,a in session:
                box.add_widget(Label(text=q, size_hint_y=None, height=25))
                ti = TextInput(text=a, size_hint_y=None, height=30)
                box.add_widget(ti)
                editable_fields.append(ti)

            scroll_popup = ScrollView()
            scroll_popup.add_widget(box)

            btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
            save_changes_btn = Button(text="Сохранить изменения", size_hint=(None,None), size=(150,40))
            delete_btn = Button(text="Удалить", size_hint=(None,None), size=(100,40))
            close_btn = Button(text="Закрыть", size_hint=(None,None), size=(100,40))
            btn_box.add_widget(save_changes_btn)
            btn_box.add_widget(delete_btn)
            btn_box.add_widget(close_btn)

            popup_content = BoxLayout(orientation='vertical')
            popup_content.add_widget(scroll_popup)
            popup_content.add_widget(btn_box)

            popup = Popup(title="Редактирование сессии", content=popup_content,
                          size_hint=(None,None), size=(650,600), auto_dismiss=False)

            def save_changes(instance):
                for i in range(len(session)):
                    session[i] = (session[i][0], editable_fields[i].text)
                btn.text = session[0][1]
                with open("sessions.json", "w", encoding="utf-8") as f:
                    json.dump(self.saved_sessions, f, ensure_ascii=False, indent=4)
                popup.dismiss()

            def delete_session(instance):
                if btn in self.answers_layout.children:
                    self.answers_layout.remove_widget(btn)
                if session in self.saved_sessions:
                    self.saved_sessions.remove(session)
                    with open("sessions.json", "w", encoding="utf-8") as f:
                        json.dump(self.saved_sessions, f, ensure_ascii=False, indent=4)
                popup.dismiss()

            save_changes_btn.bind(on_release=save_changes)
            delete_btn.bind(on_release=delete_session)
            close_btn.bind(on_release=lambda x: popup.dismiss())
            popup.open()

        self.show_session_popup = show_session_popup

        # ----------------------- Сохранение новой сессии -----------------------
        def saveanswers(instance):
            session = [(q, inp.text.strip()) for q, inp in zip(self.questions, self.inputs) if inp.text.strip()]
            if not session:
                return
            self.saved_sessions.append(session)
            btn = Button(text=session[0][1], size_hint_y=None, height=40,
                        background_color=(0.2, 0.6, 1, 0.8), color=(1, 1, 1, 1))
            self.answers_layout.add_widget(btn)
            btn.bind(on_release=lambda inst, s=session, b=btn: self.show_session_popup(s, b))
            for inp in self.inputs:
                inp.text = ""
            with open("sessions.json", "w", encoding="utf-8") as f:
                json.dump(self.saved_sessions, f, ensure_ascii=False, indent=4)

        save_btn.bind(on_release=saveanswers)

        # ----------------------- Кнопка открыть все ответы -----------------------
        def open_all_sessions(instance):
            for btn, session in zip(self.answers_layout.children[::-1], self.saved_sessions):
                self.show_session_popup(session, btn)

        open_all_btn.bind(on_release=open_all_sessions)

        # ----------------------- Навигация -----------------------
        dossier = Button(text="Досье", size_hint=(None, None), size=(100, 40), pos=(10, 10))
        plus = Button(text="+", size_hint=(None, None), size=(60, 40), pos=(10, 750))
        close = Button(text="Закрыть", size_hint=(None, None), size=(100, 40), pos=(690, 750))
        root.add_widget(dossier)
        root.add_widget(plus)
        root.add_widget(close)
        plus.opacity = close.opacity = 0

        dossier.bind(on_release=lambda x: (
            setattr(screen1, 'opacity', 1),
            setattr(plus, 'opacity', 1),
            setattr(close, 'opacity', 1),
            [setattr(r, 'opacity', 0) for r in root.children if isinstance(r, Ring)]
        ))

        plus.bind(on_release=lambda x: (
            setattr(screen2, 'opacity', 1),
            setattr(plus, 'opacity', 0)
        ))

        close.bind(on_release=lambda x: (
            setattr(screen1, 'opacity', 0),
            setattr(screen2, 'opacity', 0),
            setattr(plus, 'opacity', 0),
            setattr(close, 'opacity', 0),
            [setattr(r, 'opacity', 1) for r in root.children if isinstance(r, Ring)]
        ))

        return root

    def on_stop(self):
        """Сохраняет состояние колец и сессий при закрытии приложения"""
        rings = [child for child in self.root.children if isinstance(child, Ring)]
        rings_data = [ring.save_state() for ring in rings]
        with open("rings.json", "w", encoding="utf-8") as f:
            json.dump(rings_data, f, ensure_ascii=False, indent=4)

        with open("sessions.json", "w", encoding="utf-8") as f:
            json.dump(self.saved_sessions, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    CirclesApp().run()
