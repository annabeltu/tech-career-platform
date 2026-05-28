"""
Seed the database with roadmap actions and sample opportunities.

Usage:
    uv run --package tech-career-platform-api python -m api.scripts.seed
"""
from datetime import datetime
from sqlmodel import Session, select
from api.database import engine, create_db_and_tables
from api.models.roadmap_action import RoadmapAction
from api.models.opportunity import Opportunity


ROADMAP_ACTIONS = [
    RoadmapAction(
        stage=1,
        title="Understand the recruiting landscape",
        description="Learn what types of opportunities exist for freshmen: virtual programs, fellowships, hackathons, and freshman-specific internships.",
        action_type="Read",
        applicable_years=["Freshman", "Sophomore"],
    ),
    RoadmapAction(
        stage=1,
        title="Build your LinkedIn profile",
        description="Create a complete LinkedIn profile with your university, major, coursework, and any projects you've worked on.",
        action_type="Build",
        applicable_years=["Freshman", "Sophomore"],
    ),
    RoadmapAction(
        stage=2,
        title="Draft your first resume",
        description="Write a one-page resume highlighting coursework, projects, and extracurriculars. Upload it to Waypoint for AI feedback.",
        action_type="Build",
        applicable_years=["Freshman", "Sophomore"],
    ),
    RoadmapAction(
        stage=2,
        title="Apply to virtual programs and fellowships",
        description="Target freshman-eligible programs like Google STEP, Microsoft Explore, and CodePath. Designed for students with no experience.",
        action_type="Apply",
        applicable_years=["Freshman"],
    ),
    RoadmapAction(
        stage=3,
        title="Attend a hackathon",
        description="Register for an MLH hackathon or your school's local hackathon. You'll get a project for your resume and meet other CS students.",
        action_type="Apply",
        applicable_years=["Freshman", "Sophomore"],
    ),
    RoadmapAction(
        stage=3,
        title="Learn what an online assessment is",
        description="Most internship applications include a timed coding challenge. Study the basics of arrays and strings on LeetCode Easy difficulty.",
        action_type="Prepare",
        applicable_years=["Freshman", "Sophomore"],
    ),
    RoadmapAction(
        stage=4,
        title="Start applying to sophomore internships",
        description="Applications for summer internships at large tech companies typically open in August–September of your sophomore year. Set reminders now.",
        action_type="Apply",
        applicable_years=["Sophomore"],
    ),
    RoadmapAction(
        stage=4,
        title="Practice behavioral interview answers",
        description="Prepare 3–4 stories using the STAR format covering teamwork, challenges, and leadership. These come up in every tech interview.",
        action_type="Prepare",
        applicable_years=["Freshman", "Sophomore"],
    ),
    RoadmapAction(
        stage=5,
        title="Network intentionally",
        description="Reach out to 2–3 people in roles you're interested in on LinkedIn. Use Waypoint's cold email templates to start the conversation.",
        action_type="Build",
        applicable_years=["Freshman", "Sophomore"],
    ),
]


SAMPLE_OPPORTUNITIES = [
    Opportunity(
        title="Google STEP Internship",
        company="Google",
        type="Internship",
        description="The Student Training in Engineering Program is a 12-week internship for first and second year undergrads with little to no prior internship experience.",
        eligibility="Freshman OK",
        experience_required="None",
        is_paid=True,
        deadline=datetime(2025, 12, 1),
        location="Multiple US locations",
        application_url="https://careers.google.com/students/",
    ),
    Opportunity(
        title="Microsoft Explore Internship",
        company="Microsoft",
        type="Internship",
        description="A 12-week summer internship for freshmen and sophomores interested in exploring software engineering and program management.",
        eligibility="Freshman OK",
        experience_required="None",
        is_paid=True,
        deadline=datetime(2025, 11, 15),
        location="Redmond, WA",
        application_url="https://careers.microsoft.com/students/",
    ),
    Opportunity(
        title="CodePath Summer Internship Program",
        company="CodePath",
        type="Fellowship",
        description="Free technical interview prep and career coaching specifically designed for underrepresented students in tech. No experience required.",
        eligibility="Freshman OK",
        experience_required="None",
        is_paid=False,
        deadline=datetime(2025, 10, 1),
        location="Remote",
        application_url="https://codepath.org/",
    ),
    Opportunity(
        title="MLH Local Hack Day",
        company="Major League Hacking",
        type="Hackathon",
        description="A beginner-friendly 12-hour hackathon for first-time hackers. Build something in a weekend and meet other CS students.",
        eligibility="All Years",
        experience_required="None",
        is_paid=False,
        deadline=None,
        location="Various campuses + remote",
        application_url="https://mlh.io/",
    ),
    Opportunity(
        title="Girls Who Code Summer Immersion Program",
        company="Girls Who Code",
        type="Fellowship",
        description="A free virtual summer program for college freshmen interested in computer science.",
        eligibility="Freshman OK",
        experience_required="None",
        is_paid=False,
        deadline=datetime(2025, 3, 1),
        location="Remote",
        application_url="https://girlswhocode.com/",
    ),
    Opportunity(
        title="Kleiner Perkins Fellows Program",
        company="Kleiner Perkins",
        type="Fellowship",
        description="A highly selective 10-week fellowship pairing top undergraduate students with early-stage startups in the KP portfolio.",
        eligibility="All Years",
        experience_required="Some Projects",
        is_paid=True,
        deadline=datetime(2026, 1, 15),
        location="San Francisco, CA",
        application_url="https://fellows.kleinerperkins.com/",
    ),
]


def seed() -> None:
    create_db_and_tables()

    with Session(engine) as session:
        existing_actions = session.exec(select(RoadmapAction)).all()
        if not existing_actions:
            for action in ROADMAP_ACTIONS:
                session.add(action)
            session.commit()
            print(f"Seeded {len(ROADMAP_ACTIONS)} roadmap actions.")
        else:
            print("Roadmap actions already seeded, skipping.")

        existing_opps = session.exec(select(Opportunity)).all()
        if not existing_opps:
            for opp in SAMPLE_OPPORTUNITIES:
                session.add(opp)
            session.commit()
            print(f"Seeded {len(SAMPLE_OPPORTUNITIES)} opportunities.")
        else:
            print("Opportunities already seeded, skipping.")

    print("Seed complete.")


if __name__ == "__main__":
    seed()