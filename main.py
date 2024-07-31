import flet as ft
from flet_core.canvas.canvas import ControlEvent
import FleetingViews as fleetingviews
import requests
from bs4 import BeautifulSoup

import asyncio
from dataclasses import dataclass
from datetime import datetime
import webbrowser


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
    
    REC_TYPES_TO_IMGS = {
        "Organico, umido": organico_img,
        "Carta e Cartone": carta_img,
        "Plastica e Alluminio": plastica_img,
        "Vetro": vetro_img,
        "Secco non riciclabile": indifferenziata_img,
        "Pannolini, pannoloni, traverse": pannolini_img
    }

    def create_cards_news(news: list[New]) -> list[ft.Card]:
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

    async def load_news() -> list[New]:
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

    def handle_change(e: ControlEvent):
        match e.control.selected_index:
            case 0:
                fv.view_go("/home")
            case 1:
                fv.view_go("/news")
            case 2:
                fv.view_go("/differenziata")
            case 3:
                fv.view_go("/eventi")

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
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.EVENT),
                label="Eventi",
                selected_icon=ft.icons.RECYCLING_OUTLINED,
            )
        ]
    )

    def show_drawer(e):
        page.open(drawer)

    hamburger_btn = ft.IconButton(
        icon=ft.icons.MENU,
        on_click=show_drawer
    )

    view_definitions = {
        "home": {
            'vertical_alignment': ft.MainAxisAlignment.CENTER,
            'horizontal_alignment': ft.CrossAxisAlignment.CENTER
        },
        "news": {
            "vertical_alignment": ft.MainAxisAlignment.CENTER,
            "horizontal_alignment": ft.CrossAxisAlignment.CENTER
        },
        "differenziata": {
            'vertical_alignment': ft.MainAxisAlignment.CENTER,
            'horizontal_alignment': ft.CrossAxisAlignment.CENTER
        },
        "eventi": {
            'vertical_alignment': ft.MainAxisAlignment.CENTER,
            'horizontal_alignment': ft.CrossAxisAlignment.CENTER
        }
    }
    
    fv = fleetingviews.create_views(view_definitions=view_definitions, page=page)
    
    fv.append("home", controls=[
            ft.AppBar(
                leading=hamburger_btn,
                title=ft.Text("Floridia One", font_family="Montserrat")
            ),
            ft.Text("Home View", font_family="Montserrat")
        ]
    )
    
    async def append_to_news():
        news = await load_news()
        cards = create_cards_news(news)
        fv.append("news", controls=[
                ft.AppBar(
                    leading=hamburger_btn,
                    title=ft.Text("Floridia One", font_family="Montserrat")
                ),
                ft.GridView(
                    controls=cards, # pyright: ignore
                    expand=1,
                    runs_count=3,
                    max_extent=600,
                    child_aspect_ratio=1.5,
                    spacing=5,
                    run_spacing=5,
                )
            ]
        )
    asyncio.run(append_to_news())

    today_recycle_types = load_today_recycle_types()
    rec_types_cards = []

    for rec_type in today_recycle_types:
        rec_card = ft.Card(
            ft.Column([
                REC_TYPES_TO_IMGS[rec_type],
                ft.Text(rec_type, font_family="Montserrat")
            ])
        )
        rec_types_cards.append(rec_card)

    fv.append("differenziata", controls=[
       ft.AppBar(
           leading=hamburger_btn,
           title=ft.Text("Floridia One", font_family="Montserrat")
       ),
       ft.Text(f"Oggi devi uscire:"),
       
   ])
    

    page.drawer = drawer

    appbar = ft.AppBar(
        leading=hamburger_btn,
        title=ft.Text("Floridia One", font_family="Montserrat")
    )

    page.appbar = appbar

    page.update()
    fv.view_go("home")

ft.app(main, name="Floridia One", assets_dir="assets")
