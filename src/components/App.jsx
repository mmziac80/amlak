import { MapComponent, MapTypes } from '@neshan-maps-platform/mapbox-gl-react';
import nmp_mapboxgl from '@neshan-maps-platform/mapbox-gl';
import polyline from '@mapbox/polyline';
import '@neshan-maps-platform/mapbox-gl/dist/NeshanMapboxGl.css';

function App() {
	const mapSetter = neshanMap => {
		// Add custom marker 1

		new nmp_mapboxgl.Marker({ color: 'purple' })
			.setLngLat([51.31173, 35.758954])
			.addTo(neshanMap);

		// Create a popup

		const popup = new nmp_mapboxgl.Popup({ offset: 25 }).setText(
			'با نگه داشتن مارکر می‌توانید آن را روی نقشه جابه‌جا کنید'
		);

		// Add custom marker 2

		new nmp_mapboxgl.Marker({
			color: '#00F955',
			draggable: true,
		})
			.setPopup(popup)
			.setLngLat([51.4055941, 35.70019216])
			.addTo(neshanMap)
			.togglePopup();

		// Add some custom markers using geojson

		const geojson = {
			type: 'FeatureCollection',
			features: [
				{
					type: 'Feature',
					geometry: {
						type: 'Point',
						coordinates: [51.338057, 35.699736],
					},
					properties: {
						title: 'میدان آزادی',
						description:
							'نمایش مارکر با آیکون اختصاصی <br/> مختصات:<br/> [51.338057 , 35.699736]',
					},
				},
				{
					type: 'Feature',
					geometry: {
						type: 'Point',
						coordinates: [51.375265, 35.74472],
					},
					properties: {
						title: 'برج میلاد',
						description: 'مختصات:<br/> [51.375265 , 35.744720]',
					},
				},
			],
		};

		for (const feature of geojson.features) {
			new nmp_mapboxgl.Marker()
				.setLngLat(feature.geometry.coordinates)
				.setPopup(
					new nmp_mapboxgl.Popup({ offset: 40 }).setHTML(
						`<h3>${feature.properties.title}</h3><p>${feature.properties.description}</p>`
					)
				)
				.addTo(neshanMap)
				.togglePopup();
		}

		// Add route

		const exampleResponse = {
			routes: [
				{
					overview_polyline: {
						points: 'cy{xEa{sxHCyEr@}FIi@MWi@Um@L[l@A^{Jr@',
					},
					legs: [
						{
							summary: 'میدان انقلاب اسلامی - کارگر شمالی',
							distance: {
								value: 555.0,
								text: '۵۷۵ متر',
							},
							duration: {
								value: 99.0,
								text: '۲ دقیقه',
							},
							steps: [
								{
									name: 'آزادی',
									instruction: 'در جهت شرق در آزادی قرار بگیرید',
									bearing_after: 88,
									type: 'depart',
									distance: {
										value: 197.0,
										text: '۲۰۰ متر',
									},
									duration: {
										value: 35.0,
										text: '۱ دقیقه',
									},
									polyline: 'cy{xEa{sxHAkBAmBDa@BKHs@BWD]J{@',
									start_location: [51.388811, 35.70082],
								},
								{
									name: 'کارگر شمالی',
									instruction:
										'در میدان انقلاب اسلامی، از خروجی سوم، خارج شوید',
									rotaryName: 'میدان انقلاب اسلامی',
									bearing_after: 111,
									type: 'rotary',
									modifier: 'straight',
									exit: 3,
									distance: {
										value: 146.0,
										text: '۱۵۰ متر',
									},
									duration: {
										value: 38.0,
										text: '۱ دقیقه',
									},
									polyline: '}w{xEohtxHDSBUCUESEKGKSOUEW@UJORKXAN?N',
									start_location: [51.390956, 35.700632],
								},
								{
									name: '',
									instruction: 'به مسیر خود ادامه دهید',
									bearing_after: 354,
									type: 'exit rotary',
									modifier: 'right',
									exit: 3,
									distance: {
										value: 212.0,
										text: '۲۲۵ متر',
									},
									duration: {
										value: 39.0,
										text: '۱ دقیقه',
									},
									polyline: 'a|{xEuitxH_ADaBLO@{BRmAH',
									start_location: [51.391154, 35.701293],
								},
								{
									name: 'کارگر شمالی',
									instruction: 'در مقصد قرار دارید',
									bearing_after: 0,
									type: 'arrive',
									distance: {
										value: 0.0,
										text: '',
									},
									duration: {
										value: 0.0,
										text: '',
									},
									polyline: '}g|xEahtxH',
									start_location: [51.390885, 35.703188],
								},
							],
						},
					],
				},
			],
		};

		const routes = [];
		const points = [];

		for (let k = 0; k < exampleResponse.routes.length; k++) {
			for (let j = 0; j < exampleResponse.routes[k].legs.length; j++) {
				for (
					let i = 0;
					i < exampleResponse.routes[k].legs[j].steps.length;
					i++
				) {
					const step =
						exampleResponse.routes[k].legs[j].steps[i]['polyline'];
					const point =
						exampleResponse.routes[k].legs[j].steps[i]['start_location'];

					const route = polyline.decode(step, 5);

					route.map(item => {
						item.reverse();
					});

					routes.push(route);
					points.push(point);
				}
			}
		}

		const routeObj = {
			type: 'FeatureCollection',
			features: [
				{
					type: 'Feature',
					geometry: {
						type: 'MultiLineString',
						coordinates: routes,
					},
				},
			],
		};

		const pointsObj = {
			type: 'FeatureCollection',
			features: [
				{
					type: 'Feature',
					geometry: {
						type: 'MultiPoint',
						coordinates: points,
					},
				},
			],
		};

		neshanMap.on('load', function () {
			neshanMap.addSource('route', {
				type: 'geojson',
				data: routeObj,
			});
			neshanMap.addSource('points1', {
				type: 'geojson',
				data: pointsObj,
			});

			neshanMap.addLayer({
				id: 'route-line',
				type: 'line',
				source: 'route',
				layout: {
					'line-join': 'round',
					'line-cap': 'round',
				},
				paint: {
					'line-color': '#250ECD',
					'line-width': 9,
				},
			});

			neshanMap.addLayer({
				id: 'points1',
				type: 'circle',
				source: 'points1',
				paint: {
					'circle-color': '#9fbef9',
					'circle-stroke-color': '#FFFFFF',
					'circle-stroke-width': 2,
					'circle-radius': 5,
				},
			});
		});
	};

	return (
		<MapComponent
			options={{
				mapKey: import.meta.env.VITE_MAP_API_KEY,
				mapType: MapTypes.neshanRasterNight,
				zoom: 11,
				center: [51.389, 35.6892],
			}}
			mapSetter={mapSetter}
		/>
	);
}

export default App;
