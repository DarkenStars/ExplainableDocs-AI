<template>
  <div class="landing-page">
    <NavBar />

    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-headline fade-in-up">Clarity in a world of noise.</h1>
        <p class="hero-subheadline fade-in-up" style="animation-delay: 0.2s;">
          Our advanced AI system analyzes claims, verifies facts, and provides 
          evidence-based verdicts to help you distinguish truth from misinformation in real-time.
        </p>
        <div class="hero-buttons fade-in-up" style="animation-delay: 0.4s;">
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
        <div class="sliding-container">
          <div class="sliding-track">
            <div class="demo-card"><div class="verdict-false">FALSE</div><span>Vaccines contain microchips for tracking.</span></div>
            <div class="demo-card"><div class="verdict-true">TRUE</div><span>The Earth revolves around the Sun.</span></div>
            <div class="demo-card"><div class="verdict-false">FALSE</div><span>5G networks spread viruses.</span></div>
            <div class="demo-card"><div class="verdict-uncertain">UNCERTAIN</div><span>Coffee reduces the risk of diabetes.</span></div>
            <div class="demo-card"><div class="verdict-true">TRUE</div><span>EVs reduce overall carbon emissions.</span></div>
            
            <div class="demo-card"><div class="verdict-false">FALSE</div><span>Vaccines contain microchips for tracking.</span></div>
            <div class="demo-card"><div class="verdict-true">TRUE</div><span>The Earth revolves around the Sun.</span></div>
            <div class="demo-card"><div class="verdict-false">FALSE</div><span>5G networks spread viruses.</span></div>
            <div class="demo-card"><div class="verdict-uncertain">UNCERTAIN</div><span>Coffee reduces the risk of diabetes.</span></div>
            <div class="demo-card"><div class="verdict-true">TRUE</div><span>EVs reduce overall carbon emissions.</span></div>
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
/* Subtle fade-in animation */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-up {
  animation: fadeInUp 0.8s ease-out forwards;
}

.landing-page { padding-top: 80px; }

/* Hero Section */
.hero { text-align: center; padding: 6rem 2rem 4rem; }
.hero-content { max-width: 750px; margin: 0 auto; }
.hero-headline { font-size: 3.5rem; font-weight: 700; margin-bottom: 1.5rem; }
.hero-subheadline { font-size: 1.25rem; color: var(--color-text-secondary); margin-bottom: 2.5rem; line-height: 1.7; max-width: 600px; margin-left: auto; margin-right: auto; }
.hero-buttons { display: flex; gap: 1rem; justify-content: center; }

/* Sliding Demo Section */
@keyframes slide {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}
.sliding-container {
  overflow: hidden;
  padding: 2rem 0;
  position: relative;
  width: 100%;
}
.sliding-container::before, .sliding-container::after {
  content: '';
  position: absolute;
  top: 0;
  width: 150px;
  height: 100%;
  z-index: 2;
}
.sliding-container::before {
  left: 0;
  background: linear-gradient(to right, var(--color-background) 20%, transparent 100%);
}
.sliding-container::after {
  right: 0;
  background: linear-gradient(to left, var(--color-background) 20%, transparent 100%);
}
.sliding-track {
  display: flex;
  width: calc(350px * 10);
  animation: slide 60s linear infinite;
}
.demo-card {
  width: 300px;
  margin: 0 25px;
  flex-shrink: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
body.dark-theme .demo-card {
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.demo-card span {
  font-size: 1rem;
  color: var(--color-text-primary);
  display: block;
}
.verdict-false, .verdict-true, .verdict-uncertain {
  font-weight: 600;
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
  display: inline-block;
}
.verdict-false { color: #D92D20; }
.verdict-true { color: #059669; }
.verdict-uncertain { color: #D97706; }

/* Features Section */
.features { padding: 6rem 2rem; background: var(--color-surface); text-align: center; }
.section-title { font-size: 2.5rem; margin-bottom: 3rem; max-width: 500px; margin-left: auto; margin-right: auto; }
.features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; max-width: 1100px; margin: 0 auto; text-align: left; }
.feature-card h3 { font-size: 1.25rem; margin-bottom: 0.5rem; }
.feature-card p { color: var(--color-text-secondary); }

/* CTA Section */
.cta-section { text-align: center; padding: 6rem 2rem; }
.cta-section h2 { font-size: 2.5rem; margin-bottom: 1rem; }
.cta-section p { font-size: 1.1rem; color: var(--color-text-secondary); margin-bottom: 2rem; }

/* Responsive */
@media (max-width: 768px) {
  .hero-headline { font-size: 2.5rem; }
  .section-title, .cta-section h2 { font-size: 2rem; }
}
</style>