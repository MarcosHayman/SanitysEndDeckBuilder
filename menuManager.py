from typing import Callable
from traceback import print_exc

# The function given to the options should return a string with an operation notification, or empty if you want the loop to break
def createMenu(introduction: str | Callable, options: dict, prologue="", intro_arg=None, option_arg=None, option_func_arg=None):
    loop = True
    notification = ""
    while loop:
        if isinstance(introduction, Callable):
            intro_text = introduction() if intro_arg is None else introduction(intro_arg)
        else:
            intro_text = introduction
        if notification != "":
            print("\n** " + notification + "\n")
        print(intro_text + "\n")
        keys = list(options.keys())
        for i, option in enumerate(keys):
            if isinstance(option, Callable):
                print(f"{i+1}. {option() if option_arg is None else option(option_arg)}")
            else:
                print(f"{i+1}. {option}")
        selection = input(prologue + "\n").strip()
        if selection in keys:
            notification = options[selection]()
            loop = notification != None and notification != ""
        else:
            try:
                int_sel = int(selection.strip())
                notification = options[keys[int_sel-1]]() if option_func_arg is None else options[keys[int_sel-1]](option_func_arg)
                loop = notification != None and notification != ""
            except Exception as e:
                print_exc()
                notification = "Couldn't find option, try again"

