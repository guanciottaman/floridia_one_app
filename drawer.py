import flet as ft

class MyDrawer(ft.NavigationDrawer):
    def __init__(self, page: ft.Page, route: str, on_change, **kwargs):
        super().__init__(**kwargs)
        self.route = route
        self.page = page
        self.on_change = on_change
        
        self.controls = [
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="Home",
                icon=ft.icons.HOME,
                selected_icon_content=ft.Icon(ft.icons.HOME_FILLED),
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.NEWSPAPER),
                label="Notizie",
                selected_icon=ft.icons.NEWSPAPER_OUTLINED,
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.RECYCLING),
                label="Differenziata",
                selected_icon=ft.icons.RECYCLING_OUTLINED,
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.MAP),
                label="Mappa",
                selected_icon=ft.icons.MAP_OUTLINED,
            )
        ]