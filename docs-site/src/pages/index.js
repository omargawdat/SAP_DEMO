import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HeroBanner() {
  return (
    <header className={styles.heroBanner}>
      <div className="container">
        <Heading as="h1" className={styles.heroTitle}>
          🛡️ PII Shield
        </Heading>
        <p className={styles.heroSubtitle}>
          German PII Detection & De-identification
        </p>
        <div className={styles.stats}>
          <div className={styles.stat}>
            <span className={styles.statNumber}>8</span>
            <span className={styles.statLabel}>Detectors</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statNumber}>3</span>
            <span className={styles.statLabel}>Strategies</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statNumber}>🇩🇪</span>
            <span className={styles.statLabel}>German Focus</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statNumber}>🤖</span>
            <span className={styles.statLabel}>LLM Enhanced</span>
          </div>
        </div>
        <div className={styles.buttons}>
          <Link className="button button--primary button--lg" to="/docs">
            📚 Documentation
          </Link>
          <Link
            className="button button--secondary button--lg"
            href="https://sap-pii-shield.streamlit.app">
            🚀 Live Demo
          </Link>
        </div>
      </div>
    </header>
  );
}

const features = [
  {
    title: 'German Validation',
    icon: '🇩🇪',
    items: [
      'IBAN with MOD-97 checksum',
      'Personalausweis check digit',
      'German phone formats (+49)',
    ],
  },
  {
    title: 'Hybrid AI Detection',
    icon: '🤖',
    items: [
      'Rule-based (fast, precise)',
      'ML/NER with German spaCy',
      'Claude LLM validation',
    ],
  },
  {
    title: 'De-identification',
    icon: '🛡️',
    items: [
      'Redaction: [EMAIL]',
      'Masking: han***com',
      'Hashing: SHA-256 + salt',
    ],
  },
];

function FeatureCard({ title, icon, items }) {
  return (
    <div className={styles.featureCard}>
      <div className={styles.featureIcon}>{icon}</div>
      <Heading as="h3" className={styles.featureTitle}>{title}</Heading>
      <ul className={styles.featureList}>
        {items.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function FeaturesSection() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.featureGrid}>
          {features.map((props, idx) => (
            <FeatureCard key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

function TechBadges() {
  return (
    <section className={styles.techSection}>
      <div className="container">
        <div className={styles.badges}>
          <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white" alt="Python" />
          <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
          <img src="https://img.shields.io/badge/Presidio-ML-purple" alt="Presidio" />
          <img src="https://img.shields.io/badge/Claude-AI-black?logo=anthropic" alt="Claude" />
          <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker" />
          <img src="https://img.shields.io/badge/AWS_ECR-FF9900?logo=amazon-aws&logoColor=white" alt="AWS ECR" />
          <img src="https://img.shields.io/badge/Secrets_Manager-DD344C?logo=amazon-aws&logoColor=white" alt="AWS Secrets Manager" />
          <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white" alt="GitHub Actions" />
        </div>
      </div>
    </section>
  );
}

function SAPSection() {
  return (
    <section className={styles.sapSection}>
      <div className="container">
        <div className={styles.sapCard}>
          <Heading as="h2">🎯 Built for SAP EDT Data Protection</Heading>
          <p>
            This project demonstrates skills for the <strong>Working Student - Provisioning of de-identification services</strong> role:
          </p>
          <div className={styles.sapGrid}>
            <div>✅ Python + Cloud Development</div>
            <div>✅ German/EU Data Protection</div>
            <div>✅ ML/LLM Integration</div>
            <div>✅ Production-Ready Code</div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title="German PII Detection"
      description="Production-ready PII detection and de-identification for German data protection and GDPR compliance.">
      <HeroBanner />
      <main>
        <FeaturesSection />
        <TechBadges />
        <SAPSection />
      </main>
    </Layout>
  );
}
