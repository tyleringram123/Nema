import pandas as pd
import folium
import googlemaps
import locale

# Function to geocode address using Google Maps
def geocode_address(gmaps, address):
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
    except Exception as e:
        print(f"Error occurred while geocoding address {address}: {e}")
    return None, None

# Initialize Google Maps client
gmaps = googlemaps.Client(key='YOURAPIKEY')

# Set the locale for currency formatting
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Load the Excel file
data = pd.read_excel('Sample Data.xlsx')

# Initialize an empty map centered around the first geocoded location
initial_lat, initial_lng = geocode_address(gmaps, data['Location'][0])
mymap = folium.Map(location=[initial_lat, initial_lng], zoom_start=4)

# Define AUM ranges and corresponding colors
aum_ranges = {
    'blue': (1_000_000, 4_999_999),
    'yellow': (5_000_000, 9_999_999),
    'orange': (10_000_000, 19_999_999),
    'green': (20_000_000, 999_999_999),
}

# Create a FeatureGroup for each AUM range and add it to the map
feature_groups = {}
for color, (min_aum, max_aum) in aum_ranges.items():
    fg = folium.FeatureGroup(name=f'AUM: ${min_aum:,} - ${max_aum:,}', overlay=True, show=True)
    mymap.add_child(fg)
    feature_groups[color] = fg

# Loop through the DataFrame and add each location as a marker on the map
for index, row in data.iterrows():
    lat, lng = geocode_address(gmaps, row['Location'])
    if lat and lng:
        aum_no_cents = int(row['AUM'])
        formatted_aum = "${:,}".format(aum_no_cents)

        tooltip = folium.Tooltip(f"""<div style="white-space: nowrap;">
                                        <b>Cust ID:</b> {row['Cust ID']}<br>
                                        <b>Client:</b> {row['Client']}<br>
                                        <b>AUM:</b> {formatted_aum}
                                    </div>""")

        marker_color = None
        for color, (min_aum, max_aum) in aum_ranges.items():
            if min_aum <= aum_no_cents <= max_aum:
                marker_color = color
                break

        # Add the marker to the appropriate feature group if AUM range is found
        if marker_color:
            folium.Marker([lat, lng], tooltip=tooltip, icon=folium.Icon(color=marker_color)).add_to(feature_groups[marker_color])

mymap.add_child(folium.LayerControl())

mymap.save('map.html')

#print("Map has been saved as map.html")
