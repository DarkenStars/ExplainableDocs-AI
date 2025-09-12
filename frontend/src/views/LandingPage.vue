<template>
  <div class="landing-page">
    <!-- Abstract Background -->
    <div class="abstract-background">
      <div class="abstract-shape"></div>
      <div class="abstract-shape"></div>
      <div class="abstract-shape"></div>
      <div class="abstract-shape"></div>
      <div class="abstract-shape"></div>
    </div>

    <!-- Navigation -->
    <NavBar />

    <!-- Hero Section -->
    <section class="hero fade-in">
      <div class="hero-content">
        <div class="hero-text">
          <h1>Combat Misinformation with AI-Powered Fact Checking</h1>
          <p>
            Our advanced AI system analyzes claims, verifies facts, and provides 
            evidence-based verdicts to help you distinguish truth from misinformation 
            in real-time.
          </p>
          <div class="hero-buttons">
            <router-link to="/chat" class="btn btn-primary">
              Start Fact Checking →
            </router-link>
            <button @click="scrollToFeatures" class="btn btn-secondary">
              ▶️ Watch Demo
            </button>
          </div>
        </div>
        
        <div class="hero-demo">
          <div class="demo-container glass-card">
            <div class="demo-header">
              <div class="demo-dots">
                <div class="demo-dot"></div>
                <div class="demo-dot"></div>
                <div class="demo-dot"></div>
              </div>
            </div>
            <div class="demo-content">
              <div class="demo-message user bounce-in">
                "Vaccines contain microchips for tracking"
              </div>
              <div class="demo-message ai slide-in">
                <div class="verdict-badge verdict-false">FALSE</div>
                <div class="confidence-badge confidence-high">95% Confident</div>
                <p style="margin-top: 1rem; opacity: 0.9;">
                  No credible evidence supports this claim. Multiple health organizations 
                  have verified vaccine safety.
                </p>
                <div style="margin-top: 1rem;">
                  <small style="opacity: 0.7;">
                    🔗 Sources: WHO, CDC, Reuters
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="features">
      <div class="container">
        <h2 class="section-title">Powerful Features</h2>
        <div class="features-grid">
          <div class="feature-card glass-card fade-in">
            <div class="feature-icon" style="background: var(--gradient-primary);">
              🔍
            </div>
            <h3>AI-Powered Analysis</h3>
            <p>Advanced NLP models analyze claims against verified databases from trusted sources worldwide</p>
          </div>
          
          <div class="feature-card glass-card fade-in">
            <div class="feature-icon" style="background: var(--gradient-secondary);">
              🛡️
            </div>
            <h3>Real-time Verification</h3>
            <p>Get instant fact-check results with detailed confidence scores and evidence explanations</p>
          </div>
          
          <div class="feature-card glass-card fade-in">
            <div class="feature-icon" style="background: var(--gradient-warm);">
              🖼️
            </div>
            <h3>Image Analysis</h3>
            <p>Upload images for authenticity verification and detect manipulated visual content</p>
          </div>
          
          <div class="feature-card glass-card fade-in">
            <div class="feature-icon" style="background: var(--gradient-danger);">
              🔗
            </div>
            <h3>Credible Sources</h3>
            <p>Evidence linked to trusted organizations: WHO, CDC, Snopes, PolitiFact, and more</p>
          </div>
          
          <div class="feature-card glass-card fade-in">
            <div class="feature-icon" style="background: linear-gradient(135deg, var(--primary-pink) 0%, var(--primary-purple) 100%);">
              💬
            </div>
            <h3>Chat Interface</h3>
            <p>Natural conversation flow with persistent history and intelligent context understanding</p>
          </div>
          
          <div class="feature-card glass-card fade-in">
            <div class="feature-icon" style="background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--primary-blue) 100%);">
              📱
            </div>
            <h3>Multi-Platform</h3>
            <p>Access via web, WhatsApp bot, or Telegram bot for seamless fact-checking anywhere</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card glass-card">
          <h2>Ready to Fight Misinformation?</h2>
          <p>Join thousands of users who trust News Advisor AI for accurate, evidence-based fact-checking</p>
          <router-link to="/chat" class="btn btn-primary" style="font-size: 1.1rem; padding: 1rem 2rem;">
            ⚡ Start Your First Fact Check
          </router-link>
          
          <div class="stats-row" style="margin-top: 2rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div class="stat-item">
              <div class="stat-number gradient-text">10K+</div>
              <div class="stat-label">Claims Verified</div>
            </div>
            <div class="stat-item">
              <div class="stat-number gradient-text">95%</div>
              <div class="stat-label">Accuracy Rate</div>
            </div>
            <div class="stat-item">
              <div class="stat-number gradient-text">&lt;3s</div>
              <div class="stat-label">Response Time</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import NavBar from '../components/NavBar.vue'

export default {
  name: 'LandingPage',
  components: {
    NavBar
  },
  setup() {
    const scrollToFeatures = () => {
      document.getElementById('features')?.scrollIntoView({ 
        behavior: 'smooth' 
      })
    }
    
    return {
      scrollToFeatures
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .stats-row {
    gap: 1rem !important;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
}
</style>
