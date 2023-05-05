# Kivy-Sanity-Fix
Kivy is missing critical GUI features and has some really dumb defaults.  This is intended to make Kivy usable, since there really isn't any good Android alternative to Kivy right now.


## How it works
This module does not add any directly callable functions, classes, or anything else.  Instead of subclassing, requiring the user to learn another API and cluttering the namespace, this module elects to use Python's extensive metaprogramming powers to modify Kivy's classes directly, making the fixes transparent.

## Current Features

### kivy.app.App Class
Normally, Kivy requires the user to subclass App to do basic tasks like adding a root object.  In simple applications, this clutters the code and makes it less readable by forcing a heavily object oriented approach where it is neither necessary nor good practice.  This module fixes this by adding some methods and replacing App.build() with sane defaults.

#### App.set_layout()
This method takes a single argument, which should be a subclass of Widget.  As the name suggests, it is intended to be used to add a layout for the root widget, however, it can be used to add any Widget as the root widget.  Note that unlike Kivy's default, when set this way, the App instance keeps track of its root widget in the App.layout attribute, so you don't have to keep track of it separately, if you prefer not to.

#### App.add_widget()
This method takes a single argument, which should be a subclass of Widget.  If the layout has been set, that widget will be added to the layout with its own .add_widget() method.  This allows the the App instance to be treated as the layout in terms of adding subelements, which is common practice with many GUI systems (where the layout is treated as a property of the element it is applied to rather than as a widget itself).  Note that other interactions with the layout need to address it directly, which can be done by addressing it through the App instance with instance.layout.  If no layout has been set when this is called, it will automatically create and add a GridLayout by default.

#### App.build()
This method is not intended to be called directly by the user.  It is called automatically by App.run().  It is expected to return the root widget of the App instance.  Kivy's default behavior is to generate a new Widget object and return that, which is not a sane default, as Widget is basically a virtual class designed to be inherited from when creating new widgets.  This violation of good practice and general sanity is why App normally has to be subclassed to be useful.  This module replaces Appp.build() with a more sane alternative.  Instead of returning a new Widget, it will return whatever is in the instance's layout property.  If the App instance does not have a layout property (meaning no layout has been set), it will generate a GridLayout and set the instance's layout property to that, before returning it.  Combined with the other two added methods, this allows pure instances of App to be used without any subclassing, and since the most common use of App will generally be to add a layout and then build the UI within that layout, without making any other changes to the App class, this is far more sane than Kivy's own default of forcing the user into an object oriented ideology even when it doesn't make sense and reduces overall code quality.


### kivy.uix.label.Label Class
Kivy Widgets do not have any built-in means of setting or changing the background color by default.  Certain widgets have this capability, for example TextInput, but it is not a feature of Widgets in general.  This absurd design choice has caused a great deal of consternation and general difficulty for Kivy users, if the vast number of complaints and frustrated questions found through a simple web search mean anything.  Perhaps the single most common target of these complaints and frustrations is the Label class.  Most GUI frameworks provide the ability to set and change background color as a stock feature of _every_ widget, but for some reason Kivy decided not to.  Of course, it _is_ possible to change the background color, but this must be done by hacking the canvas object of the widget directly, which is _the recommended practice_ by Kivy devs!

This module provides a fix for this incredibly poor design choice, for the Label class.  This fix _should be_ trivially applicable to other Widget subclasses as well, but it comes with some significant limitations.  The solution is to build the above mentioned canvas hack into the Label object using Python's extensive metaprogramming powers, to avoid subclassing.  The limitation is that if you want to apply your own canvas hacks for customization purposes, there is some potential for this to get in your way.  This is easily avoided, however, by _not_ using the mechanics provided here to set a background color.  If the Label object does not have a background_color attribute, the added code will never be executed.  If you need to store your own background color in your Label object or subclass, make sure to name it something else.  (If you are subclassing, another option is to override the update_rect() method with an empty method or better yet with your own drawing code, in which case the background_color attribute is free game.)

#### Label.__init__()
The only change you need to worry about directly is that the constructor has been modified to accept a background_color named argument.  This should take the form of a 4-tuple, arranged (R, G, B, A), where each element is a float between 0 and 1.  It's that simple.  When you create your label instance, you can set the background color in the constructor.  If you want to add the background color later, add a background_color attribute to the object by assigning it a 4-tuple in the above mentioned format.  You can also change the background color by assigning the attribute a new value in the appropriate format.

#### Label.update_rect()
Don't read this if you aren't interested in the inner workings.  Otherwise, continue!  This function does the actual rendering of the background.  It is bound to the position and size update events for the object (the binding is done in the modified constructor), to ensure that the background is consistently drawn in the correct location at the correct size.  Note that this clears the canvas.before render queue each time such an event occurs, so if you want to add your own rendering stuff, you will either need to do it the regular canvas queue or the canvas.after queue (which will likely overwrite the label text...), or you will want to render the background yourself instead of using this mechanic (in which case, don't set a background color at all and don't create a background_color attribute in the object).  Alternatively, you could subclass Label and include your own update_rect() method, which calls the parent method first and then adds additional drawing commands of its own after that.

### Adding Background Colors to Other Widgets
Currently only Label gets the background color treatment, but it shouldn't be difficult to add this to other Widgets.  In the background color section of the module file, you will see two function definitions and then three lines doing some assignment/reassignment on the Label class.  To add this feature to another Widget, you can replicate those three assignment lines, but apply them to that Widget instead of Label.

The process here is simple.  First, we add the update_rect() function as a method to the Widget subclass that we want to add the background color feature to.  Then we reassign the current constructory to __old_init__(), because we need to keep it to call in the new constructor, to avoid messing anything up.  Then we assign the new constructor (bg_init()) to overwrite the original constructor.  bg_init() calls the old constructor after checking for the background_color argument and setting the property if there is one and removing the argument from the dictionary (because the old constructor raises exceptions for unrecognized arguments).  This process should work for any Widget subclass (and even for Widget itself, though I don't think that's a good idea as that would apply it to all Widget subclasses, and there's a very good reason not to do that).

!!! Warning: _Don't_ just apply this to every Widget that you want to put a background color on.  Kivy is very inconsistent about how it handles Widget rendering, and this technique can screw up widgets that don't follow the right rendering pattern.  My experience with this is extremely limited, however, the TextInput widget _definitely does not_ work properly with this.  For some reason, setting a color in canvas.before overrides _all other color settings_ in the TextInput class, causing it to render everything in that color.  This way, you get background, foreground, _and_ cursor colors all the same, making the text input element unreadable.  At first I even thought it just removed the functionality, but I am able to select the text, though the selection box only reveals the length of the text, not the text itself.  I have no idea why this happens (though I suspect TextInput does most of its rendering in canvas.before, causing the background color box to be drawn over the top of the other stuff), but it doesn't actually matter.  TextInput is one of the few Widgets that does have a background_color constructor argument, so there's no actual need to use this for it.  I would suggest only applying this feature to Widgets that don't already support background coloring.  I can't promise that some that don't already support it won't also fail though.  I'll try to add more myself as I find I need them, and I'll maintain a list in the source code comments of Widgets that it breaks.


Anyhow, I hope this helps others.  I really wish python-for-android had just ported tkinter to Android instead of trying to reinvent the wheel and quite frankly, doing a terrible job of it.  As I come across other issues with Kivy, I'll try to update this with additional sanity/quality-of-life fixes, if I have time to do so.