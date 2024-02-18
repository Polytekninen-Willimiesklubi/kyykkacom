<template>
  <span>
    <v-flex mt-10></v-flex>
    <v-app-bar style="z-index:2;" color="grey darken-3" dark>
      <router-link
        to="/"
        style="text-decoration: none; color:white; padding-right:2em; padding-left:1em;"
      >
        <img src="../../public/kyykkalogo120px.png">
      </router-link>

      <div v-for="item in items">
        <v-btn text class="hidden-md-and-down" :to=item.route 
              v-if="item.if_clause === undefined && item.title != 'Koti' || item.if_clause">
          {{ item.title }}
        </v-btn>
      </div>
      
      <v-spacer class="hidden-md-and-down"></v-spacer>
      <v-spacer class="hidden-md-and-down"></v-spacer>
      <v-select 
        v-on:input="selectSeason" 
        item-color=red 
        v-model="selectedSeason" 
        class="mt-4" align:center 
        item-text="name"
        :items="seasons">
      </v-select>
      <v-spacer class="hidden-md-and-down"></v-spacer>
      <v-spacer class="hidden-md-and-down"></v-spacer>

      <div class="hidden-md-and-down pa-4" v-if="!loggedIn">
        <log-in></log-in>
      </div>
      
      <div class="hidden-md-and-down" v-if="!loggedIn">
        <register></register>
      </div>

      <div class="hidden-md-and-down" v-if="loggedIn">
        <span class="mr-5">{{ name }}</span>
        <v-btn class="hidden-md-and-down" v-on:click.native="logout()" :to="'/'">Kirjaudu ulos</v-btn>
      </div>

      <v-spacer></v-spacer>
      <v-app-bar-nav-icon class="hidden-lg-and-up mr-4" @click.stop="drawer = !drawer"/>
    </v-app-bar>
      <v-navigation-drawer
      v-model="drawer"
      right
      absolute
      temporary
      dark
      >
        <v-list nav>
          <v-list-item-group
            active-class="text--accent-4"
          >

            <div v-for="item in items">
              <v-list-item :to=item.route v-if=item.if_clause>
                <v-list-item-icon>
                  <v-icon>{{ item.icon }}</v-icon>
                </v-list-item-icon>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
              </v-list-item>
            </div>

            <v-list-item>
              <div class="pa-2">
                <log-in v-if="!loggedIn"></log-in>
                <register v-if="!loggedIn"></register>
              </div>
              <v-btn style="position:absolute;" width="95%" v-if="loggedIn" v-on:click.native="logout()" :to="'/'">Log out</v-btn>
            </v-list-item>
          </v-list-item-group>
        </v-list>
        <template v-if="loggedIn" v-slot:prepend>
          <v-list-item two-line>
            <v-list-item-avatar>
              <img src="https://www.robertharding.com/watermark.php?type=preview&im=RF/RH_RF/VERTICAL/1112-5071">
            </v-list-item-avatar>

            <v-list-item-content>
              <v-list-item-title>{{ name }}</v-list-item-title>
              <v-list-item-subtitle>Logged In</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </template>
      </v-navigation-drawer>

  </span>
</template>


<script>
import LogIn from '@/components/LogIn';
import Register from '@/components/Register';
import { eventBus } from '../main';

export default {
    name: 'NavBar',
    components: {
        LogIn,
        Register
    },
    data() {
        return {
            drawer: false,
            loggedIn: false,
            name: '',
            team_id: '',
            selectedSeason: {},
            seasons: []
        };
    },
    computed: {
      items() {
        return [
                { title: 'Koti', route: '/', icon: 'mdi-home'},
                { title: 'Ottelut', route: '/ottelut', icon: 'mdi-space-invaders'},
                { title: 'Joukkueet', route: '/joukkueet', icon: 'mdi-emoticon-poop' },
                { title: 'Pelaajat', route: '/pelaajat', icon: 'mdi-account-group' },
                { title: 'Oma Joukkue', route: '/joukkue/' + this.team_id, if_clause: this.loggedIn && this.team_id != 'null' && this.team_id, icon: 'mdi-account' },
                { title: 'Jatkosarja', route: '/jatkosarja', icon: 'mdi-bank' },
                // { title: 'SuperWeekend', route: '/superweekend', icon: 'mdi-nuke' },
                { title: 'Info', route: '/info', icon: 'mdi-information-outline' },
              ]
      }
    },
    methods: {
        logout() {
            this.loggedIn = false;
            this.name = '';
            this.team_id = '';
            this.$session.destroy();
            localStorage.clear();
            this.$http.post('api/logout/', {}, {
              headers: {
                'X-CSRFToken': this.getCookie('csrftoken')
              },
              'withCredentials': true,
            })
        },
        selectSeason () {
          sessionStorage.season_id = this.selectedSeason;
          this.$router.push('/').catch(()=>{
            window.location.reload();
          });;
        },
        getSeasons() {
          this.$http.get('api/seasons').then(
            function(data) {
              var all_seasons = []
              data.body[0].forEach(ele => {
                all_seasons.push(ele)
              });
              this.selectedSeason = {
                'value' : data.body[1].value
              }
              all_seasons.sort((x,y) => {  // This makes the current year top most
                if (x.name < y.name) {return 1}
                else if  (x.name > y.name) {return -1}
                else {return 0}
              })
              sessionStorage.setItem('all_seasons', JSON.stringify(all_seasons))
              this.seasons = all_seasons
            }
          )
        }
    },
    created() {
        if (sessionStorage.season_id) {
          this.selectedSeason = sessionStorage.season_id;
        }
        if (!sessionStorage.all_seasons) {
          this.getSeasons()
        } else {
          this.seasons = JSON.parse(sessionStorage.all_seasons)
        }

        eventBus.$on('loginChanged', data => {
            this.loggedIn = true;
            this.name = data;

            if (localStorage.team_id != 'null' && localStorage.team_id) {
              this.team_id = localStorage.team_id
            }
            else {
                this.$http
                    .get(
                        'api/players/' +
                            localStorage.user_id +'/'
                    )
                    .then(function(response) {
                      if (response.body.team) {
                        this.team_id = response.body.team.id;
                        localStorage.team_id = this.team_id;
                      } else {
                        this.team_id = '';
                      }
                    });
            }
        });
    }
};
</script>
<style>
a {
  color: red;
  text-decoration: none;
  font-size: 130%;
}

.v-data-table-header th {
  white-space: nowrap;
}
</style>


<style scoped>
.v-app-bar--fixed {
    position: inherit;
}

.v-select {
  width: 7%;
}
</style>
