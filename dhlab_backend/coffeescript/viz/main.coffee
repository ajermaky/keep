requirejs.config
	baseUrl: '//d1sht9pkbliybl.cloudfront.net'
	paths:
		vendor: '/static/js/vendor'
		dataTables: '/static/js/vendor/datatables/jquery.dataTables.min'
		bootstrapTables: '/static/js/vendor/datatables/bootstrap.dataTables'

		masonry: '/static/js/vendor/masonry/jquery.masonry'

		leaflet: '/static/js/vendor/leaflet/leaflet'
		heatmap: '/static/js/vendor/leaflet/heatmap'
		leaflet_heatmap: '/static/js/vendor/leaflet/heatmap-leaflet'
		leaflet_cluster: '/static/js/vendor/leaflet/leaflet.markercluster'

	shim:
		# Backbone
		'vendor/underscore':
			exports: '_'
		'vendor/backbone-min':
			deps: [ 'vendor/underscore', 'jquery' ]
			exports: 'Backbone'

		# jQuery DataTables & associated plugins
		'dataTables':
			deps: [ 'jquery' ]
		'bootstrapTables':
			deps: [ 'dataTables' ]

		# Masonry
		'masonry':
			deps: [ 'jquery' ]

		# Leaflet & associated plugins
		'leaflet':
			deps: [ 'jquery' ]
			exports: 'L'
		'leaflet_heatmap':
			deps: [ 'leaflet', 'heatmap' ]
		'leaflet_cluster':
			deps: [ 'leaflet' ]

require( [ 'views', 'dataTables', 'bootstrapTables' ],
	( DataView ) ->
		document.vizApp = new DataView();
)