<template>
  <div style="height:100%; width:100%">
    <!-- <div style="height:2%">
      <p> Center is at {{ mouseCoords }} </p>
    </div> -->
    <q-resize-observable @resize="onResize"/><l-map
    :center="center"
    :zoom="zoom"
    :minZoom="minZoom"
    :maxZoom="maxZoom"
    :maxBounds="bounds"
    :crs="crsRT"
    :options="mapOptions"
    style="height: 100%"
    ref="roguetech"
    preferCanvas: true
    >
    <!-- <l-tile-layer :url="url" :attribution="attribution" :bounds="bounds" noWrap="True"/> -->
    <!-- <l-image-overlay :url="`${publicPath}galaxy.png`" :bounds="bounds" :attribution="attribution"></l-image-overlay> -->
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
      zoom: 5,
      minZoom: 3,
      maxZoom: 12,
      center: L.latLng(4000, 9000),
      // center: L.latLng(0, 0),
      attribution:
        '&copy; <a href="https://forums.frontier.co.uk/showthread.php/220230-Images-of-the-entire-ED-galaxy">Corbin Moran </a>',
      currentZoom: 11.5,
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
      url: "/bg/{z}/{x}/{y}.png",
      crsRT : L.extend({}, L.CRS.Simple, {
        projection: L.Projection.LonLat,
        // transformation: new L.Transformation(256/18000, 4000/18000, -256/18000, 9000/18000),
        transformation: new L.Transformation(140.5/18000, 0, -140.5/18000, 0),
        // Changing the transformation is the key part, everything else is the same.
        // By specifying a factor, you specify what distance in meters one pixel occupies (as it still is CRS.Simple in all other regards).
        // In this case, I have a tile layer with 256px pieces, so Leaflet thinks it's only 256 meters wide.
        // I know the map is supposed to be 2048x2048 meters, so I specify a factor of 0.125 to multiply in both directions.
        // In the actual project, I compute all that from the gdal2tiles tilemapresources.xml, 
        // which gives the necessary information about tilesizes, total bounds and units-per-pixel at different levels.
        infinite: true
      })
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
        this.$refs.roguetech.mapObject.invalidateSize();
      }
    },
    onMouseMove(e) {
      this.mouseCoords = [e.latlng.lat, e.latlng.lng, e.layerPoint.x, e.layerPoint.y, e.containerPoint.x, e.containerPoint.y];
    }
  },
  mounted() {
    this.$nextTick(() => {
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
    L.TileLayer.RT = L.TileLayer.extend({
        getTileUrl: function(coords) {
            // increment our x/y coords by 1 so they match our tile naming scheme
            coords.x = coords.x;
            coords.y = coords.y * -1 - 1;

            // pass the new coords on through the original getTileUrl
            // see http://leafletjs.com/examples/extending/extending-1-classes.html 
            // for calling parent methods
            return L.TileLayer.prototype.getTileUrl.call(this, coords);
        }
    });

    // static factory as recommended by http://leafletjs.com/reference-1.0.3.html#class
    L.tileLayer.RT = function(templateUrl, options) {
        return new L.TileLayer.RT(templateUrl, options);
    }

    this.$nextTick(function() {

      // add the image overlay,
      // so that it covers the entire map
      L.tileLayer.RT(this.url, {
        bounds: this.bounds,
        minNativeZoom: 0,
        maxNativeZoom: 7,
        tms: false,
        attribution: this.attribution
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
              console.log(counter + " systems loaded");
            });
        })
        .catch(err => {
          console.log(err);
        });
    });
  }
};
</script>
