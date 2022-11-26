import streamlit as st
import streamlit.components.v1 as components
import json
import tqdm.auto as tqdm
import ecoscope

st.title("Speed Maps")

ecoscope.init(selenium=True, force=True)

EARTHRANGER_SERVER= st.sidebar.text_input("Server")
EARTHRANGER_USERNAME = st.sidebar.text_input("Username")
EARTHRANGER_PASSWORD = st.sidebar.text_input("Password", type="password")

earthranger_io= ecoscope.io.EarthRangerIO(
    server=EARTHRANGER_SERVER,
    username=EARTHRANGER_USERNAME,
    password=EARTHRANGER_PASSWORD,
    tcp_limit=5,
    sub_page_size=4000
)
event_type_map = {entry["value"]: entry["id"] for entry in earthranger_io.get_event_types()}

# Define basemap
landDx_basemap = "https://tiles.arcgis.com/tiles/POUcpLYXNckpLjnY/arcgis/rest/services/landDx_basemap_tiles_mapservice/MapServer/tile/{z}/{y}/{x}"
default_basemap = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"

# Define the time period for running analyses

since = st.sidebar.date_input("Select start date").isoformat()
until = st.sidebar.date_input("Select end date").isoformat()

st.write("Analysis Period:", since, "to", until)

# ER subjectgroup profiles
subjectgroup_profiles = {
 "MEP_Elephants_Marmanet": {
     "map_title": 'Elephants Marmanet Speed Map',
     "track": {
         "type": "speed_tracks",
         "basemap": landDx_basemap,
     }
 },

 "acjc_report": {
    "map_title": 'Audrey, Clara, Indy Speed Map',
    "track": {
        "type": "speed_tracks",
        "basemap": landDx_basemap,
    }
 },

 "MEP_Elephants_Shimba_Hills": {
     "map_title": 'Elephants Shimba Hills Speed Map',
     "track": {
         "type": "speed_tracks",
         "basemap": landDx_basemap,
     }
 },
    
 "Glasgow_Wildebeest": {
     "map_title": 'Wildebeest Speed Map',
     "max_traj_seg_timespan": 24. * 60 * 60,
     "max_traj_seg_speed": 15.,
     "track": {
         "type": "speed_tracks",
         "basemap": default_basemap,
         "props": {
             "no_class": 6,
             "classification_method": "equal_interval",
             "linewidth": 1
         }
   },
 },

 "MEP_Elephants_Serengeti_Mara_Nyakweri_Loita_Rift": {
     "map_title": 'GME Elephant Speed Map',
     "max_traj_seg_timespan": 4. * 60 * 60,
     "max_traj_seg_speed": 8.,
     "legend_location": "best",
     "extent_ratio": 1.1,  # 👈🏾 update extent ratio here .
     "track": {
         "type": "speed_tracks",
         "basemap": landDx_basemap,
         "props": {
             "no_class": 6,
             "classification_method": "equal_interval",
             "linewidth": 1,
             'speed_colors': ['#38a800', '#8bd100', '#ffff00', '#ff8000', '#ff0000'],
             'bins': [0, 0.7, 1.5, 2.3, 3, 8]
         }
     },
     "events": [
         {
             "event_type": "mep_movement_label",
             "props": {
                 "marker": "o",
                 "markersize": 100,
                 "color": "brown",
                 "alpha": 0.7,
                 "label": "Movement-Label"
             }
         }
     ]
 },
 "MEP_Elephants_Tsavo": {
    "map_title": 'Tsavo Elephants Speed Map',
    "max_traj_seg_timespan": 4. * 60 * 60,
    "max_traj_seg_speed": 8.,
    "legend_location": "best",
    "track": {
       "type": "speed_tracks",
        "basemap": landDx_basemap,
        "props": {
          "no_class": 6,
          "classification_method": "equal_interval",
          "linewidth": 2,
          "speed_colors": ['#38a800', '#8bd100', '#ffff00', '#ff8000', '#ff0000'],
          "bins": [0, 0.7, 1.5, 2.3, 3, 8]
      }
  },
  "events": [
       {
           "event_type": "mep_movement_label",
           "props": {
           "marker": "o",
              "markersize": 100,
              "color": "brown",
              "alpha": 0.7,
              "label": "Movement-Label"
          }
       }
      ]
   },

 "MEP_Elephants_Mau": {
     "map_title": 'Mau Elephants Speed Map',
     "max_traj_seg_timespan": 4. * 60 * 60,
     "max_traj_seg_speed": 8.,
     "legend_location": "best",
     "track": {
         "type": "speed_tracks",
         "basemap": landDx_basemap,
         "props": {
             "no_class": 6,
             "classification_method": "equal_interval",
             "linewidth": 2,
             "speed_colors": ['#38a800', '#8bd100', '#ffff00', '#ff8000', '#ff0000'],
             "bins": [0, 0.7, 1.5, 2.3, 3, 8]
         }
     },
     "events": [
             {
                 "event_type": "mep_movement_label",
                 "props": {
                     "marker": "o",
                     "markersize": 100,
                     "color": "brown",
                     "alpha": 0.7,
                     "label": "Movement-Label"
                 }
             }
         ]
 },

 "MEP_Helicopters": {
   "map_title": 'Helicopter Flight Paths',
   "max_traj_seg_timespan": 0.5 * 60 * 60,
   "max_traj_seg_speed": 250.,
   "legend_location": "upper right",
   "track": {
      "type": "monochrome_tracks",
      "basemap": landDx_basemap,
      "props": {
          "linewidth": 2,
          "marker": 0,
          "color": "k",
          "label": "Helicopter Tracks"
      }
  }
 },

 "MEP_Ranger_Teams": {
         "map_title": 'Ranger Team Foot Patrols',
         "max_traj_seg_timespan": 601,
         "max_traj_seg_speed": 5.5,
         "legend_location": "center right",
         "extent_ratio": 1.1,
         "track": {
             "type": "monochrome_tracks",
             "basemap": landDx_basemap,
             "props": {
                 "linewidth": 2,
                 "marker": 0,
                 "color": "#bf00ff",
                 "label": "Tracks"
             }
         },
         "events": [
           {
                 "event_type": "mep_illegal_wildlife_trap",
                 "props": {
                     "marker": "^",
                     "markersize": 120,
                     "color": "orange",
                     "alpha": 1,
                     "label": "MEP-Wildlife-Trap"
                 }
             },
             {
                 "event_type": "mep_hwc_mitigation_event",
                 "props": {
                     "marker": "*",
                     "markersize": 110,
                     "color": "#a83800",
                     "alpha": 1,
                     "label": "MEP-HWC"
                 }
             },
             {
                 "event_type": "mep_illegal_charcoal",
                 "props": {
                     "marker": "o",
                     "markersize": 100,
                     "color": "#00ff00",
                     "edgecolors": "black",
                     "alpha": 0.7,
                     "label": "MEP-Illegal-Charcoal"
                 }
             },
           {
                 "event_type": "mep_illegal_logging",
                 "props": {
                     "marker": "o",
                     "markersize": 90,
                     "color": "white",
                     "edgecolors": "black",
                     "alpha": 0.7,
                     "label": "MEP-Illegal-Logging"
                 }
             },
             {
                 "event_type": "mep_arrest",
                 "props": {
                     "marker": "+",
                     "markersize": 80,
                     "color": "black",
                     "alpha": 1,
                     "label": "MEP-Arrest"
                 }
             },
             {
                 "event_type": "mep_mike",
                 "props": {
                     "marker": "^",
                     "markersize": 70,
                     "color": "red",
                     "alpha": 1,
                     "label": "MEP-MIKE"
                 }
             },
         ]
     },

       "MEP_Rangers_Marmanet": {
         "map_title": 'Ranger Team Foot Patrols',
         "max_traj_seg_timespan": 600,
         "max_traj_seg_speed": 5.5,
         "legend_location": "center right",
         "extent_ratio": 1.1,
         "track": {
             "type": "monochrome_tracks",
             "basemap": landDx_basemap,
             "props": {
                 "linewidth": 2,
                 "marker": 0,
                 "color": "#bf00ff",
                 "label": "Tracks"
             }
         },
         "events": [
           {
                 "event_type": "mep_illegal_wildlife_trap",
                 "props": {
                     "marker": "^",
                     "markersize": 120,
                     "color": "orange",
                     "alpha": 1,
                     "label": "MEP-Wildlife-Trap"
                 }
             },
             {
                 "event_type": "mep_hwc_mitigation_event",
                 "props": {
                     "marker": "*",
                     "markersize": 110,
                     "color": "#a83800",
                     "alpha": 1,
                     "label": "MEP-HWC"
                 }
             },
             {
                 "event_type": "mep_illegal_charcoal",
                 "props": {
                     "marker": "o",
                     "markersize": 100,
                     "color": "#00ff00",
                     "edgecolors": "black",
                     "alpha": 0.7,
                     "label": "MEP-Illegal-Charcoal"
                 }
             },
           {
                 "event_type": "mep_illegal_logging",
                 "props": {
                     "marker": "o",
                     "markersize": 90,
                     "color": "white",
                     "edgecolors": "black",
                     "alpha": 0.7,
                     "label": "MEP-Illegal-Logging"
                 }
             },
             {
                 "event_type": "mep_arrest",
                 "props": {
                     "marker": "+",
                     "markersize": 80,
                     "color": "black",
                     "alpha": 1,
                     "label": "MEP-Arrest"
                 }
             },
             {
                 "event_type": "mep_mike",
                 "props": {
                     "marker": "^",
                     "markersize": 70,
                     "color": "red",
                     "alpha": 1,
                     "label": "MEP-MIKE"
                 }
             },
         ]
     },

     "MEP_Rangers_Shimba_Hills": {
         "map_title": "Shimba Hill Ranger Team Foot Patrols",
         "max_traj_seg_timespan": 600,
         "max_traj_seg_speed": 5.5,
         "legend_location": "upper right",
         "track": {
             "type": "monochrome_tracks",
             "basemap": landDx_basemap,
             "props": {"linewidth": 2, "marker": 0, "color": "#bf00ff", "label": "Tracks"},
         },
         "events": [
             {
                 "event_type": "mep_illegal_wildlife_trap",
                 "props": {
                     "marker": "^",
                     "markersize": 120,
                     "color": "orange",
                     "alpha": 1,
                     "label": "MEP-Wildlife-Trap",
                 },
             },
             {
                 "event_type": "mep_hwc_mitigation_event",
                 "props": {
                     "marker": "*",
                     "markersize": 120,
                     "color": "#a83800",
                     "alpha": 1,
                     "label": "MEP-HWC",
                 },
             },
             {
                 "event_type": "mep_illegal_charcoal",
                 "props": {
                     "marker": "o",
                     "markersize": 120,
                     "color": "#00ff00",
                     "edgecolors": "black",
                     "alpha": 0.7,
                     "label": "MEP-Illegal-Charcoal",
                 },
             },
             {
                 "event_type": "mep_illegal_logging",
                 "props": {
                     "marker": "o",
                     "markersize": 120,
                     "color": "white",
                     "edgecolors": "black",
                     "alpha": 0.7,
                     "label": "MEP-Illegal-Logging",
                 },
             },
             {
                 "event_type": "mep_arrest",
                 "props": {
                     "marker": "+",
                     "markersize": 120,
                     "color": "black",
                     "alpha": 1,
                     "label": "MEP-Arrest",
                 },
             },
         ],
    },
    

 "MEP_Vehicles": {
     "map_title": 'Vehicle Patrols',
     "max_traj_seg_timespan": 5 * 60.,
     "max_traj_seg_speed": 130.,
     "legend_location": "upper right",
     "track": {
         "type": "monochrome_tracks",
         "basemap": landDx_basemap,
         "props": {
             "linewidth": 2,
             "marker": 0,
             "color": "#e64d00",
             "label": "Tracks"
         }
     },
     "label": "Tracks"
 },

 "MEP_Research_Field_Assistants": {
     "map_title": 'Research Field Teams',
     "max_traj_seg_timespan": 60.,
     "max_traj_seg_speed": 80.,
     "legend_location": "upper right",
     "track": {
         "type": "monochrome_tracks",
         "basemap": landDx_basemap,
         "props": {
             "linewidth": 2,
             "marker": 0,
             "color": "#fc9403"
         }
     }
 }
}   
     
sbp = [
       "MEP_Elephants_Marmanet",
       "acjc_report",
       "MEP_Elephants_Shimba_Hills",
       "Glasgow_Wildebeest",
       "MEP_Elephants_Serengeti_Mara_Nyakweri_Loita_Rift",
       "MEP_Elephants_Tsavo",
       "MEP_Elephants_Mau",
       "MEP_Helicopters",
       "MEP_Ranger_Teams",
       "MEP_Rangers_Marmanet",
       "MEP_Rangers_Shimba_Hills",
       "MEP_Vehicles",
       "MEP_Research_Field_Assistants"
      ]


get_all = st.sidebar.checkbox("Select all")

#get_none = st.sidebar.radio("Select none")
 
if get_all:
    selection = st.sidebar.multiselect("Select one or more options:",
         sbp, sbp)
#elif get_none:
#    selection = st.sidebar.multiselect("Clear selection:", [])
else:
    selection = st.sidebar.multiselect("Select one or more options:",
        sbp)

subset_cols = ['groupby_col', 'fixtime', 'junk_status', 'extra__source', 'geometry', 'extra__subject__name','extra__subject__region',
       'extra__subject__country', 'extra__subject__sex',]

if st.button("Click to process maps"):
    to_process = {}
    if len(selection) > 0:
        for i in selection:
            if i in subjectgroup_profiles.keys():
                to_process[i] = subjectgroup_profiles[i]
                
        pbar = tqdm.tqdm(list(to_process.items()))
        for group_name, vals in pbar:
            pbar.set_description(f"Downloading observations: {group_name}")
        
        #    data_dir = os.path.join(output_dir, group_name)
        #    os.makedirs(data_dir, exist_ok=True)
        
            # Relocations
            relocations_gdf = earthranger_io.get_subjectgroup_observations(
                group_name=group_name,
                include_subject_details=True,
                since=since,
                until=until,
            )
        
            relocations_gdf.apply_reloc_filter(
                ecoscope.base.RelocsCoordinateFilter(filter_point_coords=[[180, 90], [0, 0]]),
                inplace=True,
            )
            relocations_gdf.query("~junk_status", inplace=True)
        
            if 'extra__device_status_properties' in relocations_gdf:
                del relocations_gdf['extra__device_status_properties'] # Necessary for GPKG
        
            # subset columns
            relocations_gdf = relocations_gdf[subset_cols]
        
            # rename columns
            relocations_gdf.columns = [i.replace('extra__', '') for i in relocations_gdf.columns]
            relocations_gdf.columns = [i.replace('subject__', '') for i in relocations_gdf.columns]
        
        #    relocations_gdf.to_file(
        #        os.path.join(data_dir, group_name + ".gpkg"), layer="relocations", driver="GPKG"
        #    )
        
            # Trajectory
            trajectory_gdf = ecoscope.base.Trajectory.from_relocations(relocations_gdf)
            trajectory_gdf.apply_traj_filter(
                ecoscope.base.TrajSegFilter(
                    min_length_meters=0.0,
                    max_length_meters=float("inf"),
                    min_time_secs=0.0,
                    max_time_secs=vals.get("max_traj_seg_timespan"),
                    min_speed_kmhr=0.0,
                    max_speed_kmhr=vals.get("max_traj_seg_speed"),
                ),
                inplace=True,
            )
            trajectory_gdf.query("~junk_status", inplace=True)
        
        #    trajectory_gdf.to_file(
        #        os.path.join(data_dir, group_name + ".gpkg"),
        #        layer="trajectories",
        #        driver="GPKG",
        #    )
        
            print(f"{group_name}: {trajectory_gdf.dist_meters.sum()}m")
        
            # Plotting
            props = vals.get("track", {}).get("props", {})
            m = ecoscope.mapping.EcoMap(
                tiles="",
                static=True,
                height=15 * 50,
                width=20 * 50,
                search_control=False,
            )
            m.add_title(title=vals.get("map_title", group_name), font_size="24px")
        
            m.add_basemap("SATELLITE")
            m.add_tile_layer(
                url=vals.get("track", {}).get("basemap"),
                name="LandDx",
                attribution="MEP",
                opacity=0.8,
            )
            m.add_north_arrow(position="topleft", scale=0.6)
        
            if vals.get("track", {}).get("type") == "monochrome_tracks":
                m.add_gdf(
                    trajectory_gdf.geometry,
                    color=props.get("color"),
                )
            else:
                m.add_speedmap(
                    trajectory=trajectory_gdf,
                    classification_method=props.get("classification_method", "equal_interval"),
                    num_classes=props.get("no_class", 6),
                    bins=props.get("bins"),
                    speed_colors=props.get("speed_colors"),
                )
            
            m.zoom_to_gdf(trajectory_gdf)
        
            XMIN, YMIN, XMAX, YMAX = trajectory_gdf.total_bounds
        
            W = XMAX - XMIN
            H = YMAX - YMIN
            XMAX += W
            XMIN -= W
            YMAX += H
            YMIN -= H
        
            # Events
            colors = []
            labels = []
            for event in vals.get("events", []):
                pbar.set_description(f"Downloading {event['event_type']}: {group_name}")
                try:
                    events_gdf = earthranger_io.get_events(
                        event_type=event_type_map[event["event_type"]],
                        filter=json.dumps({"date_range": {"lower": since, "upper": until}}),
                        bbox=f"{XMIN},{YMIN},{XMAX},{YMAX}",
                    )
                except AssertionError:
                    continue
        
                color = event.get("props", {}).get("color")
                colors.append(color)
                labels.append(event.get("props", {}).get("label"))
                m.add_gdf(
                    events_gdf,
                    color=color,
                    marker_type="circle_marker",
                    marker_kwds={"radius": event.get("props", {}).get("markersize") / 40},
                    style_kwds={"opacity": event.get("props", {}).get("alpha")}
                )
        
            if colors:
                import branca
        
                legend = branca.element.MacroElement()
                legend._template = branca.element.Template(
                    """
                {% macro header(this, kwargs) %}
                    <style type='text/css'>
                    .maplegend .legend-title {
                        text-align: left;
                        margin-bottom: 5px;
                        font-weight: bold;
                        font-size: 90%;
                        }
                    .maplegend .legend-scale ul {
                        margin: 0;
                        margin-bottom: 5px;
                        padding: 0;
                        float: left;
                        list-style: none;
                        }
                    .maplegend .legend-scale ul li {
                        font-size: 80%;
                        list-style: none;
                        margin-left: 0;
                        line-height: 18px;
                        margin-bottom: 2px;
                        }
                    .maplegend ul.legend-labels li span {
                        display: block;
                        float: left;
                        height: 16px;
                        width: 30px;
                        margin-right: 5px;
                        margin-left: 0;
                        border: 1px solid #999;
                        }
                    .maplegend .legend-source {
                        font-size: 80%;
                        color: #777;
                        clear: both;
                        }
                    .maplegend a {
                        color: #777;
                        }
                    </style>
                {% endmacro %}
                {% macro html(this, kwargs) %}
                <div id='maplegend' class='maplegend'
                    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
                    border-radius:6px; padding: 10px; font-size:14px; left: 20px; bottom: 50px;'>
        
                <div class='legend-title'>Events</div>
                <div class='legend-scale'>
                <ul class='legend-labels'>
                """
                    + "".join(
                        [
                            f"<li><span style='background:{color};opacity:0.7;'></span>{label}</li>"
                            for color, label in zip(colors, labels)
                        ]
                    )
                    + """
                </ul>
                </div>
                </div>
                {% endmacro %}
                """
                )
                m.add_child(legend)
            
    #        m.to_png("selection.png")
            m.save("m.html")
            p = open("m.html")
            components.html(p.read(), width=600, height=600)
     
     #   pbar.set_description(f"Saving image: {group_name}")
     #   m.to_png(os.path.join(data_dir, group_name + "_tracks.png"))
     #   pbar.set_description(f"Finished: {group_name}"
