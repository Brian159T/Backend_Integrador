from flask import Blueprint, render_template
import folium
from folium.plugins import MiniMap

mapasbp = Blueprint('mapasbp', __name__)

@mapasbp.route('/mapa', methods=['GET'])
def mostrar_mapa():
    popuptext = "<b>Alcaldía de Cochabamba, mostrado por Brian Zegarra</b>"

    
    Alcaldia = folium.Map(location=[-17.39356, -66.15762], zoom_start=16)

    
    folium.Marker(location=[-17.39356, -66.15762], popup=popuptext).add_to(Alcaldia)
    folium.Circle(
        location=[-17.39356, -66.15762],
        color="purple",
        fill_color="red",
        radius=40,
        weight=4,
        fill_opacity=0.5,
        tooltip="Alcaldía de Cochabamba"
    ).add_to(Alcaldia)

    
    stamen_layer = folium.TileLayer(
        tiles='https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
        attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors',
        name='Stamen Terrain'
    )
    stamen_layer.add_to(Alcaldia)

    
    minimap_layer = folium.TileLayer(
        tiles='https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
        attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors'
    )
    
    

    
    minimap = MiniMap(tile_layer="OpenStreetMap", toggle_display=True)
    Alcaldia.add_child(minimap)

    
    map_html = Alcaldia._repr_html_()

    return render_template('Mapas.html', map_html=map_html)





  