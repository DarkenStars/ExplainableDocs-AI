<template>
  <div class="landing-page">
    <NavBar />

    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-headline">Clarity in a world of noise.</h1>
        <p class="hero-subheadline">
          Our advanced AI system analyzes claims, verifies facts, and provides 
          evidence-based verdicts to help you distinguish truth from misinformation in real-time.
        </p>
        <div class="hero-buttons">
          <router-link to="/chat" class="btn btn-primary">
            Start Fact-Checking
          </router-link>
          <button @click="scrollToFeatures" class="btn btn-secondary">
            Learn More
          </button>
        </div>
      </div>
    </section>

    <section class="demo-section">
        <div class="demo-container">
            <div class="demo-header">
                <div class="demo-dots">
                    <div class="demo-dot"></div>
                    <div class="demo-dot"></div>
                    <div class="demo-dot"></div>
                </div>
            </div>
            <div class="demo-content">
                <div class="demo-message user">
                    "Vaccines contain microchips for tracking"
                </div>
                <div class="demo-message ai">
                    <div class="verdict-false">VERDICT: FALSE</div>
                    <p>No credible evidence supports this claim. Multiple health organizations have verified vaccine safety. Sources include the WHO and CDC.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="features" class="features">
      <div class="container">
        <h2 class="section-title">Powerful, transparent, and easy to use.</h2>
        <div class="features-grid">
          <div class="feature-card">
            <h3>AI-Powered Analysis</h3>
            <p>Advanced models analyze claims against verified databases from trusted sources worldwide.</p>
          </div>
          <div class="feature-card">
            <h3>Real-time Verification</h3>
            <p>Get instant fact-check results with detailed confidence scores and clear explanations.</p>
          </div>
          <div class="feature-card">
            <h3>Credible Sources</h3>
            <p>Evidence is always linked to trusted organizations like WHO, CDC, Snopes, PolitiFact, and more.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-section">
      <div class="container">
        <h2>Ready to find clarity?</h2>
        <p>Join thousands of users who trust News Advisor AI for accurate, evidence-based fact-checking.</p>
        <router-link to="/chat" class="btn btn-primary">
          Start Your First Fact-Check
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue';

const scrollToFeatures = () => {
  document.getElementById('features')?.scrollIntoView({ 
    behavior: 'smooth' 
  });
};
</script>

<style scoped>
.landing-page {
  padding-top: 80px; /* Space for the fixed navbar */
}

/* Hero Section */
.hero {
  text-align: center;
  padding: 6rem 2rem 4rem;
}

.hero-content {
  max-width: 750px;
  margin: 0 auto;
}

.hero-headline {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.hero-subheadline {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  margin-bottom: 2.5rem;
  line-height: 1.7;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

/* Demo Section */
.demo-section {
  padding: 2rem;
}
.demo-container {
  max-width: 700px;
  margin: 0 auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  background: var(--color-background);
}
body.dark-theme .demo-container {
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.demo-header {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}
.demo-dots {
  display: flex;
  gap: 0.5rem;
}
.demo-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--color-subtle);
}
.demo-content {
  padding: 1.5rem;
  font-size: 0.95rem;
}
.demo-message {
  margin-bottom: 1rem;
}
.demo-message.user {
  font-weight: 500;
  color: var(--color-text-primary);
}
.demo-message.ai {
  color: var(--color-text-secondary);
}
.verdict-false {
  font-weight: 600;
  color: #D92D20;
  margin-bottom: 0.5rem;
}

/* Features Section */
.features {
  padding: 6rem 2rem;
  background: var(--color-surface);
  text-align: center;
}

.section-title {
  font-size: 2.5rem;
  margin-bottom: 3rem;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1100px;
  margin: 0 auto;
  text-align: left;
}

.feature-card h3 {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: var(--color-text-secondary);
}

/* CTA Section */
.cta-section {
  text-align: center;
  padding: 6rem 2rem;
}

.cta-section h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.cta-section p {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin-bottom: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .hero-headline { font-size: 2.5rem; }
  .section-title { font-size: 2rem; }
  .cta-section h2 { font-size: 2rem; }
}
</style>