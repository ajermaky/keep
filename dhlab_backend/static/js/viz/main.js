// Generated by CoffeeScript 1.6.1

requirejs.config({
  paths: {
    vendor: '/js/vendor',
    dataTables: '/js/vendor/datatables/jquery.dataTables.min',
    bootstrapTables: '/js/vendor/datatables/bootstrap.dataTables',
    masonry: '/js/vendor/masonry/jquery.masonry',
    leaflet: '/js/vendor/leaflet/leaflet',
    heatmap: '/js/vendor/leaflet/heatmap',
    leaflet_heatmap: '/js/vendor/leaflet/heatmap-leaflet',
    leaflet_cluster: '/js/vendor/leaflet/leaflet.markercluster'
  },
  shim: {
    'vendor/underscore': {
      exports: '_'
    },
    'vendor/backbone-min': {
      deps: ['vendor/underscore', 'jquery'],
      exports: 'Backbone'
    },
    'dataTables': {
      deps: ['jquery']
    },
    'bootstrapTables': {
      deps: ['dataTables']
    },
    'masonry': {
      deps: ['jquery']
    },
    'leaflet': {
      deps: ['jquery'],
      exports: 'L'
    },
    'leaflet_heatmap': {
      deps: ['leaflet', 'heatmap']
    },
    'leaflet_cluster': {
      deps: ['leaflet']
    }
  }
});

require(['views', 'dataTables', 'bootstrapTables'], function(DataView) {
  return document.vizApp = new DataView();
});
