import folium

# MMU Cyberjaya approximate coordinates
mmu_center = [2.9277816137707204, 101.64190123388995]

# Initialize map
mmu_map = folium.Map(location=mmu_center, zoom_start=17)

# Building coordinates
buildings = {
    'DTC': {
        'coords': [2.929218001348703, 101.64243684179341],
    },

    'FCI': {
        'coords': [2.9291654299019148, 101.64057166571482],
    },

    'FOM': {
        'coords': [2.9300947248194165, 101.64130911229677],
    },

    'FOE': {
        'coords': [2.92660434513222, 101.64118197322395],
    },

    'FCM': {
        'coords': [2.9262734371401344, 101.6431866497752],
    },
    
    'MPH': {
        'coords': [2.928231851893708, 101.6424075166555],
    },
    
    'STADIUM': {
        'coords': [2.9280263906308175, 101.64424507685604],
    },

    'SPORTS COMPLEX': {
        'coords' : [3.0459,101.6163],
    },

    'SWIMMING POOL COMPLEX': {
        'coords' : [2.9286172521341705, 101.64366774108161],
    }, 

    'CLC': {
        'coords' : [2.9278483211464947, 101.64249536771976],
    },   
}

# Add building markers to the map
for building, data in buildings.items():
    popup_html = f"<h4>{building}</h4>"
    folium.Marker(
        location=data['coords'],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=building,
        icon=folium.Icon(color='blue', icon='university', prefix='fa')
    ).add_to(mmu_map)

# Save to HTML
mmu_map.save("mmu_interactive_map.html")
print("Map created and saved as 'mmu_interactive_map.html'")
