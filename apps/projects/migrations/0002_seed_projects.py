"""Initial project list, taken only from the CV and facts confirmed by Atlantik.

Edit or extend these in the Django admin afterwards; this migration only inserts rows that don't exist yet.
Keep in sync with frontend/app/data/projects.ts (the static fallback used while the API is asleep).
"""
from django.db import migrations

PROJECTS = [
    {
        "slug": "pabau-clinic-crm",
        "title": "Pabau – Clinic CRM",
        "company": "Pabau Clinic Software",
        "role": "Software Engineer",
        "period": "Apr 2024 – Apr 2025",
        "summary": "All-in-one B2B practice-management CRM used by multiple clinics and medical spas. I worked across the whole stack.",
        "description": (
            "Pabau is practice-management software for clinics: clinical care, business operations and patient "
            "engagement in one platform. I led front-end efforts in React/Next.js and TypeScript and worked on the "
            "GraphQL layer with Hasura and NestJS resolvers, with Jest for testing."
        ),
        "highlights": [
            "Full-stack work: Next.js front end, GraphQL API with Hasura and NestJS resolvers",
            "Made complex clinic workflows feel simple for healthcare professionals",
            "Refined architectural decisions and mentored newer developers",
        ],
        "tech": ["Next.js", "React", "TypeScript", "GraphQL", "Hasura", "NestJS", "Jest"],
        "status": "live",
        "live_url": "https://pabau.com/",
        "featured": True,
        "order": 1,
    },
    {
        "slug": "learniverse",
        "title": "Learniverse",
        "company": "AnchorzUp (client project)",
        "role": "Frontend Developer",
        "period": "2026 – present",
        "summary": "AI-powered career-learning platform: personalised learning paths, interview simulations and workplace role-play.",
        "description": (
            "Client project at AnchorzUp. Learniverse helps students, job seekers and career changers build skills, "
            "prepare for interviews and practise workplace communication. I work on the platform and its web app."
        ),
        "highlights": [
            "Work on both learniverse.world and the app at app.learniverse.world",
            "SSR-first front-end architecture with Vue/Nuxt and TypeScript",
        ],
        "tech": ["Vue.js", "Nuxt", "TypeScript", "Pinia"],
        "status": "live",
        "live_url": "https://app.learniverse.world/",
        "featured": True,
        "order": 2,
    },
    {
        "slug": "hr-platform",
        "title": "Gamified HR Platform",
        "company": "AnchorzUp (internal product)",
        "role": "Frontend Developer",
        "period": "2026 – present",
        "summary": "Internal all-in-one HR app for companies: gamified tasks, trainings, time attendance and task evaluation.",
        "description": (
            "An all-in-one HR platform built at AnchorzUp that brings gamified tasks, trainings, time attendance "
            "and task evaluation together in a single product."
        ),
        "highlights": [
            "Gamified tasks and trainings",
            "Time attendance and task evaluation in one place",
            "Composition API, custom composables and Pinia for type-safe state",
        ],
        "tech": ["Vue.js", "Nuxt", "TypeScript", "Pinia"],
        "status": "in_development",
        "featured": True,
        "order": 3,
    },
    {
        "slug": "budget-forecasting",
        "title": "Budgeting & Forecasting App",
        "company": "Aralytiks (client project)",
        "role": "Frontend Developer",
        "period": "Jun 2025 – Feb 2026",
        "summary": "Budgeting and forecasting application for a high-end client, with full-year graphs and dashboards.",
        "description": (
            "Built for a high-end client at Aralytiks: yearly budget planning and forecasting with graphs for the "
            "whole year and interactive dashboards. The client and its data are confidential."
        ),
        "highlights": [
            "Full-year budget and forecast graphs",
            "Interactive dashboards",
            "Role-based access control, filtering, sorting and drag-and-drop",
        ],
        "tech": ["React", "TypeScript", "Refine.dev"],
        "status": "private",
        "featured": True,
        "order": 4,
    },
    {
        "slug": "eventkickoff",
        "title": "Eventkickoff",
        "company": "Eventkickoff",
        "role": "Developer",
        "period": "Aug 2023 – Jul 2024",
        "summary": "Social platform for discovering events and meeting like-minded people.",
        "description": (
            "Using Laravel, I revamped the user flow for event creation and registration and introduced features "
            "that supported a wider variety of event types and improved user retention."
        ),
        "highlights": [
            "Revamped event creation and registration flow",
            "New features for more event types and better retention",
        ],
        "tech": ["Laravel", "PHP"],
        "status": "live",
        "live_url": "https://eventkickoff.com/",
        "order": 5,
    },
    {
        "slug": "mybranda",
        "title": "myBranda",
        "company": "myBranda",
        "role": "Full Stack Developer",
        "period": "Jul 2023 – Jun 2024",
        "summary": "Helped scale the core product: React front end with Django backend work on bottlenecks and full-stack features.",
        "description": (
            "I built responsive React components and jumped into the Django backend to resolve bottlenecks and "
            "ship full-stack features, taking part in product and UX discussions. The business has since shut "
            "down, so the product is no longer online."
        ),
        "highlights": [
            "React front end, Django backend",
            "Product discussions, UX improvements and shipped updates",
        ],
        "tech": ["React", "Django", "Python"],
        "status": "offline",
        "order": 6,
    },
    {
        "slug": "portfolio-backend-lab",
        "title": "This Portfolio + Backend Lab",
        "company": "Personal project",
        "role": "Design & full-stack development",
        "period": "2026",
        "summary": "Static Nuxt site with a WebGL background and a live Django REST Framework API you can test in the browser.",
        "description": (
            "Nuxt + TypeScript + Tailwind front end deployed on Cloudflare Pages, and a Django 5 / DRF API on Render "
            "with PostgreSQL on Neon: contact form, projects, guestbook, cached analytics, JWT demo and OpenAPI docs."
        ),
        "highlights": [
            "Contact API with throttling and honeypot spam protection",
            "Interactive API explorer, JWT auth demo, Swagger docs",
            "Tests with pytest and GitHub Actions CI",
        ],
        "tech": ["Nuxt", "TypeScript", "Tailwind CSS", "GSAP", "WebGL", "Django", "DRF", "PostgreSQL"],
        "status": "live",
        "repo_url": "https://github.com/atlantikjashari/portfolio-api",
        "order": 7,
    },
]


def seed(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    for data in PROJECTS:
        Project.objects.get_or_create(slug=data["slug"], defaults=data)


def unseed(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    Project.objects.filter(slug__in=[p["slug"] for p in PROJECTS]).delete()


class Migration(migrations.Migration):
    dependencies = [("projects", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
