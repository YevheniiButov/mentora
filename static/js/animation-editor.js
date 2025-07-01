/**
 * Visual Animation Editor for GrapesJS
 * Визуальный редактор анимаций для GrapesJS
 * 
 * Professional animation editor with timeline controls and bilingual interface
 * Профессиональный редактор анимаций с элементами управления временной шкалой и двуязычным интерфейсом
 */

(function() {
    'use strict';

    // Bilingual translations
    const translations = {
        en: {
            // Timeline controls
            timeline: 'Timeline',
            play: 'Play',
            pause: 'Pause',
            restart: 'Restart',
            stop: 'Stop',
            addKeyframe: 'Add Keyframe',
            removeKeyframe: 'Remove Keyframe',
            keyframe: 'Keyframe',
            
            // Animation properties
            duration: 'Duration',
            delay: 'Delay',
            easing: 'Easing',
            iterations: 'Iterations',
            direction: 'Direction',
            fillMode: 'Fill Mode',
            
            // Animation categories
            entrance: 'Entrance',
            attention: 'Attention',
            exit: 'Exit',
            custom: 'Custom',
            
            // Trigger options
            triggers: 'Triggers',
            onLoad: 'On Page Load',
            onScroll: 'On Scroll',
            onHover: 'On Hover',
            onClick: 'On Click',
            onViewport: 'On Viewport Enter',
            
            // Animation names
            fadeIn: 'Fade In',
            slideIn: 'Slide In',
            bounceIn: 'Bounce In',
            zoomIn: 'Zoom In',
            pulse: 'Pulse',
            shake: 'Shake',
            bounce: 'Bounce',
            flash: 'Flash',
            fadeOut: 'Fade Out',
            slideOut: 'Slide Out',
            zoomOut: 'Zoom Out',
            gentleFloat: 'Gentle Float',
            shimmer: 'Shimmer',
            
            // UI elements
            preview: 'Preview',
            properties: 'Properties',
            library: 'Animation Library',
            export: 'Export CSS',
            import: 'Import',
            reset: 'Reset',
            apply: 'Apply',
            cancel: 'Cancel',
            
            // Help text
            helpTimeline: 'Drag the playhead or use controls to preview animation',
            helpKeyframes: 'Click on timeline to add keyframes, drag to adjust timing',
            helpTriggers: 'Choose when the animation should start',
            helpProperties: 'Adjust animation timing and behavior'
        },
        ru: {
            // Timeline controls
            timeline: 'Временная шкала',
            play: 'Воспроизвести',
            pause: 'Пауза',
            restart: 'Перезапустить',
            stop: 'Остановить',
            addKeyframe: 'Добавить ключевой кадр',
            removeKeyframe: 'Удалить ключевой кадр',
            keyframe: 'Ключевой кадр',
            
            // Animation properties
            duration: 'Длительность',
            delay: 'Задержка',
            easing: 'Плавность',
            iterations: 'Повторения',
            direction: 'Направление',
            fillMode: 'Режим заполнения',
            
            // Animation categories
            entrance: 'Появление',
            attention: 'Внимание',
            exit: 'Исчезновение',
            custom: 'Пользовательские',
            
            // Trigger options
            triggers: 'Триггеры',
            onLoad: 'При загрузке страницы',
            onScroll: 'При прокрутке',
            onHover: 'При наведении',
            onClick: 'При клике',
            onViewport: 'При входе в область видимости',
            
            // Animation names
            fadeIn: 'Появление',
            slideIn: 'Скольжение',
            bounceIn: 'Отскок',
            zoomIn: 'Увеличение',
            pulse: 'Пульс',
            shake: 'Тряска',
            bounce: 'Отскок',
            flash: 'Вспышка',
            fadeOut: 'Исчезновение',
            slideOut: 'Скольжение наружу',
            zoomOut: 'Уменьшение',
            gentleFloat: 'Плавное плавание',
            shimmer: 'Мерцание',
            
            // UI elements
            preview: 'Предпросмотр',
            properties: 'Свойства',
            library: 'Библиотека анимаций',
            export: 'Экспорт CSS',
            import: 'Импорт',
            reset: 'Сброс',
            apply: 'Применить',
            cancel: 'Отмена',
            
            // Help text
            helpTimeline: 'Перетащите указатель воспроизведения или используйте элементы управления для предпросмотра анимации',
            helpKeyframes: 'Нажмите на временную шкалу для добавления ключевых кадров, перетащите для настройки времени',
            helpTriggers: 'Выберите, когда должна начаться анимация',
            helpProperties: 'Настройте время и поведение анимации'
        }
    };

    // Helper function to get current language
    function getCurrentLanguage() {
        return document.documentElement.lang || 'en';
    }

    // Helper function to get localized text
    function getLocalizedText(key) {
        const lang = getCurrentLanguage();
        return translations[lang]?.[key] || translations.en[key] || key;
    }

    class AnimationEditor {
        constructor(editor) {
            this.editor = editor;
            this.currentComponent = null;
            this.isPlaying = false;
            this.currentTime = 0;
            this.duration = 1000; // 1 second default
            this.animationId = null;
            this.keyframes = [];
            this.selectedKeyframe = null;
            
            // Animation presets
            this.presets = this.createAnimationPresets();
            
            this.init();
        }

        init() {
            this.createPanel();
            this.bindEvents();
            this.loadAnimateCSS();
        }

        createPanel() {
            const panel = this.editor.Panels.addPanel({
                id: 'animation-editor-panel',
                visible: true,
                buttons: [{
                    id: 'animation-editor-btn',
                    className: 'btn-animation-editor',
                    label: getLocalizedText('timeline'),
                    command: 'animation-editor-panel',
                    active: false
                }]
            });

            const panelContent = `
                <div class="animation-editor">
                    <div class="editor-header">
                        <h3>${getLocalizedText('timeline')}</h3>
                        <div class="timeline-controls">
                            <button class="btn-play" title="${getLocalizedText('play')}">
                                <i class="bi bi-play-fill"></i>
                            </button>
                            <button class="btn-pause" title="${getLocalizedText('pause')}">
                                <i class="bi bi-pause-fill"></i>
                            </button>
                            <button class="btn-restart" title="${getLocalizedText('restart')}">
                                <i class="bi bi-arrow-clockwise"></i>
                            </button>
                            <button class="btn-stop" title="${getLocalizedText('stop')}">
                                <i class="bi bi-stop-fill"></i>
                            </button>
                        </div>
                    </div>

                    <div class="timeline-container">
                        <div class="timeline-ruler">
                            <div class="ruler-marks"></div>
                        </div>
                        <div class="timeline-track">
                            <div class="playhead" id="playhead"></div>
                            <div class="keyframes-container" id="keyframes-container"></div>
                        </div>
                        <div class="timeline-time">
                            <span id="current-time">0.00s</span> / <span id="total-time">1.00s</span>
                        </div>
                    </div>

                    <div class="editor-tabs">
                        <div class="tab-buttons">
                            <button class="tab-btn active" data-tab="library">${getLocalizedText('library')}</button>
                            <button class="tab-btn" data-tab="properties">${getLocalizedText('properties')}</button>
                            <button class="tab-btn" data-tab="triggers">${getLocalizedText('triggers')}</button>
                        </div>

                        <div class="tab-content">
                            <!-- Animation Library Tab -->
                            <div class="tab-panel active" id="library-tab">
                                <div class="animation-categories">
                                    <div class="category-section">
                                        <h4>${getLocalizedText('entrance')}</h4>
                                        <div class="animation-grid">
                                            <div class="animation-item" data-animation="fadeIn">
                                                <div class="animation-preview fadeIn-preview"></div>
                                                <span>${getLocalizedText('fadeIn')}</span>
                                            </div>
                                            <div class="animation-item" data-animation="slideIn">
                                                <div class="animation-preview slideIn-preview"></div>
                                                <span>${getLocalizedText('slideIn')}</span>
                                            </div>
                                            <div class="animation-item" data-animation="bounceIn">
                                                <div class="animation-preview bounceIn-preview"></div>
                                                <span>${getLocalizedText('bounceIn')}</span>
                                            </div>
                                            <div class="animation-item" data-animation="zoomIn">
                                                <div class="animation-preview zoomIn-preview"></div>
                                                <span>${getLocalizedText('zoomIn')}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="category-section">
                                        <h4>${getLocalizedText('attention')}</h4>
                                        <div class="animation-grid">
                                            <div class="animation-item" data-animation="pulse">
                                                <div class="animation-preview pulse-preview"></div>
                                                <span>${getLocalizedText('pulse')}</span>
                                            </div>
                                            <div class="animation-item" data-animation="shake">
                                                <div class="animation-preview shake-preview"></div>
                                                <span>${getLocalizedText('shake')}</span>
                                            </div>
                                            <div class="animation-item" data-animation="bounce">
                                                <div class="animation-preview bounce-preview"></div>
                                                <span>${getLocalizedText('bounce')}</span>
                                            </div>
                                            <div class="animation-item" data-animation="flash">
                                                <div class="animation-preview flash-preview"></div>
                                                <span>${getLocalizedText('flash')}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="category-section">
                                        <h4>${getLocalizedText('exit')}</h4>
                                        <div class="animation-grid">
                                            <div class="animation-item" data-animation="fadeOut">
                                                <div class="animation-preview fadeOut-preview"></div>
                                                <span>${getLocalizedText('fadeOut')}</span>
                                            </div>
                                            <div class="animation-item" data-animation="slideOut">
                                                <div class="animation-preview slideOut-preview"></div>
                                                <span>${getLocalizedText('slideOut')}</span>
                                            </div>
                                            <div class="animation-item" data-animation="zoomOut">
                                                <div class="animation-preview zoomOut-preview"></div>
                                                <span>${getLocalizedText('zoomOut')}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="category-section">
                                        <h4>${getLocalizedText('custom')}</h4>
                                        <div class="animation-grid">
                                            <div class="animation-item" data-animation="gentleFloat">
                                                <div class="animation-preview gentleFloat-preview"></div>
                                                <span>${getLocalizedText('gentleFloat')}</span>
                                            </div>
                                            <div class="animation-item" data-animation="shimmer">
                                                <div class="animation-preview shimmer-preview"></div>
                                                <span>${getLocalizedText('shimmer')}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Properties Tab -->
                            <div class="tab-panel" id="properties-tab">
                                <div class="property-group">
                                    <label>${getLocalizedText('duration')}</label>
                                    <div class="slider-container">
                                        <input type="range" id="anim-duration" min="0.1" max="5" step="0.1" value="1">
                                        <span class="value-display">1.0s</span>
                                    </div>
                                </div>

                                <div class="property-group">
                                    <label>${getLocalizedText('delay')}</label>
                                    <div class="slider-container">
                                        <input type="range" id="anim-delay" min="0" max="2" step="0.1" value="0">
                                        <span class="value-display">0.0s</span>
                                    </div>
                                </div>

                                <div class="property-group">
                                    <label>${getLocalizedText('easing')}</label>
                                    <select id="anim-easing">
                                        <option value="ease">ease</option>
                                        <option value="linear">linear</option>
                                        <option value="ease-in">ease-in</option>
                                        <option value="ease-out">ease-out</option>
                                        <option value="ease-in-out">ease-in-out</option>
                                        <option value="cubic-bezier(0.68, -0.55, 0.265, 1.55)">bounce</option>
                                        <option value="cubic-bezier(0.175, 0.885, 0.32, 1.275)">back</option>
                                    </select>
                                </div>

                                <div class="property-group">
                                    <label>${getLocalizedText('iterations')}</label>
                                    <select id="anim-iterations">
                                        <option value="1">1</option>
                                        <option value="2">2</option>
                                        <option value="3">3</option>
                                        <option value="infinite">∞</option>
                                    </select>
                                </div>

                                <div class="property-group">
                                    <label>${getLocalizedText('direction')}</label>
                                    <select id="anim-direction">
                                        <option value="normal">normal</option>
                                        <option value="reverse">reverse</option>
                                        <option value="alternate">alternate</option>
                                        <option value="alternate-reverse">alternate-reverse</option>
                                    </select>
                                </div>

                                <div class="property-group">
                                    <label>${getLocalizedText('fillMode')}</label>
                                    <select id="anim-fill-mode">
                                        <option value="none">none</option>
                                        <option value="forwards">forwards</option>
                                        <option value="backwards">backwards</option>
                                        <option value="both">both</option>
                                    </select>
                                </div>
                            </div>

                            <!-- Triggers Tab -->
                            <div class="tab-panel" id="triggers-tab">
                                <div class="trigger-options">
                                    <div class="trigger-option">
                                        <input type="radio" id="trigger-load" name="trigger" value="onLoad" checked>
                                        <label for="trigger-load">${getLocalizedText('onLoad')}</label>
                                    </div>
                                    <div class="trigger-option">
                                        <input type="radio" id="trigger-scroll" name="trigger" value="onScroll">
                                        <label for="trigger-scroll">${getLocalizedText('onScroll')}</label>
                                    </div>
                                    <div class="trigger-option">
                                        <input type="radio" id="trigger-hover" name="trigger" value="onHover">
                                        <label for="trigger-hover">${getLocalizedText('onHover')}</label>
                                    </div>
                                    <div class="trigger-option">
                                        <input type="radio" id="trigger-click" name="trigger" value="onClick">
                                        <label for="trigger-click">${getLocalizedText('onClick')}</label>
                                    </div>
                                    <div class="trigger-option">
                                        <input type="radio" id="trigger-viewport" name="trigger" value="onViewport">
                                        <label for="trigger-viewport">${getLocalizedText('onViewport')}</label>
                                    </div>
                                </div>

                                <div class="trigger-settings">
                                    <div class="setting-group" id="scroll-settings" style="display: none;">
                                        <label>Scroll Threshold (%)</label>
                                        <input type="range" id="scroll-threshold" min="0" max="100" value="50">
                                        <span class="value-display">50%</span>
                                    </div>

                                    <div class="setting-group" id="viewport-settings" style="display: none;">
                                        <label>Viewport Threshold (%)</label>
                                        <input type="range" id="viewport-threshold" min="0" max="100" value="20">
                                        <span class="value-display">20%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="editor-actions">
                        <button class="btn-apply">${getLocalizedText('apply')}</button>
                        <button class="btn-export">${getLocalizedText('export')}</button>
                        <button class="btn-reset">${getLocalizedText('reset')}</button>
                    </div>
                </div>
            `;

            panel.set('content', panelContent);
        }

        bindEvents() {
            // Timeline controls
            this.bindTimelineEvents();
            
            // Tab switching
            this.bindTabEvents();
            
            // Animation library
            this.bindLibraryEvents();
            
            // Properties
            this.bindPropertyEvents();
            
            // Triggers
            this.bindTriggerEvents();
            
            // Actions
            this.bindActionEvents();
            
            // Component selection
            this.bindComponentEvents();
        }

        bindTimelineEvents() {
            // Play controls
            document.querySelector('.btn-play')?.addEventListener('click', () => this.play());
            document.querySelector('.btn-pause')?.addEventListener('click', () => this.pause());
            document.querySelector('.btn-restart')?.addEventListener('click', () => this.restart());
            document.querySelector('.btn-stop')?.addEventListener('click', () => this.stop());

            // Timeline interaction
            const timelineTrack = document.querySelector('.timeline-track');
            if (timelineTrack) {
                timelineTrack.addEventListener('click', (e) => this.onTimelineClick(e));
                timelineTrack.addEventListener('mousedown', (e) => this.onTimelineDragStart(e));
            }

            // Keyframe management
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('keyframe')) {
                    this.selectKeyframe(e.target);
                }
            });
        }

        bindTabEvents() {
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const tabName = e.target.dataset.tab;
                    this.switchTab(tabName);
                });
            });
        }

        bindLibraryEvents() {
            document.querySelectorAll('.animation-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    const animationName = e.currentTarget.dataset.animation;
                    this.selectAnimation(animationName);
                });
            });
        }

        bindPropertyEvents() {
            // Duration
            const durationInput = document.getElementById('anim-duration');
            if (durationInput) {
                durationInput.addEventListener('input', (e) => {
                    const value = parseFloat(e.target.value);
                    e.target.nextElementSibling.textContent = value.toFixed(1) + 's';
                    this.duration = value * 1000;
                    this.updateTimeline();
                });
            }

            // Delay
            const delayInput = document.getElementById('anim-delay');
            if (delayInput) {
                delayInput.addEventListener('input', (e) => {
                    const value = parseFloat(e.target.value);
                    e.target.nextElementSibling.textContent = value.toFixed(1) + 's';
                    this.updateAnimationDelay(value * 1000);
                });
            }

            // Other properties
            ['anim-easing', 'anim-iterations', 'anim-direction', 'anim-fill-mode'].forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    element.addEventListener('change', (e) => {
                        this.updateAnimationProperty(id.replace('anim-', ''), e.target.value);
                    });
                }
            });
        }

        bindTriggerEvents() {
            document.querySelectorAll('input[name="trigger"]').forEach(radio => {
                radio.addEventListener('change', (e) => {
                    this.updateTrigger(e.target.value);
                });
            });

            // Trigger-specific settings
            const scrollThreshold = document.getElementById('scroll-threshold');
            if (scrollThreshold) {
                scrollThreshold.addEventListener('input', (e) => {
                    const value = e.target.value;
                    e.target.nextElementSibling.textContent = value + '%';
                    this.updateScrollThreshold(value);
                });
            }

            const viewportThreshold = document.getElementById('viewport-threshold');
            if (viewportThreshold) {
                viewportThreshold.addEventListener('input', (e) => {
                    const value = e.target.value;
                    e.target.nextElementSibling.textContent = value + '%';
                    this.updateViewportThreshold(value);
                });
            }
        }

        bindActionEvents() {
            document.querySelector('.btn-apply')?.addEventListener('click', () => this.applyAnimation());
            document.querySelector('.btn-export')?.addEventListener('click', () => this.exportCSS());
            document.querySelector('.btn-reset')?.addEventListener('click', () => this.resetAnimation());
        }

        bindComponentEvents() {
            this.editor.on('component:selected', (component) => {
                this.currentComponent = component;
                this.loadComponentAnimation();
            });
        }

        // Timeline methods
        play() {
            if (this.isPlaying) return;
            
            this.isPlaying = true;
            this.startTime = Date.now() - this.currentTime;
            this.animate();
            
            document.querySelector('.btn-play').style.display = 'none';
            document.querySelector('.btn-pause').style.display = 'inline-block';
        }

        pause() {
            this.isPlaying = false;
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
            }
            
            document.querySelector('.btn-play').style.display = 'inline-block';
            document.querySelector('.btn-pause').style.display = 'none';
        }

        restart() {
            this.currentTime = 0;
            this.updatePlayhead();
            this.pause();
        }

        stop() {
            this.currentTime = 0;
            this.updatePlayhead();
            this.pause();
            this.resetPreview();
        }

        animate() {
            if (!this.isPlaying) return;
            
            this.currentTime = Date.now() - this.startTime;
            if (this.currentTime >= this.duration) {
                this.currentTime = this.duration;
                this.pause();
            }
            
            this.updatePlayhead();
            this.updatePreview();
            
            this.animationId = requestAnimationFrame(() => this.animate());
        }

        updatePlayhead() {
            const playhead = document.getElementById('playhead');
            if (!playhead) return;
            
            const progress = (this.currentTime / this.duration) * 100;
            playhead.style.left = progress + '%';
            
            document.getElementById('current-time').textContent = (this.currentTime / 1000).toFixed(2) + 's';
        }

        onTimelineClick(e) {
            const rect = e.currentTarget.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const progress = (clickX / rect.width) * 100;
            
            this.currentTime = (progress / 100) * this.duration;
            this.updatePlayhead();
            this.updatePreview();
        }

        onTimelineDragStart(e) {
            const timelineTrack = e.currentTarget;
            const startX = e.clientX;
            const startProgress = this.currentTime / this.duration;
            
            const onMouseMove = (e) => {
                const deltaX = e.clientX - startX;
                const rect = timelineTrack.getBoundingClientRect();
                const deltaProgress = deltaX / rect.width;
                const newProgress = Math.max(0, Math.min(1, startProgress + deltaProgress));
                
                this.currentTime = newProgress * this.duration;
                this.updatePlayhead();
                this.updatePreview();
            };
            
            const onMouseUp = () => {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            };
            
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        }

        // Tab methods
        switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
            
            // Update tab panels
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Show/hide trigger-specific settings
            this.updateTriggerSettings();
        }

        updateTriggerSettings() {
            const selectedTrigger = document.querySelector('input[name="trigger"]:checked')?.value;
            
            document.getElementById('scroll-settings').style.display = 
                selectedTrigger === 'onScroll' ? 'block' : 'none';
            
            document.getElementById('viewport-settings').style.display = 
                selectedTrigger === 'onViewport' ? 'block' : 'none';
        }

        // Animation library methods
        selectAnimation(animationName) {
            // Remove previous selection
            document.querySelectorAll('.animation-item').forEach(item => {
                item.classList.remove('selected');
            });
            
            // Add selection to clicked item
            document.querySelector(`[data-animation="${animationName}"]`).classList.add('selected');
            
            // Apply preview animation
            this.applyPreviewAnimation(animationName);
        }

        applyPreviewAnimation(animationName) {
            if (!this.currentComponent) return;
            
            const animation = this.presets[animationName];
            if (!animation) return;
            
            // Apply animation to component
            this.currentComponent.setStyle({
                'animation-name': animationName,
                'animation-duration': this.duration + 'ms',
                'animation-timing-function': 'ease',
                'animation-iteration-count': '1',
                'animation-fill-mode': 'forwards'
            });
            
            // Add CSS if not already present
            this.addAnimationCSS(animationName, animation);
            
            this.editor.refresh();
        }

        // Property methods
        updateAnimationProperty(property, value) {
            if (!this.currentComponent) return;
            
            const styleMap = {
                'easing': 'animation-timing-function',
                'iterations': 'animation-iteration-count',
                'direction': 'animation-direction',
                'fill-mode': 'animation-fill-mode'
            };
            
            const cssProperty = styleMap[property];
            if (cssProperty) {
                this.currentComponent.setStyle({ [cssProperty]: value });
                this.editor.refresh();
            }
        }

        updateAnimationDelay(delay) {
            if (!this.currentComponent) return;
            
            this.currentComponent.setStyle({ 'animation-delay': delay + 'ms' });
            this.editor.refresh();
        }

        // Trigger methods
        updateTrigger(triggerType) {
            this.updateTriggerSettings();
            
            if (!this.currentComponent) return;
            
            // Remove existing trigger classes
            this.currentComponent.removeClass('animate-on-load animate-on-scroll animate-on-hover animate-on-click animate-on-viewport');
            
            // Add new trigger class
            const triggerClass = `animate-on-${triggerType.replace('on', '').toLowerCase()}`;
            this.currentComponent.addClass(triggerClass);
            
            this.editor.refresh();
        }

        updateScrollThreshold(threshold) {
            // Update scroll trigger threshold
            const style = document.createElement('style');
            style.textContent = `
                .animate-on-scroll[data-scroll-threshold="${threshold}"] {
                    --scroll-threshold: ${threshold}%;
                }
            `;
            document.head.appendChild(style);
        }

        updateViewportThreshold(threshold) {
            // Update viewport trigger threshold
            const style = document.createElement('style');
            style.textContent = `
                .animate-on-viewport[data-viewport-threshold="${threshold}"] {
                    --viewport-threshold: ${threshold}%;
                }
            `;
            document.head.appendChild(style);
        }

        // Action methods
        applyAnimation() {
            if (!this.currentComponent) return;
            
            const selectedAnimation = document.querySelector('.animation-item.selected')?.dataset.animation;
            if (!selectedAnimation) return;
            
            // Apply final animation with all properties
            const duration = document.getElementById('anim-duration').value;
            const delay = document.getElementById('anim-delay').value;
            const easing = document.getElementById('anim-easing').value;
            const iterations = document.getElementById('anim-iterations').value;
            const direction = document.getElementById('anim-direction').value;
            const fillMode = document.getElementById('anim-fill-mode').value;
            
            this.currentComponent.setStyle({
                'animation-name': selectedAnimation,
                'animation-duration': duration + 's',
                'animation-delay': delay + 's',
                'animation-timing-function': easing,
                'animation-iteration-count': iterations,
                'animation-direction': direction,
                'animation-fill-mode': fillMode
            });
            
            this.editor.refresh();
        }

        exportCSS() {
            const selectedAnimation = document.querySelector('.animation-item.selected')?.dataset.animation;
            if (!selectedAnimation) return;
            
            const animation = this.presets[selectedAnimation];
            if (!animation) return;
            
            const css = this.generateAnimationCSS(selectedAnimation, animation);
            
            // Create download link
            const blob = new Blob([css], { type: 'text/css' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${selectedAnimation}-animation.css`;
            link.click();
            URL.revokeObjectURL(url);
        }

        resetAnimation() {
            if (!this.currentComponent) return;
            
            // Remove animation styles
            this.currentComponent.setStyle({
                'animation-name': '',
                'animation-duration': '',
                'animation-delay': '',
                'animation-timing-function': '',
                'animation-iteration-count': '',
                'animation-direction': '',
                'animation-fill-mode': ''
            });
            
            // Remove trigger classes
            this.currentComponent.removeClass('animate-on-load animate-on-scroll animate-on-hover animate-on-click animate-on-viewport');
            
            // Reset UI
            document.querySelectorAll('.animation-item').forEach(item => {
                item.classList.remove('selected');
            });
            
            this.restart();
            this.editor.refresh();
        }

        // Utility methods
        createAnimationPresets() {
            return {
                fadeIn: {
                    keyframes: [
                        { time: 0, properties: { opacity: 0 } },
                        { time: 100, properties: { opacity: 1 } }
                    ]
                },
                slideIn: {
                    keyframes: [
                        { time: 0, properties: { transform: 'translateX(-100%)' } },
                        { time: 100, properties: { transform: 'translateX(0)' } }
                    ]
                },
                bounceIn: {
                    keyframes: [
                        { time: 0, properties: { transform: 'scale(0.3)', opacity: 0 } },
                        { time: 50, properties: { transform: 'scale(1.05)' } },
                        { time: 70, properties: { transform: 'scale(0.9)' } },
                        { time: 100, properties: { transform: 'scale(1)', opacity: 1 } }
                    ]
                },
                zoomIn: {
                    keyframes: [
                        { time: 0, properties: { transform: 'scale(0)', opacity: 0 } },
                        { time: 100, properties: { transform: 'scale(1)', opacity: 1 } }
                    ]
                },
                pulse: {
                    keyframes: [
                        { time: 0, properties: { transform: 'scale(1)' } },
                        { time: 50, properties: { transform: 'scale(1.05)' } },
                        { time: 100, properties: { transform: 'scale(1)' } }
                    ]
                },
                shake: {
                    keyframes: [
                        { time: 0, properties: { transform: 'translateX(0)' } },
                        { time: 10, properties: { transform: 'translateX(-10px)' } },
                        { time: 20, properties: { transform: 'translateX(10px)' } },
                        { time: 30, properties: { transform: 'translateX(-10px)' } },
                        { time: 40, properties: { transform: 'translateX(10px)' } },
                        { time: 50, properties: { transform: 'translateX(-10px)' } },
                        { time: 60, properties: { transform: 'translateX(10px)' } },
                        { time: 70, properties: { transform: 'translateX(-10px)' } },
                        { time: 80, properties: { transform: 'translateX(10px)' } },
                        { time: 90, properties: { transform: 'translateX(-10px)' } },
                        { time: 100, properties: { transform: 'translateX(0)' } }
                    ]
                },
                bounce: {
                    keyframes: [
                        { time: 0, properties: { transform: 'translateY(0)' } },
                        { time: 20, properties: { transform: 'translateY(-20px)' } },
                        { time: 40, properties: { transform: 'translateY(0)' } },
                        { time: 60, properties: { transform: 'translateY(-10px)' } },
                        { time: 80, properties: { transform: 'translateY(0)' } },
                        { time: 100, properties: { transform: 'translateY(0)' } }
                    ]
                },
                flash: {
                    keyframes: [
                        { time: 0, properties: { opacity: 1 } },
                        { time: 25, properties: { opacity: 0 } },
                        { time: 50, properties: { opacity: 1 } },
                        { time: 75, properties: { opacity: 0 } },
                        { time: 100, properties: { opacity: 1 } }
                    ]
                },
                fadeOut: {
                    keyframes: [
                        { time: 0, properties: { opacity: 1 } },
                        { time: 100, properties: { opacity: 0 } }
                    ]
                },
                slideOut: {
                    keyframes: [
                        { time: 0, properties: { transform: 'translateX(0)' } },
                        { time: 100, properties: { transform: 'translateX(100%)' } }
                    ]
                },
                zoomOut: {
                    keyframes: [
                        { time: 0, properties: { transform: 'scale(1)', opacity: 1 } },
                        { time: 100, properties: { transform: 'scale(0)', opacity: 0 } }
                    ]
                },
                gentleFloat: {
                    keyframes: [
                        { time: 0, properties: { transform: 'translateY(0px)' } },
                        { time: 50, properties: { transform: 'translateY(-10px)' } },
                        { time: 100, properties: { transform: 'translateY(0px)' } }
                    ]
                },
                shimmer: {
                    keyframes: [
                        { time: 0, properties: { backgroundPosition: '-200% 0' } },
                        { time: 100, properties: { backgroundPosition: '200% 0' } }
                    ]
                }
            };
        }

        loadAnimateCSS() {
            // Load Animate.css if not already loaded
            if (!document.querySelector('link[href*="animate.css"]')) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';
                document.head.appendChild(link);
            }
        }

        addAnimationCSS(animationName, animation) {
            const existingStyle = document.getElementById(`animation-${animationName}`);
            if (existingStyle) return;
            
            const css = this.generateAnimationCSS(animationName, animation);
            const style = document.createElement('style');
            style.id = `animation-${animationName}`;
            style.textContent = css;
            document.head.appendChild(style);
        }

        generateAnimationCSS(animationName, animation) {
            let css = `@keyframes ${animationName} {\n`;
            
            animation.keyframes.forEach(keyframe => {
                css += `  ${keyframe.time}% {\n`;
                Object.entries(keyframe.properties).forEach(([property, value]) => {
                    css += `    ${property}: ${value};\n`;
                });
                css += `  }\n`;
            });
            
            css += `}\n`;
            
            // Add trigger styles
            css += `
.animate-on-load { animation-play-state: running; }
.animate-on-scroll { animation-play-state: paused; }
.animate-on-hover { animation-play-state: paused; }
.animate-on-hover:hover { animation-play-state: running; }
.animate-on-click { animation-play-state: paused; cursor: pointer; }
.animate-on-click:active { animation-play-state: running; }
.animate-on-viewport { animation-play-state: paused; }
            `;
            
            return css;
        }

        updateTimeline() {
            document.getElementById('total-time').textContent = (this.duration / 1000).toFixed(2) + 's';
            this.updateRuler();
        }

        updateRuler() {
            const ruler = document.querySelector('.ruler-marks');
            if (!ruler) return;
            
            ruler.innerHTML = '';
            const steps = Math.ceil(this.duration / 100);
            
            for (let i = 0; i <= steps; i++) {
                const mark = document.createElement('div');
                mark.className = 'ruler-mark';
                mark.style.left = (i / steps) * 100 + '%';
                
                const label = document.createElement('span');
                label.textContent = (i * 0.1).toFixed(1) + 's';
                mark.appendChild(label);
                
                ruler.appendChild(mark);
            }
        }

        updatePreview() {
            if (!this.currentComponent) return;
            
            const selectedAnimation = document.querySelector('.animation-item.selected')?.dataset.animation;
            if (!selectedAnimation) return;
            
            const animation = this.presets[selectedAnimation];
            if (!animation) return;
            
            // Calculate current keyframe
            const progress = this.currentTime / this.duration;
            const currentKeyframe = this.getCurrentKeyframe(animation, progress);
            
            if (currentKeyframe) {
                Object.entries(currentKeyframe.properties).forEach(([property, value]) => {
                    this.currentComponent.setStyle({ [property]: value });
                });
            }
        }

        getCurrentKeyframe(animation, progress) {
            const time = progress * 100;
            const keyframes = animation.keyframes;
            
            // Find the two keyframes to interpolate between
            let startKeyframe = null;
            let endKeyframe = null;
            
            for (let i = 0; i < keyframes.length - 1; i++) {
                if (time >= keyframes[i].time && time <= keyframes[i + 1].time) {
                    startKeyframe = keyframes[i];
                    endKeyframe = keyframes[i + 1];
                    break;
                }
            }
            
            if (!startKeyframe || !endKeyframe) {
                return keyframes[keyframes.length - 1];
            }
            
            // Interpolate between keyframes
            const localProgress = (time - startKeyframe.time) / (endKeyframe.time - startKeyframe.time);
            const interpolated = {};
            
            Object.keys(startKeyframe.properties).forEach(property => {
                const startValue = startKeyframe.properties[property];
                const endValue = endKeyframe.properties[property];
                interpolated[property] = this.interpolateValue(startValue, endValue, localProgress);
            });
            
            return { properties: interpolated };
        }

        interpolateValue(start, end, progress) {
            // Simple interpolation for numeric values
            if (typeof start === 'number' && typeof end === 'number') {
                return start + (end - start) * progress;
            }
            
            // For transform values, we'll need more complex parsing
            // For now, return the start value
            return start;
        }

        resetPreview() {
            if (!this.currentComponent) return;
            
            // Reset to initial state
            const selectedAnimation = document.querySelector('.animation-item.selected')?.dataset.animation;
            if (selectedAnimation) {
                const animation = this.presets[selectedAnimation];
                if (animation && animation.keyframes[0]) {
                    Object.entries(animation.keyframes[0].properties).forEach(([property, value]) => {
                        this.currentComponent.setStyle({ [property]: value });
                    });
                }
            }
        }

        loadComponentAnimation() {
            if (!this.currentComponent) return;
            
            const style = this.currentComponent.getStyle();
            const animationName = style['animation-name'];
            
            if (animationName) {
                // Select the animation in the library
                document.querySelectorAll('.animation-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                const animationItem = document.querySelector(`[data-animation="${animationName}"]`);
                if (animationItem) {
                    animationItem.classList.add('selected');
                }
                
                // Update property controls
                this.updatePropertyControls(style);
            }
        }

        updatePropertyControls(style) {
            // Update duration
            const duration = style['animation-duration'];
            if (duration) {
                const durationInput = document.getElementById('anim-duration');
                const value = parseFloat(duration);
                if (durationInput) {
                    durationInput.value = value;
                    durationInput.nextElementSibling.textContent = value.toFixed(1) + 's';
                    this.duration = value * 1000;
                }
            }
            
            // Update other properties
            const propertyMap = {
                'animation-delay': 'anim-delay',
                'animation-timing-function': 'anim-easing',
                'animation-iteration-count': 'anim-iterations',
                'animation-direction': 'anim-direction',
                'animation-fill-mode': 'anim-fill-mode'
            };
            
            Object.entries(propertyMap).forEach(([cssProp, inputId]) => {
                const value = style[cssProp];
                if (value) {
                    const input = document.getElementById(inputId);
                    if (input) {
                        input.value = value;
                        if (input.type === 'range') {
                            input.nextElementSibling.textContent = value;
                        }
                    }
                }
            });
            
            this.updateTimeline();
        }
    }

    // Initialize when GrapesJS is ready
    if (typeof grapesjs !== 'undefined') {
        if (grapesjs.editors) {
            // GrapesJS is already loaded
            const editor = grapesjs.editors[0] || window.editor;
            if (editor) {
                window.animationEditor = new AnimationEditor(editor);
            }
        } else {
            // Wait for GrapesJS to load
            document.addEventListener('grapesjs:ready', () => {
                const editor = grapesjs.editors[0] || window.editor;
                if (editor) {
                    window.animationEditor = new AnimationEditor(editor);
                }
            });
        }
    }

    // Export for use in other scripts
    window.AnimationEditor = AnimationEditor;

})(); 