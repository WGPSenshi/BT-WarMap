<template>
  <div style="height:100%; width:100%">
    <!-- <div style="height:2%">
      <p> Center is at {{ mouseCoords }} </p>
    </div>-->
    <q-resize-observable @resize="onResize"/><l-map
    :center="center"
    :zoom="zoom"
    :minZoom="minZoom"
    :maxZoom="maxZoom"
    :maxBounds="bounds"
    :crs="crs"
    :options="mapOptions"
    style="height: 100%"
    ref="roguetech"
    preferCanvas: true
    >
    <!-- <l-tile-layer :url="url" :attribution="attribution" :bounds="bounds" noWrap="True"/> -->
    <l-image-overlay :url="`${publicPath}galaxy.png`" :bounds="bounds" :attribution="attribution"></l-image-overlay>
    <l-geo-json :geojson="geojson" :options="options" :options-style="styleFunction"></l-geo-json>
    <l-feature-group name="systemmarkers" ref="systemmarkers"></l-feature-group>
    </l-map>
  </div>
</template>

<script>
import {
  LMap,
  LTileLayer,
  LMarker,
  LImageOverlay,
  LGeoJson,
  LPopup,
  LTooltip,
  LFeatureGroup,
  LIcon,
  LCircleMarker,
  LCircle
} from "vue2-leaflet";
import oboe from "oboe";
import { circleMarker } from "leaflet";
import { SystemsSpecial } from "@/const.js";

export default {
  name: "Map",
  components: {
    LMap,
    LImageOverlay,
    LGeoJson,
    LFeatureGroup,
    LTileLayer
  },
  data() {
    return {
      zoom: -1,
      minZoom: -5,
      maxZoom: 3,
      center: L.latLng(4000, 9000),
      attribution:
        '&copy; <a href="https://forums.frontier.co.uk/showthread.php/220230-Images-of-the-entire-ED-galaxy">Corbin Moran </a>',
      currentZoom: 11.5,
      currentCenter: L.latLng(47.41322, -1.219482),
      showParagraph: false,
      mapOptions: {
        zoomSnap: 0.5
      },
      crs: L.CRS.Simple,
      bounds: [[0, 0], [18000, 18000]],
      mapBounds: [[0, 0], [18000, 18000]],
      map: null,
      // bgimg:"../assets/galaxy_small123.png"
      src: "@/assets/logo.png",
      publicPath: process.env.BASE_URL,
      geojson: null,
      fillColor: "#e4ce7f",
      icon: L.icon({
        iconUrl: "static/images/baseball-marker.png",
        iconSize: [32, 37],
        iconAnchor: [16, 37]
      }),
      systems: null,
      factions: null,
      systemMarkerRadius: 3,
      canvasRenderer: L.canvas({ padding: 0.5 }),
      mouseCoords: [0, 0],
      url: "/bg/{z}/{x}/{y}.png"
    };
  },
  methods: {
    zoomUpdate(zoom) {
      this.currentZoom = zoom;
    },
    centerUpdate(center) {
      this.currentCenter = center;
    },
    showLongText() {
      this.showParagraph = !this.showParagraph;
    },
    innerClick() {
      alert("Click!");
    },
    onResize(size) {
      if (this.$refs.roguetech != "undefined") {
        console.log("RESIZE");
        // this.$refs.roguetech.mapObject.invalidateSize();
      }
    },
    onMouseMove(e) {
      this.mouseCoords = [e.latlng.lat, e.latlng.lng];
    }
  },
  mounted() {
    this.$nextTick(() => {
      console.log("mounted");
    });
  },
  updated: function() {
    this.$nextTick(function() {
      // this.$refs.roguetech.mapObject.invalidateSize();
      // Code that will run only after the
      // entire view has been re-rendered
    });
  },
  computed: {
    options() {
      return {
        onEachFeature: this.onEachFeatureFunction
      };
    },
    styleFunction() {
      const fillColor = this.fillColor; // important! need touch fillColor in computed for re-calculate when change fillColor
      return () => {
        return {
          weight: 0,
          color: "#ECEFF1",
          opacity: 1,
          fillColor: fillColor,
          fillOpacity: 1
        };
      };
    },
    onEachFeatureFunction() {
      return (feature, layer) => {
        layer.bindTooltip(
          "<div>code:" +
            feature.properties.code +
            "</div><div>nom: " +
            feature.properties.nom +
            "</div>",
          { permanent: false, sticky: true }
        );
      };
    },
    addSystem(system) {
      return null;
    }
  },
  created() {
    this.loading = true;
    let systemsSrc = this.systems;
    let factionsSrc = this.factions;

    this.$nextTick(function() {
      var southWest = this.$refs.roguetech.mapObject.unproject([0, 18000], 0);
      var northEast = this.$refs.roguetech.mapObject.unproject([18000, 0], 0);
      northEast.lat = Math.abs(northEast.lat);
      console.log(southWest);
      console.log(northEast);
      var bounds = new L.LatLngBounds(southWest, northEast);
      console.log(bounds);

      // add the image overlay,
      // so that it covers the entire map
      L.tileLayer(this.url, {
        bounds: bounds,
        minZoom: 0,
        maxZoom: 7,
        tms: true
      }).addTo(this.$refs.roguetech.mapObject);

      this.$refs.roguetech.mapObject.on("mousemove", this.onMouseMove);
      let systemmarkers = this.$refs.systemmarkers.mapObject;
      let counter = 0;
      // Load base data
      Promise.all([fetch("/systems.json"), fetch("/factions.json")])
        .then(([systems, factions]) => {
          return Promise.all([systems.json(), factions.json()]);
        })
        .then(([systems, factions]) => {
          systemsSrc = systems;
          for (var key in factions) {
            let faction = factions[key];
            faction.colorRGB =
              "rgb(" +
              faction.color[0] * 255 +
              "," +
              faction.color[1] * 255 +
              "," +
              faction.color[2] * 255 +
              ")";
          }
          factionsSrc = factions;
        })
        .then(() => {
          // Stream markers :)
          oboe("http://roguetech.org:8000/warServices/StarMap/")
            .node("systems.*", system => {
              // This callback will be called everytime a new object is
              // found in the foods array.
              counter++;
              // if (counter > 5) this.abort();
              let systemSrcData = systemsSrc.find(obj => {
                return obj.name === system.name;
              });

              let tooltip = "<b>" + system.name + "</b><br>";
              let colorFill = "rgb(0,0,0)";
              let weight = 0;
              let color = "rgb(0,0,0)";
              let radius = 4;
              if (system.activePlayers > 0) {
                color = "#f00";
                weight = 1;
                system.companies.forEach(company => {
                  tooltip += company + "<br>";
                });
              }

              // Figure out if systems are special
              let special = SystemsSpecial.includes(system.name);
              // console.log(system);
              // if (special) console.log(system.name + " is special");
              if (special) radius = 8;

              let controllers = system.controlList.filter(
                x => x.percentage > 0
              );
              if (controllers.length > 1) {
                systemSrcData.contested = true;
                tooltip += "Contested<br>";
              }
              if (controllers.length == 0) {
                tooltip += "Abandoned<br>";
              }
              if (controllers.length > 0) {
                let owner = controllers.find(function(o) {
                  return (
                    o.percentage ==
                    Math.max.apply(
                      Math,
                      controllers.map(function(o) {
                        return o.percentage;
                      })
                    )
                  );
                });
                colorFill = factionsSrc[owner.faction].colorRGB;
              } else {
                colorFill = factionsSrc[1].colorRGB;
              }
              controllers.forEach(control => {
                systemSrcData.contested;
                tooltip +=
                  factionsSrc[control.faction].name +
                  " " +
                  control.percentage +
                  "%<br>";
              });
              L.circleMarker(
                [
                  systemSrcData.y * 0.7 + this.center.lat,
                  systemSrcData.x * 0.7 + this.center.lng
                ],
                {
                  radius: radius,
                  weight: weight,
                  fillColor: colorFill,
                  color: color,
                  fillOpacity: 0.5,
                  renderer: this.canvasRenderer
                }
              )
                .bindTooltip(tooltip)
                .addTo(systemmarkers);
              return oboe.drop;
            })
            .fail(reason => console.log(reason))
            .done(reason => {
              console.log(counter + " systems added");
            });
        })
        .catch(err => {
          console.log(err);
        });
    });
  }
};
</script>
