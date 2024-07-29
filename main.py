import flet as ft
from flet_core.canvas.canvas import ControlEvent
import requests
from bs4 import BeautifulSoup

from dataclasses import dataclass
from datetime import datetime
import webbrowser


#RECYCLING_TYPES_NAMES: list[str] = ["Organico, umido", "Carta e Cartone", "Plastica e Alluminio", "Vetro",
#    "Secco non riciclabile", "Pannolini, pannoloni, traverse"]

WEEKDAYS_ITA: list[str] = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

@dataclass
class New:
    title: str | None = None
    summary: str | None = None
    link: str | None = None


def main(page: ft.Page):
    page.title = "Floridia One"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15

    organico_img = ft.Image(src="organico.png", width=96, height=96)
    carta_img = ft.Image(src="carta.png", width=96, height=96)
    plastica_img = ft.Image(src="plastica.png", width=96, height=96)
    vetro_img = ft.Image(src="vetro.png", width=96, height=96)
    indifferenziata_img = ft.Image(src="indifferenziata.png", width=96, height=96)
    pannolini_img = ft.Image(src="pannolini.png", width=96, height=96)

    def create_cards_news() -> list[ft.Card]:
        news = load_news()
        cards = []
        for new in news:
            card = ft.Card(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.NEWSPAPER),
                                title=ft.Text(value=new.title, font_family="Montserrat"),  # pyright: ignore
                                subtitle=ft.Text(value=new.summary, font_family="Montserrat")
                            ),
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Leggi la notizia completa",
                                        on_click=lambda e, link=new.link: open_new(e, link)  # pyright: ignore
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            )
                        ]
                    ),
                    width=400,
                    padding=10
                )
            )
            cards.append(card)
        return cards

    def load_news() -> list[New]:
        news_lst: list = []
        r = requests.get("https://www.comune.floridia.sr.it/categoria/news/")
        content = r.text
        soup = BeautifulSoup(content, "html.parser")
        news_block = soup.find("div", attrs={"id": "blog-item-holder"})
        news_containers = news_block.findAll("div", class_="gdl-blog-medium gdl-border-x bottom")  # pyright: ignore
        for new in news_containers:
            new_class: New = New()
            new_class.title = new.find("h2").text.strip()
            new_class.summary = new.find("div", attrs={"class": "blog-content"}).get_text(separator=' ', strip=True)
            new_class.link = new.find("a").get("href")
            news_lst.append(new_class)
        return news_lst

    def open_new(e: ControlEvent, link: str) -> None:
        if page.platform not in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
            webbrowser.open(link)
            return
        wv = ft.WebView(link,
                        expand=True,
                        on_page_started=lambda _: print("Page started"),
                        on_page_ended=lambda _: print("Page ended"),
                        on_web_resource_error=lambda e: print("Page error:", e.data)
                        )
        page.clean()
        page.add(wv)

    def load_today_recycle_types() -> list[str]:
        recycle_types = []
        today_weekday = datetime.today().weekday()
        today_weekday_ita = WEEKDAYS_ITA[today_weekday]
        r = requests.get("https://floridia.raccolta-differenziata.it/calendario-raccolta-differenziata-domestiche/")
        content = r.text
        soup = BeautifulSoup(content, "html.parser")
        table_body = soup.find("tbody")
        for rec_type in table_body.findAll("tr"): # pyright: ignore
            tds = rec_type.findAll("td")
            weekdays = tds[2].text.strip().split(", ")
            if today_weekday_ita not in weekdays:
                continue
            else:
                recycling_type = tds[1].text.strip()
                recycle_types.append(recycling_type)
        return recycle_types

    def home_view():
        page.views.append(
            ft.View(
                "/",
                controls=[
                    ft.AppBar(
                        leading=hamburger_btn,
                        title=ft.Text("Floridia One", font_family="Montserrat")
                    ),
                    ft.Text("Home View", font_family="Montserrat")
                ]
            )
        )
        page.update()

    def news_view():
        print("Creating news view...")
        page.views.append(
            ft.View(
                "/news",
                controls=[
                    ft.AppBar(
                        leading=hamburger_btn,
                        title=ft.Text("Floridia One", font_family="Montserrat")
                    ),
                    ft.GridView(
                        controls=create_cards_news(), # pyright: ignore
                        expand=1,
                        runs_count=3,
                        max_extent=600,
                        child_aspect_ratio=1.5,
                        spacing=5,
                        run_spacing=5,
                    )
                ]
            )
        )
        page.update()
            
    def differenziata_view():
        print(load_today_recycle_types())
        page.views.append(
            ft.View(
                "/differenziata",
                controls=[
                    ft.AppBar(
                        leading=hamburger_btn,
                        title=ft.Text("Floridia One", font_family="Montserrat")
                    ),
                    ft.Text(f"Oggi devi uscire:"),
                ]
            )
        )
        page.update()

    def handle_change(e: ControlEvent):
        match e.control.selected_index:
            case 0:
                page.go("/")
            case 1:
                page.go("/news")
            case 2:
                page.go("/differenziata")

    drawer = ft.NavigationDrawer(
        on_change=handle_change,
        controls=[
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
            )
        ]
    )

    
    

    hamburger_btn = ft.IconButton(
        icon=ft.icons.MENU,
        on_click=lambda e: page.open(drawer)
    )

    def route_change(route):
        page.views.clear()
        home_view()
        if page.route == "/news":
            news_view()
        elif page.route == "/differenziata":
            differenziata_view()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route) # pyright: ignore
    
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.appbar = ft.AppBar(
        leading=hamburger_btn,
        title=ft.Text("Floridia One", font_family="Montserrat")
    )
    page.drawer = drawer
    page.update()
    page.go(page.route)

ft.app(main, name="Floridia One", assets_dir="assets")
