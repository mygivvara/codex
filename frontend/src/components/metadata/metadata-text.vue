<template>
  <div v-if="displayValue" class="text" :class="{ highlight }">
    <div class="textLabel">
      {{ label }}
    </div>
    <div class="textValue" :class="{ empty }">
      <!-- eslint-disable-next-line sonarjs/no-vue-bypass-sanitization -->
      <a v-if="href" :href="href" :title="title" :target="target">
        {{ displayValue }}
        <v-icon v-if="link" size="small">
          {{ mdiOpenInNew }}
        </v-icon>
      </a>
      <div v-else class="textContent">
        {{ displayValue }}
      </div>
      <span v-if="baseName">{{ baseName }} </span>
    </div>
  </div>
</template>

<script>
import { mdiOpenInNew } from "@mdi/js";
import { mapState } from "pinia";

import { getBrowserHref } from "@/api/v3/browser";
import { GROUPS_REVERSED, useBrowserStore } from "@/stores/browser";
const EMPTY_VALUE = "(Empty)";

export default {
  name: "MetadataTextBox",
  props: {
    label: {
      type: String,
      required: true,
    },
    value: {
      type: [Object, String, Number, Boolean],
      default: undefined,
    },
    link: {
      type: [Boolean, String],
      default: false,
    },
    group: {
      type: String,
      default: "",
    },
    obj: {
      type: Object,
      default: undefined,
    },
  },
  data() {
    return {
      mdiOpenInNew,
    };
  },
  computed: {
    ...mapState(useBrowserStore, {
      browserShow: (state) => state.settings.show,
      browserTopGroup: (state) => state.settings.topGroup,
      folderViewEnabled: (state) => state.page.adminFlags.folderView,
    }),
    computedValue() {
      return this.value && this.value.name !== undefined
        ? this.value.name
        : this.value;
    },
    lastSlashIndex() {
      return this.computedValue.lastIndexOf("/") + 1;
    },
    displayValue() {
      let value;
      if (this.group && this.computedValue === "") {
        value = EMPTY_VALUE;
      } else if (this.group === "f" && this.computedValue) {
        value = this.computedValue.substring(0, this.lastSlashIndex);
      } else {
        value = this.computedValue;
      }
      return value;
    },
    empty() {
      return this.displayValue === EMPTY_VALUE;
    },
    _browserGroupHref() {
      // Using router-link gets hijacked and topGroup is not submitted.
      const group = this.group;
      const params = this.$router.currentRoute.value.params;

      // Validate Group
      if (
        !group ||
        params.group === group ||
        (group === "f" && !this.folderViewEnabled) ||
        (!["a", "f"].includes(group) && !this.browserShow[group])
      ) {
        return;
      }

      // Get & validate pks
      const pks = this.value.ids ? this.value.ids : [this.value.pk];
      if (!pks || !pks.length) {
        return;
      }
      const topGroup = this.getTopGroup(group);
      const query = { topGroup };
      return getBrowserHref({ group, pks, query });
    },
    _linkHref() {
      if (this.link === true) {
        return this.displayValue;
      } else if (this.link) {
        return this.link;
      }
      return false;
    },
    href() {
      return this._browserGroupHref ? this._browserGroupHref : this._linkHref;
    },
    target() {
      return this.link ? "_blank" : "";
    },
    title() {
      return this._browserGroupHref ? `Browse to ${this.label}` : this.label;
    },
    baseName() {
      return this.group === "f"
        ? this.computedValue.substring(this.lastSlashIndex)
        : "";
    },
    highlight() {
      return this.obj?.group === this.group;
    },
  },
  methods: {
    getTopGroup(group) {
      // Very similar to browser store logic, could possibly combine.
      let topGroup;
      if (this.browserTopGroup === group || ["a", "f"].includes(group)) {
        topGroup = group;
      } else {
        const groupIndex = GROUPS_REVERSED.indexOf(group); // + 1;
        // Determine browse top group
        for (const testGroup of GROUPS_REVERSED.slice(groupIndex)) {
          if (testGroup !== "r" && this.browserShow[testGroup]) {
            topGroup = testGroup;
            break;
          }
        }
      }
      return topGroup;
    },
  },
};
</script>

<style scoped lang="scss">
@import "../anchors.scss";

.text {
  display: flex;
  flex-direction: column;
  padding: 10px;
  border-radius: 3px;
  max-width: 100%;
  background-color: rgb(var(--v-theme-surface));
}

.textLabel {
  font-size: 12px;
  color: rgb(var(--v-theme-textSecondary));
}

.textContent {
  border: solid thin transparent;
}

.highlight .textContent {
  background-color: rgb(var(--v-theme-primary-darken-1));
  padding: 0px 8px 0px 8px;
  border-radius: 12px;
}

// eslint-disable-next-line vue-scoped-css/no-unused-selector
.highlight a.textContent {
  color: rgb(var(--v-theme-textPrimary)) !important;
  background-color: rgb(var(--v-theme-primary-darken-1));
}

// eslint-disable-next-line vue-scoped-css/no-unused-selector
.highlight a.textContent:hover {
  border: solid thin rgb(var(--v-theme-textPrimary));
}

.empty {
  opacity: 0.5;
}
</style>
