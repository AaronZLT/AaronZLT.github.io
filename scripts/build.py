from html import escape
from pathlib import Path
from shutil import copy2
from string import Template
from textwrap import indent
from urllib.parse import quote
import json
import re


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
STYLE_FILES = ("theme", "base", "layout", "components", "responsive")


def content(name):
    return json.loads((ROOT / "content" / f"{name}.json").read_text(encoding="utf-8"))


def template(template_path, **values):
    source = (ROOT / "templates" / f"{template_path}.html").read_text(encoding="utf-8")
    return Template(source).substitute(values).rstrip()


def text(value):
    return escape(str(value), quote=True)


def timeline(entries):
    items = []
    for entry in entries:
        description = entry["description"]
        if isinstance(description, list):
            description = "".join(
                f'<a href="{text(part["url"])}">{text(part["text"])}</a>'
                if isinstance(part, dict) else text(part)
                for part in description
            )
        else:
            description = text(description)
        items.append(template(
            "items/timeline",
            date=text(entry["date"]),
            organization=text(entry["organization"]),
            role=text(entry["role"]),
            description=description,
        ))
    return "\n".join(items)


def publications(papers):
    articles = []
    for paper in papers:
        authors = []
        for position, name in enumerate(paper["authors"], start=1):
            author = text(name)
            if position == paper["author_position"]:
                author = f"<strong>{author}</strong>"
            authors.append(author)
        articles.append(template(
            "items/publication",
            title=text(paper["title"]),
            authors=", ".join(authors),
            venue=text(paper["venue"]),
        ))
    return "\n".join(articles)


def source_links(sources):
    return " · ".join(
        f'<a href="{text(source["url"])}">{text(source["label"])}</a>'
        for source in sources
    )


def chart_value(value, format_name):
    if format_name == "currency":
        return f"${value:,.2f}" if value % 1 else f"${value:,.0f}"
    return f"{value:g}"


def cost_chart(chart):
    metrics = []
    for metric in chart["metrics"]:
        bars = "\n".join(
            template(
                "items/chart-bar",
                label=text(row["label"]),
                value=text(chart_value(row["value"], metric["format"])),
                tone=text(row["tone"]),
                width=f'{row["value"] / metric["max"] * 100:.4f}',
            )
            for row in metric["rows"]
        )
        metrics.append(template(
            "items/chart-metric",
            label=text(metric["label"]),
            direction=text(metric["direction"]),
            bars=indent(bars, "    "),
            zero=text(chart_value(0, metric["format"])),
            middle=text(chart_value(metric["max"] / 2, metric["format"])),
            maximum=text(chart_value(metric["max"], metric["format"])),
        ))
    highlight = ""
    if "highlight" in chart:
        highlight = (
            '<p class="chart-highlight">'
            f'<strong>{text(chart["highlight"])}</strong>'
            f'<span>{text(chart["highlight_label"])}</span></p>'
        )
    return template(
        "items/cost-chart",
        id=text(chart["id"]),
        date=text(chart["date"]),
        title=text(chart["title"]),
        takeaway=text(chart["takeaway"]),
        metrics=indent("\n".join(metrics), "  "),
        highlight=indent(highlight, "  "),
        note=text(chart["note"]),
        sources=source_links(chart["sources"]),
    )


def operating_cost_chart(costs):
    rows = [
        {
            "label": model["label"],
            "tone": model["tone"],
            "value": costs["requests_per_month"] * (
                costs["input_tokens_per_request"] * model["input_price"]
                + costs["output_tokens_per_request"] * model["output_price"]
            ) / 1_000_000,
        }
        for model in costs["models"]
    ]
    return cost_chart({
        **costs,
        "metrics": [{
            "label": "Monthly API bill · USD",
            "direction": "Lower is better",
            "format": "currency",
            "max": max(row["value"] for row in rows),
            "rows": rows,
        }],
        "note": (
            f'Illustrative workload: {costs["requests_per_month"]:,} requests/month, '
            f'{costs["input_tokens_per_request"]:,} input + '
            f'{costs["output_tokens_per_request"]:,} output tokens/request. '
            'Standard uncached rates; Haiku 5.5 prompts ≤100k tokens.'
        ),
    })


def build():
    profile = content("profile")
    experience = content("experience")
    research = content("research")
    service = content("service")
    hero = profile["hero"]
    approach = research["approach"]
    evidence = research["evidence"]

    headline = "".join(
        f'<em>{text(part["text"])}</em>' if part.get("emphasis") else text(part["text"])
        for part in hero["headline"]
    )
    areas = "\n".join(
        template("items/research-area", **{key: text(value) for key, value in area.items()})
        for area in research["areas"]
    )
    charts = "\n".join(cost_chart(chart) for chart in evidence["charts"])
    service_years = []
    for year in evidence["timeline"]["years"]:
        events = "\n".join(
            template(
                "items/service-event",
                date=text(event["date"]),
                title=text(event["title"]),
                status=text(event["status"]),
                tone=text(event["tone"]),
                description=text(event["description"]),
                sources=source_links(event["sources"]),
            )
            for event in year["events"]
        )
        service_years.append(template(
            "items/service-year", year=year["year"], events=indent(events, "    ")
        ))
    courses = "\n".join(
        template("items/course", course=text(course["course"]), term=text(course["term"]))
        for course in service["teaching"]
    )

    sections = {
        "hero": template(
            "sections/hero",
            headline=headline,
            introduction=text(hero["introduction"]),
            scholar_href=text(hero["scholar"]["href"]),
            scholar_label=text(hero["scholar"]["label"]),
            button_href=text(hero["button"]["href"]),
            button_label=text(hero["button"]["label"]),
            name=text(profile["name"]),
            position=text(profile["position"]),
            email=text(profile["email"]),
            tags=indent("\n".join(f"<li>{text(tag)}</li>" for tag in profile["tags"]), "      "),
        ),
        "about": template("sections/about", bio=text(profile["bio"])),
        "education": template("sections/education", entries=indent(timeline(experience["education"]), "    ")),
        "experience": template("sections/experience", entries=indent(timeline(experience["experience"]), "    ")),
        "research": template(
            "sections/research",
            title=text(research["title"]),
            introduction=text(research["introduction"]),
            areas=indent(areas, "    "),
            approach_label=text(approach["label"]),
            approach_title=text(approach["title"]),
            approach_description=text(approach["description"]),
            evidence_title=text(evidence["title"]),
            evidence_subtitle=text(evidence["subtitle"]),
            overview=text(evidence["overview"]),
            operating_costs=indent(operating_cost_chart(evidence["operating_costs"]), "      "),
            charts=indent(charts, "        "),
            timeline_title=text(evidence["timeline"]["title"]),
            service_years=indent("\n".join(service_years), "          "),
            performance_title=text(evidence["performance_context"]["title"]),
            performance_description=text(evidence["performance_context"]["description"]),
            performance_sources=source_links(evidence["performance_context"]["sources"]),
            limitations_title=text(evidence["limitations"]["title"]),
            limitations_description=text(evidence["limitations"]["description"]),
            date_note=text(evidence["date_note"]),
        ),
        "publications": template("sections/publications", papers=indent(publications(content("publications")), "    ")),
        "service": template(
            "sections/service",
            conferences=text(service["reviewer"]["conferences"]),
            journals=text(", ".join(service["reviewer"]["journals"])),
            courses=indent(courses, "      "),
        ),
        "contact": template(
            "sections/contact",
            introduction=text(profile["contact"]["introduction"]),
            email=text(profile["email"]),
            affiliation="<br>".join(text(line) for line in profile["contact"]["affiliation"]),
            linkedin_href=text(profile["contact"]["linkedin"]),
            wechat_image=text(profile["contact"]["wechat"]["image"]),
            wechat_alt=text(profile["contact"]["wechat"]["alt"]),
            wechat_caption=text(profile["contact"]["wechat"]["caption"]),
        ),
    }
    navigation = "\n".join(
        f'<a href="{text(link["href"])}">{text(link["label"])}</a>'
        for link in profile["navigation"]
    )
    styles = "\n".join(
        (ROOT / "styles" / f"{name}.css").read_text(encoding="utf-8")
        for name in STYLE_FILES
    )
    accent = re.search(r"--accent:\s*(#[0-9a-fA-F]{6})", styles).group(1)
    favicon = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="14" fill="{accent}"/>'
        '<text x="32" y="43" text-anchor="middle" font-family="Georgia,serif" '
        f'font-size="34" fill="white">{text(profile["initials"])}</text></svg>'
    )
    html = template(
        "page",
        language=text(profile["page"]["language"]),
        description=text(profile["page"]["description"]),
        title=text(profile["page"]["title"]),
        theme_color=accent,
        favicon="data:image/svg+xml," + quote(favicon, safe=""),
        header=indent(template("header", name=text(profile["name"]), navigation=indent(navigation, "      ")), "    "),
        **{name: indent(html, "      ") for name, html in sections.items()},
        footer=indent(template("footer", year=profile["footer"]["year"], name=text(profile["name"]), last_updated=text(profile["footer"]["last_updated"])), "    "),
    )
    (DIST / "assets").mkdir(parents=True, exist_ok=True)
    copy2(ROOT / profile["contact"]["wechat"]["image"], DIST / profile["contact"]["wechat"]["image"])
    copy2(ROOT / "googledd3d6e39161b82df.html", DIST / "googledd3d6e39161b82df.html")
    (DIST / "index.html").write_text(html + "\n", encoding="utf-8")
    (DIST / "assets" / "style.css").write_text(styles, encoding="utf-8")


if __name__ == "__main__":
    build()
    print(f"Built {DIST}")
