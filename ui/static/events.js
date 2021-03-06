export const events = {
  seek: {
    get(analyzer_id) {
      return `seek-sync-${analyzer_id}`;
    },
    reset(analyzer_id) {
      return `seek-reset-${analyzer_id}`;
    },
    set(analyzer_id) {
      return `seek-go-${analyzer_id}`;
    },
    step_fw(analyzer_id) {
      return `seek-forward-${analyzer_id}`;
    },
    step_bw(analyzer_id) {
      return `seek-backward-${analyzer_id}`;
    },
  },
  sidebar: {
    status(analyzer_id) {
      return `sidebar-status-${analyzer_id}`;
    },
    close(analyzer_id) {
      return `sidebar-close-${analyzer_id}`;
    },
    cancel(analyzer_id) {
      return `sidebar-cancel-${analyzer_id}`;
    },
    open(url) {
      return `sidebar-open-${url}`;
    },
    highlight(url) {
      return `sidebar-highlight-${url}`;
    },
    unhighlight(url) {
      return `sidebar-unhighlight-${url}`;
    },
  },
  config: {
    change(analyzer_id) {
      return `config-change-${analyzer_id}`;
    },
  },
  data: {
    update(analyzer_id) {
      return `data-update-${analyzer_id}`;
    },
  },
};

export const COMMIT = "commit";
export const ENTER_FOCUSOUT_INTERVAL = 1000;
