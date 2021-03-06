<template>
  <b-container class="basic-config">
    <!--  FILES  -->
    <b-row
      v-for="file in files"
      :key="file.type"
      class="basic-config-row path-row"
    >
      <b-input-group>
        <b-input-group-prepend class="path-prepend">
          <b-button
            class="path-browse"
            @click="file.browse"
            data-toggle="tooltip"
            :title="`Browse for a ${file.type} file...`"
            :disabled="staticPaths"
          >
            <i :class="file.icon" />
          </b-button>
          <b-dropdown
            class="path-select"
            data-toggle="tooltip"
            :title="`Recent ${file.type} files`"
            :disabled="staticPaths"
          >
            <b-dropdown-item
              v-for="path in path_options[file.model]"
              :key="`path-${path}`"
              @click="file.select(path)"
            >
              {{ path }}
            </b-dropdown-item>
          </b-dropdown>
        </b-input-group-prepend>
        <b-form-input
          :class="{
            // don't set if null
            'is-valid': file.valid === true,
            'is-invalid': file.valid === false,
          }"
          :readonly="staticPaths"
          @change="file.check"
          :ref="file.model"
          type="text"
          v-model="config[file.model]"
          :placeholder="`${file.type} file path`"
        />
      </b-input-group>
    </b-row>

    <!--    FRAMES   -->
    <b-row class="basic-config-row">
      <b-col class="leftmost-col">
        <b-input-group-text class="leftmost-label">
          <b>frames</b>
        </b-input-group-text>
      </b-col>
      <b-col class="frame-col">
        <b-row class="basic-config-row">
          <b-input-group>
            <b-form-select
              class="fis-selector isimple-form-field-auto"
              ref="frame_interval_setting"
              v-model="config.frame_interval_setting"
              @change="selectFrameIntervalSetting"
              :plain="false"
              :options="frame_interval_settings.options"
            />
            <b-input-group-text class="basic-config-label isimple-form-label">
              {{
                frame_interval_settings.descriptions[
                  config.frame_interval_setting
                ]
              }}
            </b-input-group-text>
            <b-form-input
              class="fis-value isimple-form-field-auto"
              ref="interval"
              type="number"
              v-model="config[config.frame_interval_setting]"
              :placeholder="config.frame_interval_setting"
              @change="onChange"
            />
          </b-input-group>
        </b-row>
      </b-col>
    </b-row>

    <!--    FEATURES   -->
    <b-row
      v-for="(feature, index) in config.features"
      :key="index"
      class="basic-config-row"
    >
      <b-col class="leftmost-col" :key="index">
        <b-input-group-text v-if="index === 0" class="leftmost-label">
          <b>features</b>
        </b-input-group-text>
      </b-col>
      <b-col class="feature-col">
        <b-row class="basic-config-row">
          <b-form-select
            class="feature-selector isimple-form-field-auto"
            v-model="config.features[index]"
            :options="features.options"
            @input="(v) => selectFeature(index, v)"
            :plain="false"
          />
        </b-row>
      </b-col>
      <b-col class="parameter-col">
        <b-row class="basic-config-row">
          <!--          <b-input-group-->
          <!--            v-for="(value, parameter) in config.feature_parameters[feature]"-->
          <!--            :key="parameter"-->
          <!--            class="parameter-group"-->
          <!--          >-->
          <!--            <b-input-group-text class="basic-config-label">-->
          <!--              {{ features.parameters[feature][parameter].description }}-->
          <!--            </b-input-group-text>-->
          <!--            &lt;!&ndash;          todo: connect to schema !!&ndash;&gt;-->
          <!--            <b-form-input-->
          <!--              class="parameter-field"-->
          <!--              ref="interval"-->
          <!--              type="text"-->
          <!--              v-model="config.feature_parameters[feature][parameter]"-->
          <!--            />-->
          <!--          </b-input-group>-->
          <b-input-group
            v-for="(value, parameter) in config.feature_parameters[index]"
            :key="parameter"
            class="parameter-group"
          >
            <b-input-group-text class="basic-config-label isimple-form-label">
              {{ features.parameters[feature][parameter].description }}
            </b-input-group-text>
            <SchemaField
              :class_="'parameter-field'"
              :type="features.parameters[feature][parameter].type"
              :value="config.feature_parameters[index][parameter]"
              :options="features.parameters[feature][parameter]"
              @input="(v) => setParameter(index, parameter, v)"
              @commit="onChange"
              :new_row="false"
              :style_="{
                'max-width': ['number', 'integer', 'float'].includes(
                  features.parameters[feature][parameter].type
                )
                  ? '60px'
                  : undefined,
              }"
            />
          </b-input-group>
        </b-row>
      </b-col>
      <b-col class="remove-col">
        <b-button
          v-if="config.features.length > 1"
          class="remove-button"
          @click="handleRemoveFeature(index)"
          data-toggle="tooltip"
          :title="`Remove feature '${feature}'`"
        >
          <i class="fa fa-close" />
        </b-button>
      </b-col>
    </b-row>

    <!--    ADD FEATURE-->
    <b-row class="basic-config-row">
      <b-col class="leftmost-col"> </b-col>
      <b-col class="add-feature-col">
        <b-row class="basic-config-row">
          <b-button
            class="add-button"
            @click="handleAddFeature()"
            v-bind:class="{
              'is-valid': hasFeatures === true,
              'is-invalid': hasFeatures === false,
            }"
          >
            <i class="fa fa-plus" /> &nbsp; Add feature...
          </b-button>
        </b-row>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import {
  select_design_path,
  select_video_path,
  check_design_path,
  check_video_path,
  resolve_paths,
  get_recent_paths,
} from "../../static/api";

import AsyncComputed from "vue-async-computed";
import Vue from "vue";
import SchemaField from "@/components/config/SchemaField";

import has from "lodash/has";
import cloneDeep from "lodash/cloneDeep";
import { COMMIT, ENTER_FOCUSOUT_INTERVAL } from "static/events";

Vue.use(AsyncComputed);

export default {
  name: "BasicConfig",
  components: {
    SchemaField,
  },
  props: {
    staticPaths: {
      type: Boolean,
      default: false,
    },
    config: {
      type: Object,
      default: () => {
        return {
          video_path: "",
          design_path: "",
          frame_interval_setting: "Nf",
          Nf: 100,
          dt: 5,
          features: [],
          feature_parameters: [], // todo: these don't actually get sent to the backend
        };
      },
    },
  },
  mounted() {
    this.$store.dispatch("schemas/sync");
    if ("features" in this.config && this.config.features.length === 0) {
      this.handleAddFeature();
    }
  },
  methods: {
    onChange(v) {
      // console.log(this.config);
      this.$emit(COMMIT);
    },
    onKeyUp(e) {
      console.log(e);
      if (this.type_commit && e.key === "Enter") {
        this.lastEnter = Date.now();
        if (this.valueOut !== this.value) {
          console.log("SchemaField.onKeyUp() 'Enter' -> commit");
          this.$emit(COMMIT);
        }
      }
    },
    onFocusOut(e) {
      console.log(e);
      if (
        this.type_commit &&
        Math.abs(Date.now() - this.lastEnter) > ENTER_FOCUSOUT_INTERVAL
      ) {
        if (this.valueOut !== this.value) {
          console.log("SchemaField.onFocusOut() -> commit");
          this.$emit(COMMIT);
        }
      }
    },
    setParameter(index, parameter, value) {
      // console.log(
      //   `BasicConfig.setParameter() feature=${feature} parameter=${parameter}, value=${value}`
      // );
      this.config.feature_parameters[index][parameter] = value;
    },
    getConfig() {
      // console.log("BasicConfig.getconfig() -- this.config=");
      // console.log(this.config);

      let config = Object.assign(this.config, {
        [`${this.config.frame_interval_setting}`]: Number(
          this.config[`${this.config.frame_interval_setting}`] // todo: is this really necessary? maybe just gather both.
          //todo: also: see this text -> number conversion, that's why parameters can't be set!
        ),
      });

      // console.log(config);

      return config;
    },
    selectFrameIntervalSetting(setting) {
      // console.log("selecting frame_interval_setting");
      // console.log(setting);
      if (setting in this.frame_interval_settings) {
        this.config.frame_interval_setting = setting;
      }
      this.onChange();
    },
    handleRemoveFeature(index) {
      this.config.features.splice(index, 1);
      this.onChange();
    },
    handleAddFeature() {
      const feature = this.features.options[0];

      if (this.config.features === undefined) {
        this.config.features = [];
      }
      if (this.config.feature_parameters === undefined) {
        this.config.feature_parameters = [];
      }

      this.config.features = cloneDeep([...this.config.features, feature]);

      try {
        this.config.feature_parameters = [
          ...this.config.feature_parameters,
          cloneDeep(this.features.defaults[feature]),
        ];
      } catch (e) {
        console.warn(e);
        this.config.feature_parameters = [];
      }
      this.onChange();
    },
    selectFeature(index, feature) {
      // console.log(`selectFeature(${index}) -> feature = ${feature}`);

      if (this.features.options.includes(feature)) {
        // console.log(this.features);

        this.config.feature_parameters[index] = cloneDeep(
          this.features.defaults[feature]
        );
      }
      this.onChange();
    },
    selectVideoFile() {
      select_video_path().then((path) => {
        if (path) {
          this.config.video_path = path;
          this.checkVideoPath();
        }
      });
    },
    selectVideoFileFromDropdown(path) {
      // console.log(`selectVideoFileFromDropdown: ${path}`);
      if (path) {
        this.config.video_path = path;
        this.checkVideoPath();
      }
    },
    selectDesignFile() {
      select_design_path().then((path) => {
        if (path) {
          this.config.design_path = path;
          this.checkDesignPath();
        }
      });
    },
    selectDesignFileFromDropdown(path) {
      // console.log(`selectDesignFileFromDropdown: ${path}`);
      if (path) {
        this.config.design_path = path;
        this.checkDesignPath();
      }
    },
    async isValid() {
      if (this.validVideo === null) {
        await this.checkVideoPath();
      }
      if (this.validDesign === null) {
        await this.checkDesignPath();
      }

      return this.validVideo && this.validDesign && this.hasFeatures;
    },
    async checkVideoPath() {
      if (!this.staticPaths && this.config.video_path) {
        return check_video_path(this.config.video_path).then((ok) => {
          this.validVideo = ok;
          return ok;
        });
      } else {
        // don't bother sending a request if empty string
        if (!this.staticPaths) {
          this.validVideo = false;
        }
      }
    },
    async checkDesignPath() {
      if (!this.staticPaths && this.config.design_path) {
        return check_design_path(this.config.design_path).then((ok) => {
          this.validDesign = ok;
          return ok;
        });
      } else {
        // don't bother sending a request if empty string
        if (!this.staticPaths) {
          this.validDesign = false;
        }
      }
    },
  },
  watch: {
    config() {
      // console.log("BasicConfig.watch.config()");
      for (let i = 0; i < this.config.features.length; i++) {
        if (!this.config.feature_parameters[i]) {
          this.config.feature_parameters[i] = JSON.parse(
            JSON.stringify(
              this.features.parameter_defaults[this.config.features[i]]
            )
          );
        }
      }
    },
    frame_interval_settings() {
      try {
        this.selectFrameIntervalSetting(this.config.frame_interval_setting);
      } catch (err) {
        console.warn(err);
      }
    },
  },
  computed: {
    hasFeatures() {
      return this.config.features.length > 0;
    },
    frame_interval_settings() {
      return this.$store.getters["schemas/getFrameIntervalSetting"];
    },
    features() {
      return this.$store.getters["schemas/getFeature"];
    },
    files() {
      return [
        {
          model: "video_path",
          type: "video",
          icon: "fa fa-file-video-o",
          browse: this.selectVideoFile,
          select: this.selectVideoFileFromDropdown,
          check: this.checkVideoPath,
          valid: this.validVideo,
        },
        {
          model: "design_path",
          type: "design",
          icon: "fa fa-file-code-o",
          browse: this.selectDesignFile,
          select: this.selectDesignFileFromDropdown,
          check: this.checkDesignPath,
          valid: this.validDesign,
        },
      ];
    },
  },
  asyncComputed: {
    path_options: {
      async get() {
        return get_recent_paths().then((options) => {
          if (!this.config.video_path) {
            this.config.video_path = options.video_path[0];
            this.checkVideoPath();
          }
          if (!this.config.design_path) {
            this.config.design_path = options.design_path[0];
            this.checkDesignPath();
          }
          return options;
        });
      },
      default: {
        video_path: [],
        design_path: [],
      },
    },
  },
  data() {
    return {
      showHeight: false,
      validVideo: null,
      validDesign: null,
      path_options: {
        video_path: [],
        design_path: [],
      },
    };
  },
};
</script>

<style lang="scss">
@import "../../assets/scss/_bootstrap-variables";
@import "../../assets/scss/_core-variables";
@import "node_modules/bootstrap/scss/functions";

$gap: 4px;

$fit-height: 30px; // should be smaller than form elements

$path-browse-width: 32px;
$path-select-width: 32px;
$path-button-width: calc(#{$path-browse-width} + #{$path-select-width});

$fis-select-width: 60px;
$fis-value-width: 60px;

$feature-selector-width: 160px;
$parameter-field-width: 60px;
$remove-button-width: 24px;
$add-button-width: 120px;

.basic-config {
  padding: 0;
  margin: 0;
  max-width: 100% !important;
}

.basic-config-row {
  padding: 0;
  margin: 0;
  padding-bottom: $gap;
  padding-right: $gap;
}

.path-prepend {
  width: $path-button-width;
  padding-right: 1px;
}

.path-browse {
  width: $path-browse-width;
  border-style: none;
  padding: 0;
  font-size: 16px;
  &:disabled {
    pointer-events: none;
  }
}

.path-select {
  border-style: none;
  ::v-deep .btn {
    width: $path-select-width;
    padding: 0;
    font-size: 16px;
    &:disabled {
      pointer-events: none;
    }
  }
}

.basic-config-row .leftmost-col {
  padding: 0;
  margin: 0;
  max-width: $path-button-width;

  .leftmost-label {
    height: $fit-height;
    width: $path-button-width;
    text-align: right;
    padding-right: $gap;
    padding-left: 0;
    border: hidden;
    background: none;
    display: block;
    flex-shrink: 0;
    flex-grow: 0;
    * {
      text-align: right;
    }
  }
}

.basic-config-row .frame-col {
  padding: 0;
  margin: 0;
  .basic-config-row {
    padding: 0;
  }
}

.basic-config-row .feature-col {
  padding: 0;
  margin: 0;
  max-width: $feature-selector-width;
  margin-right: $gap;

  .basic-config-row {
    padding: 0;
  }

  .feature-selector {
    width: $feature-selector-width;
    padding: $gap;
  }
}

.basic-config-row .parameter-col {
  padding: 0;
  margin: 0;
  .basic-config-row {
    padding: 0;
    .parameter-group {
      width: auto;
      margin-right: $gap;
      margin-bottom: $gap;
    }
    margin-bottom: -$gap; // cancel out the bottom-most layer of .parameter-group
  }
}

.basic-config-row .remove-col {
  padding: 0;
  margin: 0;
  max-width: $remove-button-width;
  .remove-button {
    width: $remove-button-width;
    height: $remove-button-width;
    padding: 0;
    text-align: center;
    font-size: 14px;
    background: transparent;
    border: none;
    pointer-events: all;
    &:hover {
      background: theme-color("danger");
      color: theme-color("gray-100");
      cursor: pointer;
    }
  }
}

.add-button-text {
  //color: transparent;
}

.basic-config-row .add-feature-col {
  padding: 0;
  margin: 0;
  margin-right: $gap;

  .add-button {
    border: none;
    background: transparent;
    color: transparent;
    border-radius: 0;
    padding-left: 8px;
    pointer-events: all;
    -webkit-user-select: none; /* Safari */
    -moz-user-select: none; /* Firefox */
    -ms-user-select: none; /* IE10+/Edge */
    user-select: none; /* Standard */
    &:hover {
      background: theme-color("gray-500");
      color: theme-color("gray-100") !important;
      cursor: pointer;
    }
    &:focus {
      color: theme-color("gray-700");
    }
    &:hover * {
      color: theme-color("gray-100") !important;
    }
    .fa {
      color: theme-color("gray-700");
    }
  }
}

.basic-config-label {
  border-radius: 0;
  margin-right: -1px;
}

.fis-selector {
  padding: $gap;
  padding-left: calc(2 * #{$gap});
  margin-right: $gap;
  max-width: $fis-select-width;
  min-width: $fis-select-width;
}

.fis-value {
  max-width: $fis-value-width;
  -webkit-appearance: none; // no arrows
  -moz-appearance: textfield;
}
</style>
