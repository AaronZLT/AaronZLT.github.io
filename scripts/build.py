from datetime import date
from html import escape
from pathlib import Path
from shutil import copy2
from string import Template
from textwrap import indent
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


def linked_text(value):
    return re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        r'<a href="\2">\1</a>',
        text(value),
    )


def timeline(entries):
    return "\n".join(
        template(
            "items/timeline",
            date=text(entry["date"]),
            organization=text(entry["organization"]),
            role=text(entry["role"]),
            description=linked_text(entry["description"]),
        )
        for entry in entries
    )


def publications(papers, author_name):
    articles = []
    for paper in papers:
        authors = ", ".join(
            f"<strong>{text(name)}</strong>" if name == author_name else text(name)
            for name in paper["authors"]
        )
        articles.append(template(
            "items/publication",
            title=text(paper["title"]),
            authors=authors,
            venue=text(paper["venue"]),
        ))
    return "\n".join(articles)


def build():
    site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    profile = content("profile")
    about = content("about")
    contact = about["contact"]
    services = content("services")
    site_url = site["url"]

    sections = {
        "about": template(
            "sections/about",
            paragraphs=indent("\n".join(f"<p>{linked_text(p)}</p>" for p in about["paragraphs"]), "  "),
            contact_text=text(contact["text"]),
            email=text(contact["email"]),
            scholar_href=text(contact["google_scholar"]),
            linkedin_href=text(contact["linkedin"]),
            wechat_image=text(contact["wechat_qr"]),
        ),
        "publications": template(
            "sections/publications",
            papers=indent(publications(content("publications"), profile["name"]), "    "),
        ),
        "education": template("sections/education", entries=indent(timeline(content("education")), "    ")),
        "experience": template("sections/experience", entries=indent(timeline(content("experience")), "    ")),
        "services": template(
            "sections/services",
            conferences=text(services["reviewer"]["conferences"]),
            journals=text(", ".join(services["reviewer"]["journals"])),
            courses=indent("\n".join(
                template("items/course", course=text(course["course"]), term=text(course["term"]))
                for course in services["teaching"]
            ), "    "),
        ),
    }
    style_paths = [ROOT / "styles" / f"{name}.css" for name in STYLE_FILES]
    styles = "\n".join(path.read_text(encoding="utf-8") for path in style_paths)
    style_version = max(path.stat().st_mtime_ns for path in style_paths)
    structured_data = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "@id": site_url + "#webpage",
        "url": site_url,
        "name": site["title"],
        "description": site["description"],
        "mainEntity": {
            "@type": "Person",
            "@id": site_url + "#person",
            "name": profile["name"],
            "url": site_url,
            "image": site_url + profile["avatar"],
            "jobTitle": profile["role"],
            "affiliation": {
                "@type": "CollegeOrUniversity",
                "name": profile["affiliation"],
            },
            "sameAs": [contact["google_scholar"], contact["linkedin"]],
        },
    }
    html = template(
        "page",
        language=text(site["language"]),
        description=text(site["description"]),
        title=text(site["title"]),
        name=text(profile["name"]),
        canonical_url=text(site_url),
        style_version=style_version,
        structured_data=json.dumps(structured_data, ensure_ascii=False, indent=2).replace("<", "\\u003c"),
        header=indent(template("header"), "    "),
        sidebar=indent(template("sidebar", **{key: text(value) for key, value in profile.items()}), "      "),
        **{name: indent(html, "        ") for name, html in sections.items()},
        footer=indent(template("footer", year=date.today().year, name=text(profile["name"])), "    "),
    )
    (DIST / "assets").mkdir(parents=True, exist_ok=True)
    for image_path in (profile["avatar"], contact["wechat_qr"], "assets/favicon.ico"):
        copy2(ROOT / image_path, DIST / image_path)
    copy2(ROOT / "googledd3d6e39161b82df.html", DIST / "googledd3d6e39161b82df.html")
    copy2(ROOT / "BingSiteAuth.xml", DIST / "BingSiteAuth.xml")
    (DIST / "index.html").write_text(html + "\n", encoding="utf-8")
    (DIST / "assets" / "style.css").write_text(styles, encoding="utf-8")
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {site_url}sitemap.xml\n",
        encoding="utf-8",
    )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{text(site_url)}</loc></url>\n'
        '</urlset>\n',
        encoding="utf-8",
    )


if __name__ == "__main__":
    build()
    print(f"Built {DIST}")
