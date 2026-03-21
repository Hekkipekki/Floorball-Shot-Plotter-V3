import os
from gui.layout import update_background_menu  # Importera funktionen för att uppdatera menyn
from utils.helpers import get_resource_path

def get_available_backgrounds(app):
    resources_path = get_resource_path("Resources")
    if not os.path.exists(resources_path):
        return []
    return [f for f in os.listdir(resources_path) if f.lower().endswith(".png")]

def init_background_files(app):
    # Läs in tillgängliga bakgrundsbilder
    app.bg_files = get_available_backgrounds(app)
    if app.bg_files:
        # Sätt första som standardval
        app.bg_choice.set(app.bg_files[0])
        app.selected_background.set(app.bg_files[0])
    else:
        # Om inga bilder finns, sätt till tomt värde
        app.bg_choice.set("")
        app.selected_background.set("")

    # Uppdatera bakgrundsmenyn så att den visar aktuella bakgrunder
    update_background_menu(app)

def set_background(app, bg_name):
    if bg_name in app.bg_files:
        app.selected_background.set(bg_name)
        # Ladda om bakgrundsbild och uppdatera plotten
        from gui.plot_controller import load_image, update_plot
        load_image(app)
        update_plot(app)
        # Uppdatera menyn för att reflektera aktiv bakgrund (valfritt)
