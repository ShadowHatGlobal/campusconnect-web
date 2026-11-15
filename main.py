# Import standard Python libraries + PyScript browser APIs
import html
import json
from pyscript import document, when, window

# Browser localStorage key for saving data across page reloads
STORAGE_KEY = "campusconnect_web_v1"

# Track active tab and modal action state
state = {
    "tab": "events",
    "modal_action": None,
    "target_id": None,
}


# Starter dataset so the community hub looks populated on first load
def get_default_data():
    return {
        "events": [
            {
                "title": "Annual Campus Hackathon",
                "organizer": "Computer Science Club",
                "date": "2026-11-25",
                "venue": "Main Auditorium",
            },
            {
                "title": "Resume & Career Workshop",
                "organizer": "Student Placement Cell",
                "date": "2026-11-28",
                "venue": "Seminar Hall B",
            },
        ],
        "study_groups": [
            {
                "id": 1,
                "course": "CS101",
                "topic": "Python & Data Structures",
                "schedule": "Tue & Thu, 4:00 PM - Library Room 2",
                "members": ["Aarav", "Meera"],
            },
            {
                "id": 2,
                "course": "MATH201",
                "topic": "Linear Algebra Exam Prep",
                "schedule": "Wed, 5:00 PM - Academic Block C",
                "members": ["Rohan"],
            },
        ],
        "resources": [
            {
                "id": 1,
                "author": "Ananya",
                "title": "Free Git & GitHub Cheat Sheet",
                "details": "Helpful summary guide for first-year lab submissions and team projects.",
                "replies": ["Karan: Thanks! This really helped with our group repo."],
            }
        ],
    }


# Save community dictionary to browser localStorage as JSON
def save_data(data):
    window.localStorage.setItem(STORAGE_KEY, json.dumps(data))


# Load community dictionary from localStorage or initialize defaults
def load_data():
    raw = window.localStorage.getItem(STORAGE_KEY)
    if not raw:
        data = get_default_data()
        save_data(data)
        return data
    try:
        return json.loads(raw)
    except Exception:
        data = get_default_data()
        save_data(data)
        return data


# Load initial data into memory
community_data = load_data()


# Show a clean notification banner
def show_toast(message):
    document.querySelector("#toast-msg").innerText = message
    document.querySelector("#toast").classList.remove("hidden")


@when("click", "#toast-close")
def close_toast(event):
    document.querySelector("#toast").classList.add("hidden")


# Update the hero statistics counters
def update_stats():
    document.querySelector("#stat-events").innerText = str(len(community_data["events"]))
    document.querySelector("#stat-groups").innerText = str(len(community_data["study_groups"]))
    document.querySelector("#stat-posts").innerText = str(len(community_data["resources"]))


# Render cards for the active tab, applying the search keyword filter
def render_feed():
    update_stats()
    keyword = document.querySelector("#search-input").value.strip().lower()
    container = document.querySelector("#cards-container")
    title_el = document.querySelector("#feed-title")
    tab = state["tab"]

    cards_html = []

    if tab == "events":
        title_el.innerText = "Upcoming Campus Events & Notices"
        for evt in community_data["events"]:
            text_blob = f"{evt['title']} {evt['organizer']} {evt['venue']}".lower()
            if keyword and keyword not in text_blob:
                continue
            cards_html.append(f"""
                <article class="card">
                    <div class="card-top">
                        <h4>{html.escape(evt['title'])}</h4>
                        <span class="badge">{html.escape(evt['date'])}</span>
                    </div>
                    <p class="meta">Organized by <strong>{html.escape(evt['organizer'])}</strong></p>
                    <p class="card-body-text">Venue: {html.escape(evt['venue'])}</p>
                </article>
            """)

    elif tab == "groups":
        title_el.innerText = "Active Course Study Groups"
        for grp in community_data["study_groups"]:
            text_blob = f"{grp['course']} {grp['topic']} {grp['schedule']}".lower()
            if keyword and keyword not in text_blob:
                continue
            members_text = ", ".join(html.escape(m) for m in grp["members"]) or "No members yet"
            cards_html.append(f"""
                <article class="card">
                    <div class="card-top">
                        <h4>{html.escape(grp['topic'])}</h4>
                        <span class="badge">{html.escape(grp['course'])}</span>
                    </div>
                    <p class="meta">{html.escape(grp['schedule'])}</p>
                    <div class="members-list">
                        <strong>Members ({len(grp['members'])}):</strong> {members_text}
                    </div>
                    <button type="button" class="btn-outline" data-action="join" data-id="{grp['id']}">
                        + Join Study Group
                    </button>
                </article>
            """)

    elif tab == "resources":
        title_el.innerText = "Student Q&A & Shared Resources"
        for post in community_data["resources"]:
            text_blob = f"{post['title']} {post['details']} {post['author']}".lower()
            if keyword and keyword not in text_blob:
                continue
            if post["replies"]:
                items = "".join(f"<li>{html.escape(r)}</li>" for r in post["replies"])
                replies_block = f"<div class='replies-box'><strong>Replies:</strong><ul>{items}</ul></div>"
            else:
                replies_block = "<p class='meta'>No replies yet. Be the first to help!</p>"

            cards_html.append(f"""
                <article class="card">
                    <div class="card-top">
                        <h4>{html.escape(post['title'])}</h4>
                        <span class="badge">By {html.escape(post['author'])}</span>
                    </div>
                    <p class="card-body-text">{html.escape(post['details'])}</p>
                    {replies_block}
                    <button type="button" class="btn-outline" data-action="reply" data-id="{post['id']}">
                        Reply to Post
                    </button>
                </article>
            """)

    if cards_html:
        container.innerHTML = "".join(cards_html)
    else:
        container.innerHTML = "<div class='empty-state'>No matching records found. Try another keyword or add one!</div>"


# Switch tabs and toggle the matching sidebar form
@when("click", "#tab-nav")
def handle_tab_click(event):
    btn = event.target.closest(".tab-btn")
    if not btn:
        return

    selected_tab = btn.getAttribute("data-tab")
    state["tab"] = selected_tab

    for el in document.querySelectorAll(".tab-btn"):
        el.classList.remove("active")
    btn.classList.add("active")

    for panel_id in ("#panel-events", "#panel-groups", "#panel-resources"):
        document.querySelector(panel_id).classList.add("hidden")
    document.querySelector(f"#panel-{selected_tab}").classList.remove("hidden")

    render_feed()


# Live search filter as the user types
@when("input", "#search-input")
def handle_search(event):
    render_feed()


# Add a new campus event
@when("click", "#btn-add-event")
def add_event(event):
    title = document.querySelector("#evt-title").value.strip()
    organizer = document.querySelector("#evt-org").value.strip()
    date = document.querySelector("#evt-date").value.strip()
    venue = document.querySelector("#evt-venue").value.strip()

    if not (title and organizer and date and venue):
        window.alert("Please fill out all event fields.")
        return

    community_data["events"].insert(0, {
        "title": title,
        "organizer": organizer,
        "date": date,
        "venue": venue,
    })
    save_data(community_data)

    for field_id in ("#evt-title", "#evt-org", "#evt-date", "#evt-venue"):
        document.querySelector(field_id).value = ""

    render_feed()
    show_toast(f"Published event: {title}")


# Create a new course study group
@when("click", "#btn-add-group")
def add_group(event):
    course = document.querySelector("#grp-course").value.strip().upper()
    topic = document.querySelector("#grp-topic").value.strip()
    schedule = document.querySelector("#grp-schedule").value.strip()
    creator = document.querySelector("#grp-creator").value.strip()

    if not (course and topic and schedule and creator):
        window.alert("Please fill out all study group fields.")
        return

    groups = community_data["study_groups"]
    next_id = max((g["id"] for g in groups), default=0) + 1
    groups.insert(0, {
        "id": next_id,
        "course": course,
        "topic": topic,
        "schedule": schedule,
        "members": [creator],
    })
    save_data(community_data)

    for field_id in ("#grp-course", "#grp-topic", "#grp-schedule", "#grp-creator"):
        document.querySelector(field_id).value = ""

    render_feed()
    show_toast(f"Created study group for {course}!")


# Publish a new resource or question
@when("click", "#btn-add-resource")
def add_resource(event):
    author = document.querySelector("#res-author").value.strip()
    title = document.querySelector("#res-title").value.strip()
    details = document.querySelector("#res-details").value.strip()

    if not (author and title and details):
        window.alert("Please fill out all resource/question fields.")
        return

    posts = community_data["resources"]
    next_id = max((p["id"] for p in posts), default=0) + 1
    posts.insert(0, {
        "id": next_id,
        "author": author,
        "title": title,
        "details": details,
        "replies": [],
    })
    save_data(community_data)

    for field_id in ("#res-author", "#res-title", "#res-details"):
        document.querySelector(field_id).value = ""

    render_feed()
    show_toast("Resource / question published!")


# Open modal when clicking "Join Study Group" or "Reply to Post"
@when("click", "#cards-container")
def handle_card_action(event):
    btn = event.target.closest("button[data-action]")
    if not btn:
        return

    action = btn.getAttribute("data-action")
    target_id = int(btn.getAttribute("data-id"))

    state["modal_action"] = action
    state["target_id"] = target_id

    document.querySelector("#modal-name").value = ""
    document.querySelector("#modal-reply-text").value = ""

    if action == "join":
        document.querySelector("#modal-title").innerText = "Join Study Group"
        document.querySelector("#modal-reply-group").classList.add("hidden")
    else:
        document.querySelector("#modal-title").innerText = "Reply to Community Post"
        document.querySelector("#modal-reply-group").classList.remove("hidden")

    document.querySelector("#modal-overlay").classList.remove("hidden")


@when("click", "#modal-cancel")
def cancel_modal(event):
    document.querySelector("#modal-overlay").classList.add("hidden")


# Handle modal submission for Join or Reply
@when("click", "#modal-submit")
def submit_modal(event):
    name = document.querySelector("#modal-name").value.strip()
    if not name:
        window.alert("Please enter your name.")
        return

    action = state["modal_action"]
    target_id = state["target_id"]

    if action == "join":
        for grp in community_data["study_groups"]:
            if grp["id"] == target_id:
                if name in grp["members"]:
                    show_toast(f"{name} is already a member of {grp['course']}.")
                else:
                    grp["members"].append(name)
                    save_data(community_data)
                    show_toast(f"{name} joined {grp['course']} - {grp['topic']}!")
                break

    elif action == "reply":
        reply_text = document.querySelector("#modal-reply-text").value.strip()
        if not reply_text:
            window.alert("Please enter your reply.")
            return
        for post in community_data["resources"]:
            if post["id"] == target_id:
                post["replies"].append(f"{name}: {reply_text}")
                save_data(community_data)
                show_toast("Reply added successfully!")
                break

    document.querySelector("#modal-overlay").classList.add("hidden")
    render_feed()


# Reset browser localStorage back to starter demo records
@when("click", "#btn-reset")
def reset_demo(event):
    global community_data
    community_data = get_default_data()
    save_data(community_data)
    render_feed()
    show_toast("Demo data restored to defaults.")


# Initial UI render once PyScript finishes loading
status_badge = document.querySelector("#py-status")
status_badge.innerText = "Welcome Fellow Student"
status_badge.classList.remove("loading")
status_badge.classList.add("ready")
render_feed()

