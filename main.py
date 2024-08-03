import flet as ft
from flet_core.canvas.canvas import ControlEvent
import flet.map as map
import FleetingViews as fleetingviews
import requests
from bs4 import BeautifulSoup

import asyncio
from dataclasses import dataclass
from datetime import datetime
import locale
import webbrowser

from drawer import MyDrawer

WEEKDAYS_ITA = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

cur_news_page: int = 1

@dataclass
class New:
    title: str | None = None
    summary: str | None = None
    link: str | None = None

def main(page: ft.Page):
    page.title = "Floridia One"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15
    
    locale.setlocale(locale.LC_TIME, locale="it_IT.UTF-8")

    organico_img = ft.Image(src="https://i.imgur.com/DfdlRW8.png", width=96, height=96)
    carta_img = ft.Image(src="https://i.imgur.com/RaZTm4Q.png", width=96, height=96)
    plastica_img = ft.Image(src="https://i.imgur.com/ReSnmMQ.png", width=96, height=96)
    vetro_img = ft.Image(src="https://i.imgur.com/Us2fwkB.png", width=96, height=96)
    indifferenziata_img = ft.Image(src="https://i.imgur.com/jGEdda0.png", width=96, height=96)
    pannolini_img = ft.Image(src="https://i.imgur.com/PsPSj7U.png", width=96, height=96)
    
    REC_TYPES_TO_IMGS = {
        "Organico, umido": organico_img,
        "Carta e Cartone": carta_img,
        "Plastica e alluminio": plastica_img,
        "Vetro": vetro_img,
        "Secco non riciclabile": indifferenziata_img,
        "Pannolini, pannoloni, traverse": pannolini_img
    }

    def create_cards_news(news):
        cards = []
        for new in news:
            card = ft.Card(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                title=ft.Text(value=new.title[:70]  + " ...", font_family="Montserrat"),  # pyright: ignore
                                subtitle=ft.Text(value=new.summary.replace("Vai alla Notizia", "")[:100] + " ...", font_family="Montserrat")
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

    async def load_news(page:int):
        news_lst = []
        r = requests.get(f"https://www.comune.floridia.sr.it/categoria/news/page/{page}")
        content = r.text
        soup = BeautifulSoup(content, "html.parser")
        news_block = soup.find("div", attrs={"id": "blog-item-holder"})
        news_containers = news_block.findAll("div", class_="gdl-blog-medium gdl-border-x bottom")  # pyright: ignore
        for new in news_containers:
            new_class = New()
            new_class.title = new.find("h2").text.strip()
            new_class.summary = new.find("div", attrs={"class": "blog-content"}).get_text(separator=' ', strip=True)
            new_class.link = new.find("a").get("href")
            news_lst.append(new_class)
        return news_lst

    def go_back(e=None):
        fv.go_back(20)

    def open_new(e, link):
        if page.platform not in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
            webbrowser.open(link)
            return
        fv.view_go("new_view")
        fv.working_view.controls.clear()
        r = requests.get(link)
        soup = BeautifulSoup(r.text, "html.parser")
        blog_content = soup.find("div", class_="blog-content")
        for paragraph in blog_content.findAll("p"): # pyright: ignore
            fv.append(
                "new_view",
                controls=[
                    ft.Text(paragraph.text.strip(), font_family="Montserrat", text_align=ft.TextAlign.CENTER)
                ]
            )
        fv.append(
            "new_view",
            controls=[
                ft.ElevatedButton("Back", on_click=go_back)
            ]
        )

    def load_today_recycle_types():
        recycle_types = ["Pannolini, pannoloni, traverse"]
        today_weekday = datetime.today().weekday()
        today_weekday_ita = WEEKDAYS_ITA[today_weekday]
        r = requests.get("https://floridia.raccolta-differenziata.it/calendario-raccolta-differenziata-domestiche/")
        content = r.text
        soup = BeautifulSoup(content, "html.parser")
        table_body = soup.find("tbody")
        for rec_type in table_body.findAll("tr"):  # pyright: ignore
            tds = rec_type.findAll("td")
            weekdays = tds[2].text.strip().split(", ")
            weekdays = [day.replace('Ã¬', 'ì') for day in weekdays]
            if today_weekday_ita not in weekdays:
                continue
            else:
                recycling_type = tds[1].text.strip()
                recycle_types.append(recycling_type)
        return recycle_types

    def handle_change(e):
        match e.control.selected_index:
            case 0:
                fv.view_go("home")
            case 1:
                fv.view_go("news")
            case 2:
                fv.view_go("differenziata")
            case 3:
                fv.view_go("mappa")

    home_drawer = MyDrawer(page, "home", handle_change)
    news_drawer = MyDrawer(page, "news", handle_change)
    differenziata_drawer = MyDrawer(page, "differenziata", handle_change)
    mappa_drawer = MyDrawer(page, "mappa", handle_change)
    new_view_drawer = MyDrawer(page, "new_view", handle_change)

    def show_home_drawer(e):
        page.open(home_drawer)

    home_hamburger_btn = ft.IconButton(
        icon=ft.icons.MENU,
        on_click=show_home_drawer
    )

    def show_news_drawer(e):
        page.open(news_drawer)

    news_hamburger_btn = ft.IconButton(
        icon=ft.icons.MENU,
        on_click=show_news_drawer
    )

    def show_differenziata_drawer(e):
        page.open(differenziata_drawer)

    differenziata_hamburger_btn = ft.IconButton(
        icon=ft.icons.MENU,
        on_click=show_differenziata_drawer
    )

    def show_mappa_drawer(e):
        page.open(mappa_drawer)

    mappa_hamburger_btn = ft.IconButton(
        icon=ft.icons.MENU,
        on_click=show_mappa_drawer
    )
    
    def show_new_view_drawer(e):
        page.open(mappa_drawer)

    new_view_hamburger_btn = ft.IconButton(
        icon=ft.icons.MENU,
        on_click=show_new_view_drawer
    )
    
    view_definitions = {
        "home": {
            'vertical_alignment': ft.MainAxisAlignment.CENTER,
            'horizontal_alignment': ft.CrossAxisAlignment.CENTER,
            "drawer": home_drawer
        },
        "news": {
            "vertical_alignment": ft.MainAxisAlignment.CENTER,
            "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
            "drawer": news_drawer
        },
        "differenziata": {
            'vertical_alignment': ft.MainAxisAlignment.CENTER,
            'horizontal_alignment': ft.CrossAxisAlignment.CENTER,
            "drawer": differenziata_drawer
        },
        "mappa": {
            'vertical_alignment': ft.MainAxisAlignment.CENTER,
            'horizontal_alignment': ft.CrossAxisAlignment.CENTER,
            "drawer": mappa_drawer
        },
        "new_view": {
            'vertical_alignment': ft.MainAxisAlignment.CENTER,
            'horizontal_alignment': ft.CrossAxisAlignment.CENTER,
        }
    }
    
    fv = fleetingviews.create_views(view_definitions=view_definitions, page=page)

    
    async def load_home():
        first_news = await load_news(1)
        print(first_news)
        cards = create_cards_news(first_news)
        print(cards)
        
        fv.append("home", controls=[
            ft.AppBar(
                leading=home_hamburger_btn,
                title=ft.Text("Floridia One", font_family="Montserrat")
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(  # pyright: ignore
                            content=ft.Text(
                                value="Benvenuti a Floridia One!",
                                font_family="Montserrat",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE
                            ),
                            padding=20
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.icons.CALENDAR_TODAY, size=24),
                                ft.Text(
                                    value=datetime.now().strftime("%A, %d %B %Y"),
                                    font_family="Montserrat",
                                    size=18,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=5
                        ),
                        ft.Container(
                            content=ft.Text(
                                value=f"Oggi devi uscire: {', '.join(load_today_recycle_types())}",
                                font_family="Montserrat",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.GREEN
                            ),
                            padding=10,
                        ),
                        ft.Container(
                            content=ft.Text(
                                value="Ultime notizie",
                                font_family="Montserrat",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ),
                        ft.GridView(
                            controls=cards[:3],  # Display only the top 3 news items
                            expand=1,
                            runs_count=3,
                            max_extent=600,
                            child_aspect_ratio=1.5,
                            spacing=10,
                            run_spacing=10,
                        ),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    text="Notizie",
                                    icon=ft.icons.NEWSPAPER,
                                    on_click=lambda e: page.go("/news"),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.colors.BLUE
                                    )
                                ),
                                ft.ElevatedButton(
                                    text="Differenziata",
                                    icon=ft.icons.RECYCLING,
                                    on_click=lambda e: page.go("/differenziata"),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.colors.GREEN
                                    )
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        ft.Text(
                            value="© 2024 Floridia One. Tutti i diritti riservati.",
                            font_family="Montserrat",
                            size=14,
                            color=ft.colors.GREY,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=20,
                ),
                padding=20
            )
        ])

    asyncio.run(load_home())

    async def load_more_news(e=None):
        global cur_news_page
        cur_news_page += 1
        print(cur_news_page)
        news = await load_news(cur_news_page)
        print(news)
        cards = create_cards_news(news)
        print(len(fv.actual_view.controls[1].controls))
        fv.actual_view.controls[1].controls.extend(cards)
        print(len(fv.actual_view.controls[1].controls))
        print("Added")
        page.update()

    def on_click_wrapper(event):
        asyncio.run(load_more_news(event))

    async def append_to_news():
        news = await load_news(cur_news_page)
        cards = create_cards_news(news)
        fv.append(
            "news",
            controls=[
                ft.AppBar(
                    leading=news_hamburger_btn,
                    title=ft.Text("Floridia One", font_family="Montserrat")
                ),
                ft.GridView(
                    controls=cards,  # pyright: ignore
                    expand=1,
                    runs_count=3,
                    max_extent=600,
                    child_aspect_ratio=1.3,
                    spacing=5,
                    run_spacing=5,
                ),
                ft.ElevatedButton(
                    "Carica altro",
                    on_click=on_click_wrapper
                )
            ]
        )
    
    asyncio.run(append_to_news())

    today_recycle_types = load_today_recycle_types()
    rec_types_cards = []

    for rec_type in today_recycle_types:
        rec_card = ft.Card(
            ft.Container(
                content=ft.Column(
                    controls=[
                        REC_TYPES_TO_IMGS[rec_type],
                        ft.Text(rec_type, font_family="Montserrat", size=16)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                    spacing=10
                ),
                alignment=ft.alignment.center,
                padding=20
            ),
            width=120,
            height=150,
            margin=10
        )
        rec_types_cards.append(rec_card)

    fv.append("differenziata", controls=[
       ft.AppBar(
           leading=differenziata_hamburger_btn,
           title=ft.Text("Floridia One", font_family="Montserrat")
       ),
       ft.Text(f"Oggi devi uscire:"),
       ft.GridView(
           controls=rec_types_cards,  # pyright: ignore
           expand=1,
           runs_count=3,
           max_extent=600,
           child_aspect_ratio=1.5,
           spacing=5,
           run_spacing=5,
       )
   ])
    
    initial_center = map.MapLatitudeLongitude(37.0834300, 15.1533200)
    initial_zoom = 15  # Adjust zoom level as needed
    
    fv.append("mappa",
        controls=[
        ft.AppBar(
            leading=mappa_hamburger_btn,
            title=ft.Text("Floridia One", font_family="Montserrat")
        ),
        map.Map(
                    expand=True,
                    configuration=map.MapConfiguration(
                        initial_center=initial_center,
                        initial_zoom=initial_zoom,
                        interaction_configuration=map.MapInteractionConfiguration(
                            flags=map.MapInteractiveFlag.ALL
                        ),
                        on_init=lambda e: print("Map initialized"),
                    ),
                    layers=[
                        map.TileLayer(
                            url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                            on_image_error=lambda e: print("TileLayer Error"),
                        )
                    ],
                ),
        ]
    )

    page.update()
    fv.view_go("home")

ft.app(main, name="Floridia One", assets_dir="assets")
