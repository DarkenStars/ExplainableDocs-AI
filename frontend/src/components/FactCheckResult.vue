<template>
  <div class="fact-check-result">
    <header class="result-header">
      <div class="verdict-badge" :class="`verdict-${result.verdict.toLowerCase()}`">
        {{ result.verdict.toUpperCase() }}
      </div>
      <div class="confidence-badge" :class="getConfidenceClass(result.confidence)">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        {{ result.confidence }}% Confident
      </div>
    </header>
    
    <div class="result-explanation">
      <p>{{ result.explanation }}</p>
    </div>
    
    <div v-if="result.sources && result.sources.length" class="result-sources">
      <h4>Sources</h4>
      <ul class="source-list">
        <li v-for="source in result.sources" :key="source.id" class="source-item">
          <a :href="source.url" target="_blank" rel="noopener noreferrer" class="source-link">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.72"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.72-1.72"></path></svg>
            {{ source.title }}
            <span v-if="source.organization" class="source-org">
              {{ source.organization }}
            </span>
          </a>
        </li>
      </ul>
    </div>
    
    <footer v-if="result.processing_time" class="result-footer">
      <span>⚡ Analyzed in {{ result.processing_time.toFixed(1) }}s</span>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'FactCheckResult',
  props: {
    result: {
      type: Object,
      required: true
    }
  },
  setup() {
    const getConfidenceClass = (confidence) => {
      if (confidence >= 80) return 'confidence-high'
      if (confidence >= 60) return 'confidence-medium'
      return 'confidence-low'
    }
    
    return {
      getConfidenceClass
    }
  }
}
</script>

<style scoped>
/* These styles use the variables from your main ChatApp for perfect consistency */
.fact-check-result {
  background-color: var(--color-sidebar-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  padding: 1.25rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.verdict-badge {
  padding: 0.3rem 0.85rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
  color: #FFFFFF;
  text-transform: uppercase;
}
.verdict-false { background-color: #EF4444; }
.verdict-true { background-color: #22C55E; }
.verdict-misleading { background-color: #F97316; }

.confidence-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.3rem 0.7rem;
  border-radius: 9999px;
}
.confidence-high { color: #16A34A; background-color: #F0FDF4; }
.confidence-medium { color: #CA8A04; background-color: #FEFCE8; }
.confidence-low { color: #DC2626; background-color: #FEF2F2; }

.result-explanation {
  margin-bottom: 1.5rem;
  line-height: 1.6;
  color: var(--color-text-body);
}

.result-sources h4 {
  margin-bottom: 0.75rem;
  color: var(--color-text-header);
  font-size: 0.9rem;
  font-weight: 600;
}

.source-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.source-link {
  color: var(--color-accent);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.source-link:hover {
  text-decoration: underline;
}

.source-org {
  color: var(--color-text-light);
  font-size: 0.8em;
  font-weight: 400;
  background-color: var(--color-bg);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  border: 1px solid var(--color-border);
}

.result-footer {
  margin-top: 1.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
  text-align: right;
  font-size: 0.8rem;
  color: var(--color-text-light);
}
</style>