from flask import Blueprint, render_template
import folium
from folium.plugins import MiniMap

mapasbp = Blueprint('mapasbp', __name__)

@mapasbp.route('/api/mapa', methods=['GET'])
def mostrar_mapa():
    Alcaldia = folium.Map(location=[-17.39356, -66.15762], zoom_start=16)

    popuptext = "<b>Alcaldía de Cochabamba, mostrado por Brian Zegarra</b>"
    folium.Marker(
        location=[-17.39356, -66.15762],
        popup=popuptext
    ).add_to(Alcaldia)

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

    minimap = MiniMap(tile_layer="OpenStreetMap", toggle_display=True)
    Alcaldia.add_child(minimap)

    map_id = Alcaldia.get_name()

    # JS personalizado para el click en el mapa y postMessage al padre
    custom_js = f"""
function onMapClick(e) {{
    if (window.lastMarker) {{
        {map_id}.removeLayer(window.lastMarker);
    }}
    var lat = e.latlng.lat.toFixed(6);
    var lng = e.latlng.lng.toFixed(6);
    var popup = L.popup()
        .setLatLng(e.latlng)
        .setContent("Coordenadas seleccionadas:<br><b>Lat:</b> " + lat + "<br><b>Lng:</b> " + lng)
        .openOn({map_id});
    window.lastMarker = L.marker(e.latlng).addTo({map_id});
    console.log("Enviando coordenadas:", lat, lng);
    window.parent.postMessage({{ lat: lat, lng: lng }}, "*");
}}
{map_id}.on('click', onMapClick);
"""

    Alcaldia.get_root().html.add_child(folium.Element(f"""
<script>
{custom_js}
</script>
"""))

    map_html = Alcaldia._repr_html_()
    return render_template('Mapas.html', map_html=map_html)

@mapasbp.route('/api/mapah', methods=['GET'])
def mostrar_mapah():
    Alcaldia = folium.Map(
        location=[-17.31352, -66.28351],
        zoom_start=16,
        tiles='OpenStreetMap',
        attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors',
        name='Stamen Terrain',
        control_scale=True
    )

    # Marcador con popup
    popuptext = "<b>Ubicacion a analizar en el sistema HIDROALERT</b>"
    folium.Marker(
        location=[-17.31352, -66.28351],
        popup=popuptext,
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(Alcaldia)

    # Círculo decorativo
    folium.Circle(
        location=[-17.31352, -66.28351],
        color="purple",
        fill_color="red",
        radius=40,
        weight=4,
        fill_opacity=0.5,
        tooltip="Punto de análisis"
    ).add_to(Alcaldia)

    # Obtener el ID del mapa
    map_id = Alcaldia.get_name()

    # JS personalizado para clics en el mapa
    custom_js = f"""
    function onMapClick(e) {{
        if (window.lastMarker) {{
            {map_id}.removeLayer(window.lastMarker);
        }}
        var lat = e.latlng.lat.toFixed(6);
        var lng = e.latlng.lng.toFixed(6);
        var popup = L.popup()
            .setLatLng(e.latlng)
            .setContent("Coordenadas seleccionadas:<br><b>Lat:</b> " + lat + "<br><b>Lng:</b> " + lng)
            .openOn({map_id});
        window.lastMarker = L.marker(e.latlng).addTo({map_id});
        console.log("Enviando coordenadas:", lat, lng);
        window.parent.postMessage({{ lat: lat, lng: lng }}, "*");
    }}
    {map_id}.on('click', onMapClick);
    """

    # Inyección de JavaScript en el HTML del mapa
    Alcaldia.get_root().html.add_child(folium.Element(f"""
    <script>
    {custom_js}
    </script>
    """))

    # Renderizar el mapa en el HTML
    map_html = Alcaldia._repr_html_()
    return render_template('Mapash.html', map_html=map_html)
