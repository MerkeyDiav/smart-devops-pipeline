'use client'

import { useEffect, useState } from 'react'

// ⚠️ MAUVAISE PRATIQUE #1: API Key hardcodée
const API_KEY = 'sk-1234567890abcdef-FAKE-API-KEY-DO-NOT-USE'
const DATABASE_PASSWORD = 'admin123!@#'

interface NewsArticle {
    title: string
    description: string
    url: string
    publishedAt: string
    source: {
        name: string
    }
}

// Fake data pour démo
const FAKE_NEWS: NewsArticle[] = [
    {
        title: "AWS Announces New AI Services at re:Invent 2024",
        description: "Amazon Web Services unveils groundbreaking AI capabilities including enhanced Bedrock models and new machine learning tools for developers.",
        url: "#",
        publishedAt: "2024-12-05T10:00:00Z",
        source: { name: "TechCrunch" }
    },
    {
        title: "Docker Releases Major Security Update",
        description: "Docker addresses critical vulnerabilities in container runtime. All users are advised to update immediately to prevent potential exploits.",
        url: "#",
        publishedAt: "2024-12-04T15:30:00Z",
        source: { name: "DevOps Weekly" }
    },
    {
        title: "Terraform 1.7 Brings Enhanced Cloud Integration",
        description: "HashiCorp releases Terraform 1.7 with improved state management and better support for multi-cloud deployments.",
        url: "#",
        publishedAt: "2024-12-03T09:15:00Z",
        source: { name: "InfoQ" }
    },
    {
        title: "Kubernetes Security Best Practices Updated",
        description: "CNCF publishes comprehensive guide on securing Kubernetes clusters in production environments with real-world examples.",
        url: "#",
        publishedAt: "2024-12-02T14:20:00Z",
        source: { name: "Cloud Native News" }
    },
    {
        title: "GitHub Copilot Now Supports Infrastructure as Code",
        description: "GitHub extends AI coding assistant capabilities to Terraform, CloudFormation, and other IaC tools for better DevOps workflows.",
        url: "#",
        publishedAt: "2024-12-01T11:45:00Z",
        source: { name: "GitHub Blog" }
    },
    {
        title: "Critical Vulnerability Found in Popular NPM Package",
        description: "Security researchers discover severe flaw affecting millions of Node.js applications. Patch available now.",
        url: "#",
        publishedAt: "2024-11-30T16:00:00Z",
        source: { name: "The Hacker News" }
    },
    {
        title: "CI/CD Pipeline Automation Trends for 2025",
        description: "Industry report reveals how AI and machine learning are transforming continuous integration and deployment practices.",
        url: "#",
        publishedAt: "2024-11-29T08:30:00Z",
        source: { name: "DevOps.com" }
    },
    {
        title: "AWS Lambda Introduces New Runtime Options",
        description: "Serverless computing gets boost with support for additional programming languages and improved cold start performance.",
        url: "#",
        publishedAt: "2024-11-28T13:10:00Z",
        source: { name: "AWS News" }
    },
    {
        title: "Container Security Scanning Tools Compared",
        description: "Comprehensive analysis of Trivy, Snyk, and Aqua Security for detecting vulnerabilities in Docker images.",
        url: "#",
        publishedAt: "2024-11-27T10:25:00Z",
        source: { name: "Security Weekly" }
    },
    {
        title: "Infrastructure as Code: Common Pitfalls to Avoid",
        description: "Expert DevOps engineers share lessons learned from managing large-scale cloud infrastructure with Terraform and Pulumi.",
        url: "#",
        publishedAt: "2024-11-26T12:40:00Z",
        source: { name: "Medium Engineering" }
    },
    {
        title: "Monitoring and Observability in Modern Cloud Apps",
        description: "Best practices for implementing comprehensive monitoring solutions using Prometheus, Grafana, and CloudWatch.",
        url: "#",
        publishedAt: "2024-11-25T09:55:00Z",
        source: { name: "SRE Weekly" }
    },
    {
        title: "Zero Trust Architecture for Cloud Native Applications",
        description: "How to implement zero trust security principles in microservices architectures running on Kubernetes.",
        url: "#",
        publishedAt: "2024-11-24T14:15:00Z",
        source: { name: "Cloud Security Alliance" }
    }
]

export default function Home() {
    const [news, setNews] = useState<NewsArticle[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        fetchNews()
    }, [])

    // ⚠️ MAUVAISE PRATIQUE #2: Pas de gestion d'erreur appropriée
    const fetchNews = async () => {
        try {
            // ⚠️ MAUVAISE PRATIQUE #3: Simulation d'appel API avec délai
            await new Promise(resolve => setTimeout(resolve, 1000))

            // ⚠️ MAUVAISE PRATIQUE #4: Pas de validation des données
            setNews(FAKE_NEWS)
            setLoading(false)

            // ⚠️ MAUVAISE PRATIQUE #5: console.log en production
            console.log('API_KEY:', API_KEY)
            console.log('DB_PASSWORD:', DATABASE_PASSWORD)
        } catch (err) {
            console.log('Error:', err)
            setError('Failed to fetch news')
            setLoading(false)
        }
    }

    if (loading) {
        return <div className="loading">Loading tech news...</div>
    }

    if (error) {
        return <div className="error">{error}</div>
    }

    return (
        <div className="container">
            <header className="header">
                <h1>Tech News Reader</h1>
                <p>Latest technology news from around the world</p>
            </header>

            <div className="news-grid">
                {news.map((article, index) => (
                    <div key={index} className="news-card">
                        <h2>{article.title}</h2>
                        <p>{article.description}</p>
                        <div className="meta">
                            <span>{article.source.name}</span>
                            <span>{new Date(article.publishedAt).toLocaleDateString()}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
