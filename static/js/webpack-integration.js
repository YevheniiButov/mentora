/**
 * WebpackIntegration - Интеграция с Webpack для сборки проектов
 * Поддерживает конфигурацию, HMR, TypeScript и оптимизацию
 */

// Проверяем, не объявлен ли уже класс
if (typeof WebpackIntegration === 'undefined') {
    class WebpackIntegration {
        constructor() {
            this.isInitialized = false;
            this.webpackDevServer = null;
            this.config = {
                mode: 'development',
                entry: './src/index.js',
                output: {
                    path: '/dist',
                    filename: 'bundle.js'
                },
                module: {
                    rules: []
                },
                plugins: [],
                devServer: {
                    port: 3000,
                    hot: true,
                    open: true
                }
            };
            
            this.supportedFrameworks = {
                react: {
                    presets: ['@babel/preset-react'],
                    plugins: ['react-hot-loader/babel']
                },
                vue: {
                    plugins: ['vue-loader']
                },
                angular: {
                    plugins: ['@angular/compiler-cli']
                }
            };
            
            this.initialize();
        }
        
        async initialize() {
            try {
                console.log('🔧 Initializing Webpack integration...');
                
                // Загружаем Webpack Dev Server
                await this.loadWebpackDevServer();
                
                // Настраиваем базовую конфигурацию
                this.setupDefaultConfig();
                
                this.isInitialized = true;
                console.log('✅ Webpack integration initialized');
                
            } catch (error) {
                console.error('❌ Webpack initialization failed:', error);
                throw error;
            }
        }
        
        async loadWebpackDevServer() {
            return new Promise((resolve, reject) => {
                if (window.webpack && window.webpack.optimize) {
                    console.log('✅ Webpack already loaded');
                    resolve();
                    return;
                }
                
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/webpack@5.88.0/dist/webpack.min.js';
                script.onload = () => {
                    console.log('✅ Webpack loaded from CDN');
                    resolve();
                };
                script.onerror = () => {
                    console.warn('⚠️ Failed to load Webpack from CDN, using fallback');
                    this.setupFallbackMode();
                    resolve();
                };
                document.head.appendChild(script);
            });
        }
        
        setupFallbackMode() {
            console.log('🔄 Setting up Webpack fallback mode');
            // Создаем заглушку для Webpack
            window.webpack = {
                optimize: {
                    ModuleConcatenationPlugin: class {
                        constructor() {}
                        apply() {}
                    }
                },
                container: {
                    ModuleFederationPlugin: class {
                        constructor() {}
                        apply() {}
                    }
                }
            };
        }
        
        setupDefaultConfig() {
            // Базовые правила для разных типов файлов
            this.config.module.rules = [
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            presets: ['@babel/preset-env']
                        }
                    }
                },
                {
                    test: /\.css$/,
                    use: ['style-loader', 'css-loader']
                },
                {
                    test: /\.(png|svg|jpg|jpeg|gif)$/i,
                    type: 'asset/resource'
                }
            ];
            
            // Базовые плагины
            this.config.plugins = [
                new (window.webpack?.optimize?.ModuleConcatenationPlugin || class {})()
            ];
        }
        
        configureForFramework(framework) {
            const frameworkConfig = this.supportedFrameworks[framework];
            if (!frameworkConfig) {
                throw new Error(`Unsupported framework: ${framework}`);
            }
            
            console.log(`🔧 Configuring Webpack for ${framework}...`);
            
            // Добавляем специфичные правила для фреймворка
            switch (framework) {
                case 'react':
                    this.addReactSupport();
                    break;
                case 'vue':
                    this.addVueSupport();
                    break;
                case 'angular':
                    this.addAngularSupport();
                    break;
            }
            
            // Обновляем entry point
            this.config.entry = `./src/index.${framework === 'vue' ? 'vue' : 'js'}`;
            
            console.log(`✅ Webpack configured for ${framework}`);
        }
        
        addReactSupport() {
            // Добавляем поддержку JSX
            this.config.module.rules.push({
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env', '@babel/preset-react'],
                        plugins: ['react-hot-loader/babel']
                    }
                }
            });
            
            // Добавляем расширения
            this.config.resolve = {
                extensions: ['.js', '.jsx', '.json']
            };
        }
        
        addVueSupport() {
            // Добавляем поддержку Vue
            this.config.module.rules.push({
                test: /\.vue$/,
                loader: 'vue-loader'
            });
            
            // Добавляем плагин Vue
            if (window.VueLoaderPlugin) {
                this.config.plugins.push(new window.VueLoaderPlugin());
            }
            
            // Добавляем расширения
            this.config.resolve = {
                extensions: ['.js', '.vue', '.json']
            };
        }
        
        addAngularSupport() {
            // Добавляем поддержку TypeScript для Angular
            this.config.module.rules.push({
                test: /\.ts$/,
                use: 'ts-loader',
                exclude: /node_modules/
            });
            
            // Добавляем расширения
            this.config.resolve = {
                extensions: ['.ts', '.js', '.json']
            };
        }
        
        addTypeScriptSupport() {
            console.log('🔧 Adding TypeScript support...');
            
            // Добавляем правило для TypeScript
            this.config.module.rules.push({
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/
            });
            
            // Добавляем расширения
            if (!this.config.resolve) {
                this.config.resolve = {};
            }
            if (!this.config.resolve.extensions) {
                this.config.resolve.extensions = [];
            }
            this.config.resolve.extensions.push('.ts', '.tsx');
            
            // Создаем tsconfig.json если его нет
            this.createTypeScriptConfig();
            
            console.log('✅ TypeScript support added');
        }
        
        createTypeScriptConfig() {
            const tsConfig = {
                compilerOptions: {
                    target: "es5",
                    lib: ["dom", "dom.iterable", "es6"],
                    allowJs: true,
                    skipLibCheck: true,
                    esModuleInterop: true,
                    allowSyntheticDefaultImports: true,
                    strict: true,
                    forceConsistentCasingInFileNames: true,
                    noFallthroughCasesInSwitch: true,
                    module: "esnext",
                    moduleResolution: "node",
                    resolveJsonModule: true,
                    isolatedModules: true,
                    noEmit: false,
                    jsx: "react-jsx"
                },
                include: ["src"]
            };
            
            // Сохраняем конфигурацию
            this.saveConfigFile('tsconfig.json', tsConfig);
        }
        
        addHotModuleReplacement() {
            console.log('🔥 Adding Hot Module Replacement...');
            
            // Добавляем HMR в entry
            if (typeof this.config.entry === 'string') {
                this.config.entry = [
                    'webpack-dev-server/client/index.js?/',
                    'webpack/hot/dev-server.js',
                    this.config.entry
                ];
            } else if (Array.isArray(this.config.entry)) {
                this.config.entry.unshift(
                    'webpack-dev-server/client/index.js?/',
                    'webpack/hot/dev-server.js'
                );
            }
            
            // Добавляем плагин HMR
            if (window.webpack?.HotModuleReplacementPlugin) {
                this.config.plugins.push(new window.webpack.HotModuleReplacementPlugin());
            }
            
            // Настраиваем dev server
            this.config.devServer.hot = true;
            this.config.devServer.liveReload = false;
            
            console.log('✅ Hot Module Replacement added');
        }
        
        addOptimization() {
            console.log('⚡ Adding optimization...');
            
            this.config.optimization = {
                minimize: this.config.mode === 'production',
                splitChunks: {
                    chunks: 'all',
                    cacheGroups: {
                        vendor: {
                            test: /[\\/]node_modules[\\/]/,
                            name: 'vendors',
                            chunks: 'all'
                        }
                    }
                }
            };
            
            console.log('✅ Optimization added');
        }
        
        async buildProject(projectData) {
            try {
                console.log('🔨 Building project with Webpack...');
                
                // Создаем временную структуру проекта
                const projectStructure = await this.createProjectStructure(projectData);
                
                // Генерируем конфигурацию Webpack
                const webpackConfig = this.generateWebpackConfig(projectStructure);
                
                // Симулируем сборку
                const buildResult = await this.simulateBuild(webpackConfig, projectStructure);
                
                console.log('✅ Project built successfully');
                return buildResult;
                
            } catch (error) {
                console.error('❌ Build failed:', error);
                throw error;
            }
        }
        
        async createProjectStructure(projectData) {
            const structure = {
                src: {
                    'index.js': this.generateEntryPoint(projectData),
                    'styles.css': projectData.css || '',
                    'components': {}
                },
                public: {
                    'index.html': projectData.html || '<!DOCTYPE html><html><head><title>Project</title></head><body><div id="root"></div></body></html>'
                },
                'package.json': this.generatePackageJson(projectData),
                'webpack.config.js': ''
            };
            
            // Добавляем компоненты если есть
            if (projectData.components) {
                projectData.components.forEach(component => {
                    structure.src.components[`${component.name}.js`] = component.code;
                });
            }
            
            return structure;
        }
        
        generateEntryPoint(projectData) {
            let entry = '';
            
            if (projectData.framework === 'react') {
                entry = `
import React from 'react';
import ReactDOM from 'react-dom';
import './styles.css';

${projectData.components?.map(comp => `import ${comp.name} from './components/${comp.name}.js';`).join('\n') || ''}

function App() {
    return (
        <div className="app">
            ${projectData.components?.map(comp => `<${comp.name} />`).join('\n            ') || ''}
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));
                `;
            } else if (projectData.framework === 'vue') {
                entry = `
import { createApp } from 'vue';
import './styles.css';

${projectData.components?.map(comp => `import ${comp.name} from './components/${comp.name}.vue';`).join('\n') || ''}

const app = createApp({
    components: {
        ${projectData.components?.map(comp => comp.name).join(',\n        ') || ''}
    }
});

app.mount('#app');
                `;
            } else {
                entry = `
import './styles.css';

${projectData.components?.map(comp => `import './components/${comp.name}.js';`).join('\n') || ''}

console.log('Project loaded successfully!');
                `;
            }
            
            return entry;
        }
        
        generatePackageJson(projectData) {
            const dependencies = {
                "webpack": "^5.88.0",
                "webpack-cli": "^5.1.0",
                "webpack-dev-server": "^4.15.0"
            };
            
            if (projectData.framework === 'react') {
                dependencies.react = "^18.2.0";
                dependencies["react-dom"] = "^18.2.0";
                dependencies["@babel/preset-react"] = "^7.22.0";
            } else if (projectData.framework === 'vue') {
                dependencies.vue = "^3.3.0";
                dependencies["vue-loader"] = "^17.2.0";
            }
            
            return {
                name: projectData.name || "webpack-project",
                version: "1.0.0",
                description: projectData.description || "Webpack project",
                main: "src/index.js",
                scripts: {
                    "start": "webpack serve --mode development",
                    "build": "webpack --mode production",
                    "dev": "webpack serve --mode development --open"
                },
                dependencies: dependencies,
                devDependencies: {
                    "@babel/core": "^7.22.0",
                    "@babel/preset-env": "^7.22.0",
                    "babel-loader": "^9.1.0",
                    "css-loader": "^6.8.0",
                    "style-loader": "^3.3.0"
                }
            };
        }
        
        generateWebpackConfig(projectStructure) {
            // Копируем базовую конфигурацию
            const config = JSON.parse(JSON.stringify(this.config));
            
            // Добавляем специфичные настройки
            config.output.path = require('path').resolve(__dirname, 'dist');
            config.output.publicPath = '/';
            
            return config;
        }
        
        async simulateBuild(webpackConfig, projectStructure) {
            // Симулируем процесс сборки
            const startTime = Date.now();
            
            // Имитируем время сборки
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            const buildTime = Date.now() - startTime;
            
            return {
                success: true,
                duration: buildTime,
                output: {
                    bundle: 'bundle.js',
                    vendor: 'vendors.js',
                    css: 'styles.css'
                },
                stats: {
                    modules: projectStructure.src ? Object.keys(projectStructure.src).length : 0,
                    chunks: 2,
                    assets: 3
                }
            };
        }
        
        saveConfigFile(filename, content) {
            // В реальном приложении здесь будет сохранение файла
            console.log(`💾 Config file ${filename} would be saved:`, content);
        }
        
        getConfig() {
            return this.config;
        }
        
        updateConfig(newConfig) {
            this.config = { ...this.config, ...newConfig };
            console.log('✅ Webpack config updated');
        }
        
        isReady() {
            return this.isInitialized;
        }
    }
    
    // Инициализация при загрузке страницы
    let webpackIntegration;
    document.addEventListener('DOMContentLoaded', () => {
        webpackIntegration = new WebpackIntegration();
    });
    
    // Экспорт для использования в других модулях
    window.WebpackIntegration = WebpackIntegration;
} 