import kivy.app
import kivy.uix.label


### Add sane defaults to kivy.app.App ###
#

def app_set_layout(self, layout):
    self.layout = layout

def app_ui_builder(self):
    if not hasattr(self, "layout"):
        print("!!! Warning: Using default layout: GridLayout  (Layout may be set with App.set_layout())")
        self.layout = kivy.uix.gridlayout.GridLayout()

    return self.layout

# Adds widget to the set layout (if no layout is set, a GridLayout is created)
def app_add_widget(self, widget):
    if not hasattr(self, "layout"):
        print("!!! Warning: Using default layout: GridLayout  (Layout may be set with App.set_layout())")
        self.layout = kivy.uix.gridlayout.GridLayout()

    self.layout.add_widget(widget)

kivy.app.App.set_layout = app_set_layout
kivy.app.App.build      = app_ui_builder
kivy.app.App.add_widget = app_add_widget

#
##################################


### Add sane background color support to elements lacking it ###
#

def update_rect(self, *args):
	if hasattr(self, "background_color"):
		self.canvas.before.clear()
		print("Update rect", self.background_color)
		self.canvas.before.add(kivy.graphics.Color(*self.background_color))
		self.canvas.before.add(kivy.graphics.Rectangle(pos=self.pos, size=self.size))

def bg_init(self, **kwarg):
	if "background_color" in kwarg:
		self.background_color = kwarg["background_color"]
		del kwarg["background_color"]
		self.bind(pos=self.update_rect, size=self.update_rect)

	self.__class__.__old_init__(self, **kwarg)


# Add sane backgroundd color support to Label
# (This pattern should work for any widget, but
# don't use it for widgets that already have a
# similar mechanic, like TextInput, as it may
# screw up their rendering.)
kivy.uix.label.Label.update_rect = update_rect
kivy.uix.label.Label.__old_init__ = kivy.uix.label.Label.__init__
kivy.uix.label.Label.__init__ = bg_init

#
###############################################################





