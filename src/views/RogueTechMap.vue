<template>
  <q-page class="flex flex-center">
    <Map style="position:absolute"></Map>
  </q-page>
</template>

<script lang="ts">
import Map from "@/components/Map.vue"; // @ is an alias to /src

export default {
  name: "RogueTechMap",
  components: {
    Map
  }
};
</script>
