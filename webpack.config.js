const path = require('path');

module.exports = {
    mode: 'production', // تنظیم حالت تولید
    entry: {
        'bundle': './static/js/admin/location_picker.js',
        'neshan_map': './static/js/neshan_map.js',
        'leaflet-draw': './static/js/leaflet.draw.js',
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'static/dist'),
        clean: true // پاک کردن خودکار فایل‌های قدیمی
    },
    resolve: {
        alias: {
            '@neshan-maps-platform/mapbox-gl-vue': path.resolve(__dirname, 'node_modules/@neshan-maps-platform/mapbox-gl-vue')
        }
    },
    optimization: {
        splitChunks: {
            chunks: 'all',
            maxSize: 244000, // حداکثر سایز هر چانک
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all'
                }
            }
        },
        minimize: true
    },
    performance: {
        hints: false // غیرفعال کردن هشدارهای سایز
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader'
                }
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    }
};
