# Код вкладки "Архив" - Полный комплект

## 1. HTML - Основной контент (левая колонка)

```html
<!-- ARCHIVE TAB CONTENT - в левой колонке -->
<div x-show="activeTab === 'archive'" 
     x-data="archiveComponent()"
     class="archive-container">
    <!-- Category Tabs -->
    <div class="archive-categories">
        <button @click="activeCategory = 'english'; pagination = null; loadItems()" 
                :class="{ 'active': activeCategory === 'english' }"
                class="category-btn">
            <i class="bi bi-book"></i> {{ t('english_passages', lang)|default('English Passages') }}
        </button>
        <button @click="activeCategory = 'terms'; pagination = null; loadItems()" 
                :class="{ 'active': activeCategory === 'terms' }"
                class="category-btn">
            <i class="bi bi-card-text"></i> {{ t('dutch_terms', lang)|default('Dutch Terms') }}
        </button>
        <button @click="activeCategory = 'tests'; pagination = null; loadItems()" 
                :class="{ 'active': activeCategory === 'tests' }"
                class="category-btn">
            <i class="bi bi-clipboard-check"></i> {{ t('medical_tests', lang)|default('Medical Tests') }}
        </button>
        <button @click="activeCategory = 'virtual-patients'; pagination = null; loadItems()" 
                :class="{ 'active': activeCategory === 'virtual-patients' }"
                class="category-btn">
            <i class="bi bi-person-badge"></i> {{ t('virtual_patients', lang)|default('Virtual Patients') }}
        </button>
    </div>

    <!-- Filters -->
    <div class="archive-filters">
        <input type="text" 
               x-model="searchQuery" 
               @input.debounce.300ms="loadItems()"
               placeholder="Search..."
               class="filter-search">
        <select x-model="sortBy" @change="loadItems()" class="filter-select">
            <option value="date">Sort by Date</option>
            <option value="score">Sort by Score</option>
            <option value="time">Sort by Time</option>
        </select>
        <select x-model="sortOrder" @change="loadItems()" class="filter-select">
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
        </select>
    </div>

    <!-- Items List -->
    <div class="archive-items" x-show="!loading && items.length > 0">
        <template x-for="item in items" :key="item.id">
            <div class="archive-item" @click="viewItem(item)">
                <div class="item-header">
                    <h4 x-text="item.title || item.term_nl || item.session_type_label || 'Unknown'"></h4>
                    <div class="item-score" 
                         :class="getScoreClass(item.score_percentage || item.score || item.accuracy || 0)">
                        <span x-text="formatScore(item)"></span>
                    </div>
                </div>
                <div class="item-meta">
                    <span x-show="item.completed_at || item.last_reviewed || item.started_at">
                        <i class="bi bi-calendar"></i>
                        <span x-text="formatDate(item.completed_at || item.last_reviewed || item.started_at)"></span>
                    </span>
                    <span x-show="item.time_spent">
                        <i class="bi bi-clock"></i>
                        <span x-text="formatTime(item.time_spent)"></span>
                    </span>
                    <span x-show="item.total_questions || item.questions_answered">
                        <i class="bi bi-question-circle"></i>
                        <span x-text="(item.total_questions || item.questions_answered) + ' questions'"></span>
                    </span>
                </div>
            </div>
        </template>
    </div>

    <!-- Pagination -->
    <div class="archive-pagination" x-show="pagination && pagination.pages > 1">
        <button @click="changePage((pagination?.page || 1) - 1)" 
                :disabled="!pagination || pagination.page <= 1"
                class="page-btn">
            <i class="bi bi-chevron-left"></i>
        </button>
        <span class="page-info">
            <span x-text="pagination?.page || 1"></span> / <span x-text="pagination?.pages || 1"></span>
        </span>
        <button @click="changePage((pagination?.page || 1) + 1)" 
                :disabled="!pagination || pagination.page >= pagination.pages"
                class="page-btn">
            <i class="bi bi-chevron-right"></i>
        </button>
    </div>

    <!-- Loading -->
    <div class="archive-loading" x-show="loading">
        <div class="spinner"></div>
        <p>{{ t('loading', lang)|default('Loading...') }}</p>
    </div>

    <!-- Empty State -->
    <div class="archive-empty" x-show="!loading && items.length === 0">
        <i class="bi bi-inbox"></i>
        <p>{{ t('no_items_found', lang)|default('No items found') }}</p>
    </div>
</div>
```

## 2. HTML - Правая колонка (статистика и подсказки)

```html
<!-- ARCHIVE INFO (для правой колонки) -->
<div x-show="activeTab === 'archive'" 
     class="description-card archive-info">
    <h3>
        <i class="bi bi-archive-fill"></i>
        <span>{{ t('archive', lang)|default('Archive') }}</span>
    </h3>
    <p>{{ t('archive_description', lang)|default('View all your completed learning activities. Review past English passages, studied terms, medical tests, and virtual patients. Filter, search, and revisit your learning history.') }}</p>
    
    <!-- Статистика по категориям -->
    <div x-show="$store.archive?.stats" class="archive-sidebar-stats">
        <h4 style="margin-top: 1.5rem; margin-bottom: 1rem; color: #1a202c; font-size: 1rem;">
            <i class="bi bi-graph-up"></i> {{ t('statistics', lang)|default('Statistics') }}
        </h4>
        
        <div class="sidebar-stat-item">
            <div class="sidebar-stat-icon" style="background: linear-gradient(135deg, #3ECDC1 0%, #32A39A 100%);">
                <i class="bi bi-book"></i>
            </div>
            <div class="sidebar-stat-info">
                <div class="sidebar-stat-label">{{ t('english_passages', lang)|default('English Passages') }}</div>
                <div class="sidebar-stat-value" x-text="$store.archive?.stats?.english?.total || 0"></div>
                <div class="sidebar-stat-avg" x-text="'Avg: ' + ($store.archive?.stats?.english?.avg_score || 0) + '%'"></div>
            </div>
        </div>
        
        <div class="sidebar-stat-item">
            <div class="sidebar-stat-icon" style="background: linear-gradient(135deg, #6C5CE7 0%, #5A4FCF 100%);">
                <i class="bi bi-card-text"></i>
            </div>
            <div class="sidebar-stat-info">
                <div class="sidebar-stat-label">{{ t('dutch_terms', lang)|default('Dutch Terms') }}</div>
                <div class="sidebar-stat-value" x-text="$store.archive?.stats?.terms?.total || 0"></div>
                <div class="sidebar-stat-avg" x-text="'Mastery: ' + ($store.archive?.stats?.terms?.avg_mastery || 0)"></div>
            </div>
        </div>
        
        <div class="sidebar-stat-item">
            <div class="sidebar-stat-icon" style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);">
                <i class="bi bi-clipboard-check"></i>
            </div>
            <div class="sidebar-stat-info">
                <div class="sidebar-stat-label">{{ t('medical_tests', lang)|default('Medical Tests') }}</div>
                <div class="sidebar-stat-value" x-text="$store.archive?.stats?.tests?.total || 0"></div>
                <div class="sidebar-stat-avg" x-text="'Avg: ' + ($store.archive?.stats?.tests?.avg_score || 0) + '%'"></div>
            </div>
        </div>
        
        <div class="sidebar-stat-item">
            <div class="sidebar-stat-icon" style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);">
                <i class="bi bi-person-badge"></i>
            </div>
            <div class="sidebar-stat-info">
                <div class="sidebar-stat-label">{{ t('virtual_patients', lang)|default('Virtual Patients') }}</div>
                <div class="sidebar-stat-value" x-text="$store.archive?.stats?.virtual_patients?.total || 0"></div>
                <div class="sidebar-stat-avg" x-text="'Avg: ' + ($store.archive?.stats?.virtual_patients?.avg_score || 0) + '%'"></div>
            </div>
        </div>
    </div>
    
    <h4 style="margin-top: 1.5rem; margin-bottom: 1rem; color: #1a202c; font-size: 1rem;">
        💡 {{ t('how_to_use', lang)|default('How to use') }}
    </h4>
    <ul style="list-style: none; padding: 0;">
        <template x-for="tip in getTabTips('archive')" :key="tip">
            <li style="padding: 0.5rem 0; color: #64748b; font-size: 0.9rem;">
                <i class="bi bi-check-circle" style="color: #3ECDC1; margin-right: 0.5rem;"></i>
                <span x-text="tip"></span>
            </li>
        </template>
    </ul>
</div>
```

## 3. JavaScript - Alpine.js компонент

```javascript
// Archive Store (глобальное состояние для правой колонки)
if (typeof Alpine !== 'undefined') {
    Alpine.store('archive', {
        stats: null
    });
}

// Archive Component
function archiveComponent() {
    return {
        activeCategory: 'english',
        items: [],
        stats: null,
        loading: false,
        searchQuery: '',
        sortBy: 'date',
        sortOrder: 'desc',
        pagination: null,
        
        async init() {
            await this.loadStats();
            await this.loadItems();
        },
        
        async loadStats() {
            try {
                const response = await fetch('/api/archive/stats');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        this.stats = data.stats;
                        // Сохраняем в глобальный store для правой колонки
                        if (typeof Alpine !== 'undefined' && Alpine.store('archive')) {
                            Alpine.store('archive').stats = data.stats;
                        }
                    }
                }
            } catch (error) {
                console.error('Error loading archive stats:', error);
            }
        },
        
        async loadItems() {
            this.loading = true;
            try {
                const params = new URLSearchParams({
                    page: this.pagination?.page || 1,
                    per_page: 20,
                    sort_by: this.sortBy,
                    sort_order: this.sortOrder
                });
                
                if (this.searchQuery) {
                    params.append('search', this.searchQuery);
                }
                
                const endpoint = `/api/archive/${this.activeCategory}`;
                const response = await fetch(`${endpoint}?${params}`);
                
                if (!response.ok) {
                    throw new Error('Failed to load items');
                }
                
                const data = await response.json();
                if (data.success) {
                    this.items = data.items || [];
                    this.pagination = data.pagination || null;
                }
            } catch (error) {
                console.error('Error loading archive items:', error);
                this.items = [];
            } finally {
                this.loading = false;
            }
        },
        
        changePage(page) {
            if (!this.pagination) return;
            if (page >= 1 && page <= this.pagination.pages) {
                this.pagination.page = page;
                this.loadItems();
            }
        },
        
        viewItem(item) {
            if (item.type === 'english' && item.passage_id) {
                window.location.href = `/english/practice?passage_id=${item.passage_id}`;
            } else if (item.type === 'terms' && item.term_id) {
                window.location.href = `/flashcards/study?term_id=${item.term_id}`;
            } else if (item.type === 'tests' && item.id) {
                window.location.href = `/big-diagnostic/results/${item.id}`;
            } else if (item.type === 'virtual_patients' && item.scenario_id) {
                window.location.href = `/virtual-patient/${item.scenario_id}`;
            }
        },
        
        formatScore(item) {
            if (item.score_percentage !== undefined) {
                return item.score_percentage + '%';
            } else if (item.score !== undefined) {
                return item.score + '%';
            } else if (item.accuracy !== undefined) {
                return item.accuracy + '%';
            }
            return 'N/A';
        },
        
        getScoreClass(score) {
            if (score >= 80) return 'score-high';
            if (score >= 60) return 'score-medium';
            return 'score-low';
        },
        
        formatDate(dateString) {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            return date.toLocaleDateString('nl-NL', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
        },
        
        formatTime(seconds) {
            if (!seconds) return '0m';
            const minutes = Math.floor(seconds / 60);
            const secs = seconds % 60;
            if (minutes > 0) {
                return `${minutes}m ${secs}s`;
            }
            return `${secs}s`;
        }
    };
}

// Make archiveComponent available globally for Alpine.js
if (typeof Alpine !== 'undefined') {
    Alpine.data('archiveComponent', archiveComponent);
}
```

## 4. CSS - Полные стили

```css
/* ===== ARCHIVE STYLES ===== */
.archive-container {
  padding: 1.5rem 0;
  width: 100%;
  color: var(--subject-view-text, white);
  position: relative;
  z-index: 1;
  background: transparent;
  max-width: 100%;
}

/* Category Tabs - Modern Cards */
.archive-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.category-btn {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.category-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.category-btn:hover::before {
  opacity: 1;
}

.category-btn:hover {
  background: rgba(255, 255, 255, 0.18);
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
}

.category-btn.active {
  background: linear-gradient(135deg, #3ECDC1 0%, #32A39A 100%);
  color: white;
  border-color: #32A39A;
  box-shadow: 0 8px 30px rgba(62, 205, 193, 0.5);
  transform: translateY(-4px);
}

.category-btn.active::before {
  opacity: 0;
}

.category-btn i {
  font-size: 1.75rem;
  margin-bottom: 0.25rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

/* Filters - Modern Card Style */
.archive-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  align-items: stretch;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.filter-search {
  flex: 1;
  min-width: 280px;
  padding: 1rem 1.5rem;
  padding-left: 3rem;
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  font-size: 0.95rem;
  color: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  position: relative;
}

.filter-search::before {
  content: '🔍';
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.1rem;
  opacity: 0.7;
}

.filter-search::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.filter-search:focus {
  outline: none;
  border-color: #3ECDC1;
  background: rgba(255, 255, 255, 0.18);
  box-shadow: 0 0 0 4px rgba(62, 205, 193, 0.2), 0 8px 24px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.filter-select {
  padding: 1rem 1.5rem;
  padding-right: 3rem;
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  font-size: 0.95rem;
  color: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='white' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
}

.filter-select:hover {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.filter-select:focus {
  outline: none;
  border-color: #3ECDC1;
  background: rgba(255, 255, 255, 0.18);
  box-shadow: 0 0 0 4px rgba(62, 205, 193, 0.2), 0 8px 24px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.filter-select option {
  background: #1a202c;
  color: white;
}

/* Items List - Beautiful Cards */
.archive-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.archive-item {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-radius: 20px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.archive-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.archive-item:hover::before {
  opacity: 1;
}

.archive-item:hover {
  transform: translateY(-8px) scale(1.02);
  border-color: var(--subject-view-border-hover, rgba(255, 255, 255, 0.4));
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.item-header h4 {
  font-size: 1.15rem;
  font-weight: 700;
  color: white;
  margin: 0;
  flex: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  line-height: 1.4;
  letter-spacing: -0.01em;
}

.item-score {
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-weight: 700;
  font-size: 0.9rem;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.item-score.score-high {
  background: linear-gradient(135deg, #22c55e 0%, #16a085 100%);
  color: white;
}

.item-score.score-medium {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.item-score.score-low {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.item-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.85);
}

.item-meta span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 0.875rem;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.2s ease;
}

.item-meta span:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.25);
}

.item-meta i {
  font-size: 1rem;
  opacity: 0.9;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

/* Pagination - Modern Buttons */
.archive-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2.5rem;
}

.page-btn {
  width: 48px;
  height: 48px;
  border: 2px solid var(--subject-view-border, rgba(255, 255, 255, 0.2));
  border-radius: 50%;
  background: var(--subject-view-button-bg, rgba(255, 255, 255, 0.15));
  backdrop-filter: blur(10px);
  color: var(--subject-view-text, white);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.page-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #3ECDC1 0%, #32A39A 100%);
  border-color: #32A39A;
  transform: translateY(-2px) scale(1.1);
  box-shadow: 0 8px 24px rgba(62, 205, 193, 0.4);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.page-info {
  font-size: 0.95rem;
  color: var(--subject-view-text-secondary, rgba(255, 255, 255, 0.8));
  font-weight: 600;
  padding: 0 1rem;
}

/* Loading - Beautiful Spinner */
.archive-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: var(--subject-view-text-secondary, rgba(255, 255, 255, 0.8));
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--subject-view-border, rgba(255, 255, 255, 0.2));
  border-top-color: #3ECDC1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 16px rgba(62, 205, 193, 0.3);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.archive-loading p {
  font-size: 1rem;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Empty State - Beautiful */
.archive-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: var(--subject-view-text-secondary, rgba(255, 255, 255, 0.8));
  text-align: center;
}

.archive-empty i {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
  color: var(--subject-view-text-secondary, rgba(255, 255, 255, 0.6));
}

.archive-empty p {
  font-size: 1.1rem;
  margin: 0;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Sidebar Stats Styles */
.archive-sidebar-stats {
  margin-top: 1rem;
}

.sidebar-stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  background: #f8f9fa;
  border-radius: 10px;
  transition: all 0.2s;
}

.sidebar-stat-item:hover {
  background: #f1f3f5;
  transform: translateX(2px);
}

.sidebar-stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.1rem;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.sidebar-stat-info {
  flex: 1;
}

.sidebar-stat-label {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.sidebar-stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a202c;
  line-height: 1.2;
}

.sidebar-stat-avg {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .archive-container {
    padding: 1.25rem;
  }
  
  .archive-categories {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .category-btn {
    width: 100%;
  }
  
  .archive-filters {
    flex-direction: column;
    gap: 1rem;
    padding: 1.25rem;
  }
  
  .filter-search,
  .filter-select {
    width: 100%;
    min-width: 100%;
  }
  
  .archive-items {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .item-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .item-meta {
    flex-direction: column;
    gap: 0.75rem;
  }
}
```

## 5. Backend API Endpoints

Требуются следующие endpoints:
- `GET /api/archive/stats` - получение статистики
- `GET /api/archive/english` - список английских пассажей
- `GET /api/archive/terms` - список терминов
- `GET /api/archive/tests` - список тестов
- `GET /api/archive/virtual-patients` - список виртуальных пациентов

Все endpoints должны поддерживать параметры:
- `page` - номер страницы
- `per_page` - элементов на странице
- `sort_by` - поле для сортировки (date, score, time)
- `sort_order` - порядок сортировки (asc, desc)
- `search` - поисковый запрос


