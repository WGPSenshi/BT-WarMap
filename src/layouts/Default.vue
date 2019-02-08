<template>
  <q-layout view="lHh Lpr lFf">
    <q-layout-header>
      <q-toolbar color="primary" :glossy="$q.theme === 'mat'" :inverted="$q.theme === 'ios'">
        <q-btn
          flat
          dense
          round
          @click="leftDrawerOpen = !leftDrawerOpen"
          aria-label="Menu"
          icon="menu"
        />

        <q-toolbar-title>Roguetech Persistent War Map
          <div slot="subtitle">Overhaul Alpha {{ version }}</div>
        </q-toolbar-title>
      </q-toolbar>
    </q-layout-header>

    <q-layout-drawer
      v-model="leftDrawerOpen"
      :content-class="$q.theme === 'mat' ? 'bg-grey-2' : null"
      :content-style="{color: 'white'}"
      :width="200"
    >
      <q-list no-border link inset-delimiter>
        <q-list no-border link inset-delimiter>
          <!-- <q-list-header>Navigation</q-list-header>
          <q-item to="/" exact>
            <q-item-side icon="satellite"/>
            <q-item-main label="Map"/>
          </q-item>
          <q-item-separator/>-->
          <q-list-header :style="{color: 'white'}">Essential Links</q-list-header>
          <q-item @click.native="openURL('https://www.nexusmods.com/battletech/mods/79')">
            <q-item-side icon="cloud_download"/>
            <q-item-main label="Nexus"></q-item-main>
          </q-item>
          <q-item @click.native="openURL('https://discord.gg/RKFXP9G')">
            <q-item-side icon="chat"/>
            <q-item-main label="Discord"></q-item-main>
          </q-item>
          <q-item @click.native="openURL('https://roguetech.gamepedia.com/')">
            <q-item-side icon="library_books"/>
            <q-item-main label="Wiki"></q-item-main>
          </q-item>
          <q-item
            @click.native="openURL('https://www.nexusmods.com/Core/Libs/Common/Widgets/PayPalPopUp?user=6191338')"
          >
            <q-item-side icon="attach_money"/>
            <q-item-main label="Donate"></q-item-main>
          </q-item>
        </q-list>
      </q-list>
    </q-layout-drawer>

    <q-page-container>
      <router-view/>
    </q-page-container>
  </q-layout>
</template>

<script>
import { openURL } from "quasar";

export default {
  name: "LayoutDefault",
  data() {
    return {
      leftDrawerOpen: this.$q.platform.is.desktop,
      version: "2019-02-09 Build 1"
    };
  },
  methods: {
    openURL
  }
};
</script>

<style></style>
