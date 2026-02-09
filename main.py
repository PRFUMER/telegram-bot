from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
import math

Window.clearcolor = (0, 0, 0, 1)

BASE = "/home/anwar/Downloads/Python-3.9.25/Python/Python Basics/ConnectionCardPics/"

BACKGROUND = BASE + "crimeboard.png"

CIRCLE1 = BASE + "smallestcirucle.png"
CIRCLE2 = BASE + "meddiumcirucle.png"
CIRCLE3 = BASE + "largecirucle.png"
CIRCLE4 = BASE + "largestcirucle.png"

LABEL1 = BASE + "closestconnection.png"
LABEL2 = BASE + "connectionofinterest.png"
LABEL3 = BASE + "productionofconnection.png"
LABEL4 = BASE + "connectionofdevelopment.png"


class CrimeBoard(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.bind(mouse_pos=self.on_mouse_move)
        self.bind(size=self.update_canvas, pos=self.update_canvas)

        # Масштабы
        self.normal_scale = 1.0
        self.hover_scale = 1.2

        self.circle1_scale = self.normal_scale
        self.circle2_scale = self.normal_scale
        self.circle3_scale = self.normal_scale
        self.circle4_scale = self.normal_scale

        # Hover-флаги
        self.circle1_hovered = False
        self.circle2_hovered = False
        self.circle3_hovered = False
        self.circle4_hovered = False

        # Список крестиков
        # Каждый элемент: {"rel_pos": (dx, dy), "size": 25, "lines": (line1, line2, color)}
        self.crosses = []

        with self.canvas:
            # фон
            self.bg_color = Color(1, 1, 1, 1)
            self.bg = Rectangle()

            # круги
            self.c1_color = Color(1, 1, 1, 1)
            self.c1 = Rectangle()
            self.c2_color = Color(1, 1, 1, 1)
            self.c2 = Rectangle()
            self.c3_color = Color(1, 1, 1, 1)
            self.c3 = Rectangle()
            self.c4_color = Color(1, 1, 1, 1)
            self.c4 = Rectangle()

            # Labels
            self.l1 = Rectangle()
            self.l2 = Rectangle()
            self.l3 = Rectangle()
            self.l4 = Rectangle()

        Clock.schedule_once(self.load_textures, 0)
        Clock.schedule_once(self.show_labels_once, 10)

    def load_textures(self, dt):
        self.bg.source = BACKGROUND
        self.c1.source = CIRCLE1
        self.c2.source = CIRCLE2
        self.c3.source = CIRCLE3
        self.c4.source = CIRCLE4

        self.l1.source = LABEL1
        self.l2.source = LABEL2
        self.l3.source = LABEL3
        self.l4.source = LABEL4

        self.update_canvas()

    def show_labels_once(self, dt):
        self.update_canvas()
        Clock.schedule_once(self.hide_labels_once, 10)

    def hide_labels_once(self, dt):
        self.l1.source = ''
        self.l2.source = ''
        self.l3.source = ''
        self.l4.source = ''

    def update_canvas(self, *args):
        # фон
        self.bg.pos = self.pos
        self.bg.size = self.size

        # circle1
        w1 = self.width * self.circle1_scale
        h1 = self.height * self.circle1_scale
        self.c1.size = (w1, h1)
        self.c1.pos = (self.center_x - w1 / 2, self.center_y - h1 / 2)

        # circle2
        w2 = self.width * self.circle2_scale
        h2 = self.height * self.circle2_scale
        self.c2.size = (w2, h2)
        self.c2.pos = (self.center_x - w2 / 2, self.center_y - h2 / 2)

        # circle3
        w3 = self.width * self.circle3_scale
        h3 = self.height * self.circle3_scale
        self.c3.size = (w3, h3)
        self.c3.pos = (self.center_x - w3 / 2, self.center_y - h3 / 2)

        # circle4
        w4 = self.width * self.circle4_scale
        h4 = self.height * self.circle4_scale
        self.c4.size = (w4, h4)
        self.c4.pos = (self.center_x - w4 / 2, self.center_y - h4 / 2)

        # Labels
        for label in (self.l1, self.l2, self.l3, self.l4):
            label.pos = self.pos
            label.size = self.size

        # Перерисовываем крестики относительно circle4
        for cross in self.crosses:dx, dy = cross["rel_pos"]
            size = cross["size"]
            cx, cy = self.center_x, self.center_y
            scale = self.circle4_scale

            mx = cx + dx * scale
            my = cy + dy * scale

            cross["lines"][0].points = [mx - size, my - size, mx + size, my + size]
            cross["lines"][1].points = [mx - size, my + size, mx + size, my - size]

    # Анимации
    def animate_circle1(self, scale):
        Animation.stop_all(self, 'circle1_scale')
        anim = Animation(circle1_scale=scale, duration=0.15, t='out_quad')
        anim.bind(on_progress=lambda *_: self.update_canvas())
        anim.start(self)

    def animate_circle2(self, scale):
        Animation.stop_all(self, 'circle2_scale')
        anim = Animation(circle2_scale=scale, duration=0.15, t='out_quad')
        anim.bind(on_progress=lambda *_: self.update_canvas())
        anim.start(self)

    def animate_circle3(self, scale):
        Animation.stop_all(self, 'circle3_scale')
        anim = Animation(circle3_scale=scale, duration=0.15, t='out_quad')
        anim.bind(on_progress=lambda *_: self.update_canvas())
        anim.start(self)

    def animate_circle4(self, scale):
        Animation.stop_all(self, 'circle4_scale')
        anim = Animation(circle4_scale=scale, duration=0.15, t='out_quad')
        anim.bind(on_progress=lambda *_: self.update_canvas())
        anim.start(self)

    # Hover
    def on_mouse_move(self, window, pos):
        mx, my = pos
        cx, cy = self.center
        dist = math.sqrt((mx - cx) ** 2 + (my - cy) ** 2)

        r1 = min(self.width, self.height) * 0.15
        r2 = min(self.width, self.height) * 0.25
        r3 = min(self.width, self.height) * 0.35
        r4 = min(self.width, self.height) * 0.45

        tolerance = 60

        hover1 = abs(dist - r1) <= tolerance
        hover2 = abs(dist - r2) <= tolerance
        hover3 = abs(dist - r3) <= tolerance
        hover4 = abs(dist - r4) <= tolerance

        if hover1 != self.circle1_hovered:
            self.circle1_hovered = hover1
            self.animate_circle1(self.hover_scale if hover1 else self.normal_scale)

        if hover2 != self.circle2_hovered:
            self.circle2_hovered = hover2
            self.animate_circle2(self.hover_scale if hover2 else self.normal_scale)

        if hover3 != self.circle3_hovered:
            self.circle3_hovered = hover3
            self.animate_circle3(self.hover_scale if hover3 else self.normal_scale)

        if hover4 != self.circle4_hovered:
            self.circle4_hovered = hover4
            self.animate_circle4(self.hover_scale if hover4 else self.normal_scale)

    # Правый клик на circle4
    def on_touch_down(self, touch):
        if touch.button == 'right':
            mx, my = touch.pos
            w4 = self.width * self.circle4_scale
            h4 = self.height * self.circle4_scale
            cx, cy = self.center_x, self.center_y

            if (cx - w4 / 2 <= mx <= cx + w4 / 2) and (cy - h4 / 2 <= my <= cy + h4 / 2):
                # Вычисляем относительное положение крестика к центру круга
                dx = (mx - cx) / self.circle4_scale
                dy = (my - cy) / self.circle4_scale
                size = 25

                with self.canvas:
                    color = Color(1, 0, 0, 1)
                    line1 = Line(points=[mx - size, my - size, mx + size, my + size], width=2)
                    line2 = Line(points=[mx - size, my + size, mx + size, my - size], width=2)
                    self.crosses.append({"rel_pos": (dx, dy), "size": size, "lines": (line1, line2, color)})

        return super().on_touch_down(touch)


class CrimeBoardApp(App):
    def build(self):
        return CrimeBoard()


if __name__ == "__main__":
    CrimeBoardApp().run()