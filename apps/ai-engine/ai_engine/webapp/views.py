"""Server-rendered HTML. No build step, no template engine, no client framework.

Every interpolated value goes through :func:`esc`. Transcript text is *untrusted
input* — it is whatever a person typed, or whatever a model returned — so rendering it
raw would be a script-injection hole in a tool whose whole job is handling sensitive
material.
"""
from __future__ import annotations

from html import escape

CSS = """
:root { color-scheme: light dark; --fg:#111; --muted:#666; --bg:#fff; --card:#f6f6f7;
        --line:#e3e3e6; --accent:#2b6cb0; --warn:#b7791f; --bad:#c53030; --good:#276749; }
@media (prefers-color-scheme: dark) {
  :root { --fg:#e8e8ea; --muted:#9a9aa2; --bg:#16161a; --card:#1f1f25;
          --line:#2e2e36; --accent:#7cb3e8; --warn:#e0b050; --bad:#f08a8a; --good:#7fc99b; }
}
* { box-sizing:border-box; }
body { margin:0; font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
       color:var(--fg); background:var(--bg); }
main { max-width:920px; margin:0 auto; padding:24px 20px 64px; }
a { color:var(--accent); }
h1 { font-size:22px; margin:0 0 4px; } h2 { font-size:17px; margin:28px 0 10px; }
h3 { font-size:15px; margin:0 0 6px; }
.posture { font:12px ui-monospace,SFMono-Regular,Menlo,monospace; color:var(--muted);
           border-bottom:1px solid var(--line); padding:8px 20px; background:var(--card); }
.posture .flag { color:var(--warn); font-weight:600; }
.sub { color:var(--muted); margin:0 0 18px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px;
        padding:14px 16px; margin:0 0 12px; }
.quote { border-left:3px solid var(--accent); padding:8px 12px; margin:8px 0;
         background:var(--bg); border-radius:0 6px 6px 0; }
.meta { font:12px ui-monospace,Menlo,monospace; color:var(--muted); }
.tier { display:inline-block; font-size:11px; padding:1px 7px; border-radius:99px;
        border:1px solid var(--line); color:var(--muted); }
.verdict { font-size:12px; font-weight:600; }
.accepted { color:var(--good); } .rejected { color:var(--bad); } .amended { color:var(--warn); }
button, .btn { font:inherit; padding:7px 13px; border-radius:7px; border:1px solid var(--line);
        background:var(--bg); color:var(--fg); cursor:pointer; text-decoration:none;
        display:inline-block; }
button.primary { background:var(--accent); border-color:var(--accent); color:#fff; }
button.danger { color:var(--bad); }
input[type=text], textarea, select { font:inherit; padding:7px 9px; border-radius:7px;
        border:1px solid var(--line); background:var(--bg); color:var(--fg); width:100%; }
form.inline { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
table { width:100%; border-collapse:collapse; font-size:14px; }
th,td { text-align:left; padding:7px 8px; border-bottom:1px solid var(--line); }
th { color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; }
.row { display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
.spacer { flex:1; }
.note { border-left:3px solid var(--warn); padding:8px 12px; color:var(--muted);
        font-size:13px; margin:12px 0; }
.turn { margin:0 0 14px; } .q { font-weight:600; } .a { color:var(--muted); }
.seg { padding:6px 10px; border-left:3px solid transparent; border-radius:6px; }
.seg .who { font-size:12px; font-weight:600; color:var(--muted); text-transform:uppercase; }
.seg:target { border-left-color:var(--accent); background:var(--card); outline:1px solid var(--accent); }
.grounded { border-left:3px solid var(--good); padding:8px 12px; margin:12px 0;
        font-size:13px; color:var(--muted); background:var(--bg); border-radius:0 6px 6px 0; }
.grounded strong { color:var(--good); }
.evi { font-size:12px; font-weight:600; text-decoration:none; }
.split { display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:14px; }
.split h3 { margin:0 0 8px; }
.split .doc { max-height:72vh; overflow:auto; }
.split .label { font-size:12px; font-weight:600; text-transform:uppercase;
        color:var(--muted); letter-spacing:.4px; }
.split .left  { border-top:3px solid var(--accent); }
.split .right { border-top:3px solid var(--good); }
pre { white-space:pre-wrap; font:13px ui-monospace,Menlo,monospace; }
"""


def esc(value) -> str:
    return escape(str(value), quote=True)


def layout(title: str, body: str, *, posture: str = "", warn: bool = False,
           head_extra: str = "") -> str:
    flag = ' <span class="flag">⚠ not a real interview / not protected at rest</span>' if warn else ""
    bar = f'<div class="posture">{esc(posture)}{flag}</div>' if posture else ""
    return (
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        '<meta name=viewport content="width=device-width,initial-scale=1">'
        f"{head_extra}"
        f"<title>{esc(title)} · Groundwork</title><style>{CSS}</style></head><body>"
        f"{bar}<main>{body}</main></body></html>"
    )


def invitations(*, items: list[dict], posture: str, warn: bool) -> str:
    rows = ""
    for item in items:
        link = f"/i/{item['token']}"
        tid = item["transcript_id"]
        transcript_cell = (
            f'<a href="/transcripts/{esc(tid)}/review">review</a>' if tid else "—"
        )
        rows += (
            "<tr>"
            f'<td>{esc(item["pseudonym"])}</td>'
            f'<td>{esc(item["status"])}</td>'
            f'<td class="meta">{esc(link)}</td>'
            f"<td>{transcript_cell}</td>"
            "</tr>"
        )
    table = (f"<table><tr><th>Participant</th><th>Status</th><th>Link path</th>"
             f"<th>Transcript</th></tr>{rows}</table>"
             if rows else '<p class="sub">No invitations yet.</p>')
    body = (
        "<h1>Invitations</h1>"
        '<p class="sub">Each link opens the interview surface for one person. The '
        "participant is never asked for their name — the pseudonym is assigned here.</p>"
        + _nav("/invitations")
        + """
        <form class="inline" method="post" action="/invitations/new">
          <label>Participant <input type="text" name="participant"
                 placeholder="name or code (kept on this side only)" required></label>
          <button class="primary" type="submit">Create invitation</button>
        </form>
        <form method="post" action="/invitations/batch" style="margin-top:10px">
          <label>Or paste a roster — one participant per line
            <textarea name="names" rows="3"
                      placeholder="Ana&#10;Bo&#10;Citra"></textarea></label>
          <div style="margin-top:8px">
            <button class="primary" type="submit">Create batch</button>
          </div>
        </form>
        """
        + '<div class="note">Send the link path to the participant on the interview '
          "surface host (run it with <code>python -m ai_engine.employee</code>, default "
          "port 8100). Treat the links as secrets: the token is the only access control, "
          "and it is what keeps one person's interview from being anyone else's.</div>"
        + table
    )
    return layout("Invitations", body, posture=posture, warn=warn)


def _nav(current: str = "") -> str:
    items = [("/", "Interviews"), ("/invitations", "Invitations"),
             ("/engagement", "Engagement report")]
    links = " · ".join(
        f'<a href="{esc(href)}">{esc(label)}</a>' if href != current else f"<strong>{esc(label)}</strong>"
        for href, label in items
    )
    return f'<p class="meta">{links}</p>'


# --- dashboard -------------------------------------------------------------

def dashboard(*, interviews: list[dict], live: list[dict], posture: str, warn: bool,
              engagements: list[dict] | None = None) -> str:
    rows = ""
    for item in interviews:
        pending = item["claims"] - item["validated"]
        rows += (
            "<tr>"
            f'<td><a href="/transcripts/{esc(item["id"])}/review">{esc(item["id"])}</a></td>'
            f'<td>{esc(item["participant"])}</td>'
            f'<td>{esc(item.get("engagement", "—"))}</td>'
            f'<td>{item["segments"]}</td>'
            f'<td>{item["claims"]}</td>'
            f'<td>{"—" if not pending else f"<strong>{pending}</strong>"}</td>'
            f'<td><a class="btn" href="/transcripts/{esc(item["id"])}/review">Review</a> '
            f'<a class="btn" href="/transcripts/{esc(item["id"])}">Transcript</a></td>'
            "</tr>"
        )
    table = (
        "<table><tr><th>Interview</th><th>Participant</th><th>Engagement</th>"
        "<th>Segments</th>"
        f"<th>Claims</th><th>To review</th><th></th></tr>{rows}</table>"
        if rows else '<p class="sub">No stored interviews yet.</p>'
    )

    live_html = ""
    if live:
        items = "".join(
            f'<li><a href="/interviews/{esc(x["id"])}">{esc(x["id"])}</a> — '
            f'turn {x["turns"]}, {esc(x["status"])}</li>' for x in live
        )
        live_html = f"<h2>In progress</h2><ul>{items}</ul>"

    engagements_html = ""
    if engagements:
        e_rows = "".join(
            f"<tr><td>{esc(e['name'])}</td><td>{e['interviews']}</td>"
            f'<td class="meta">{esc(e["id"])}</td></tr>'
            for e in engagements
        )
        engagements_html = (
            "<h2>Engagements</h2>"
            "<table><tr><th>Name</th><th>Interviews</th><th></th></tr>"
            f"{e_rows}</table>"
        )

    new_form = """
    <h2>Start an interview</h2>
    <form class="inline" method="post" action="/interviews/new">
      <label>Participant
        <input type="text" name="participant" placeholder="name or code" required>
      </label>
      <label>Engagement <input type="text" name="engagement"
             placeholder="engagement name (optional)"></label>
      <label>Mode
        <select name="mode">
          <option value="manual">Answered at the keyboard</option>
          <option value="simulated">Simulated persona (demo)</option>
        </select>
      </label>
      <button class="primary" type="submit">Start</button>
    </form>
    <form class="inline" method="post" action="/demo/run" style="margin-top:10px">
      <button type="submit">Run the demo engagement — all interviews in parallel,
        both deliverables out</button>
    </form>
    <div class="note">The participant's name is pseudonymised immediately and never
    stored with their answers. Only this consultant workspace can re-identify, via a
    key held separately.</div>
    """
    # While interviews are live the dashboard refreshes itself, so the demo
    # reads as parallel progress without any client-side code.
    refresh = '<meta http-equiv="refresh" content="4">' if live else ""
    body = (
        "<h1>Consultant workspace</h1>"
        '<p class="sub">Interview · review evidence · validate · report</p>'
        + _nav("/") + new_form + live_html + "<h2>Stored interviews</h2>" + table
        + engagements_html
    )
    return layout("Workspace", body, posture=posture, warn=warn, head_extra=refresh)


# --- interview runner ------------------------------------------------------

def runner(*, interview_id: str, participant: str, question: str | None,
           turns: int, max_turns: int, transcript_html: str, closed: bool,
           coverage: dict, posture: str, warn: bool) -> str:
    if closed:
        action = (
            f'<form method="post" action="/interviews/{esc(interview_id)}/finish">'
            '<button class="primary" type="submit">Finalise &amp; store transcript</button>'
            "</form>"
            '<div class="note">Finalising makes the transcript immutable and stores it, '
            "so every quote stays verifiable afterwards.</div>"
        )
    else:
        action = (
            f'<form method="post" action="/interviews/{esc(interview_id)}/answer">'
            f'<div class="card"><h3>{esc(question or "")}</h3>'
            '<textarea name="answer" rows="4" placeholder="the answer, as given" required autofocus></textarea>'
            '<div class="row" style="margin-top:10px">'
            '<button class="primary" type="submit">Send answer</button>'
            '<div class="spacer"></div>'
            f'<button class="danger" type="submit" formaction="/interviews/{esc(interview_id)}/finish">'
            "End interview</button></div></div></form>"
        )
    covered = f'{coverage.get("areas_covered", 0)}/{coverage.get("areas_total", 0)}'
    body = (
        f"<h1>Interview · {esc(participant)}</h1>"
        f'<p class="sub">{esc(interview_id)} — turn {turns} of {max_turns} · '
        f"areas covered {esc(covered)} · Tier-2+ disclosures "
        f'{coverage.get("disclosures_tier2plus", 0)}</p>'
        + action
        + "<h2>Transcript so far</h2>" + transcript_html
    )
    return layout("Interview", body, posture=posture, warn=warn)


def transcript_turns(segments: list[dict]) -> str:
    if not segments:
        return '<p class="sub">Nothing recorded yet.</p>'
    out = ""
    for seg in segments:
        cls = "q" if seg["speaker"] == "interviewer" else "a"
        who = "Groundwork" if seg["speaker"] == "interviewer" else "Participant"
        out += (f'<div class="turn"><div class="{cls}">{esc(who)}: {esc(seg["text"])}</div>'
                f'<div class="meta">{esc(seg["id"])}</div></div>')
    return out


# --- review ----------------------------------------------------------------

def review(*, interview_id: str, participant: str, items: list[dict],
           confabulation: float, unsourced: int, unsupported: int,
           posture: str, warn: bool) -> str:
    if not items:
        cards = '<p class="sub">No claims were proposed from this interview.</p>'
    else:
        cards = ""
        for item in items:
            v = item.get("verdict")
            badge = (f'<span class="verdict {esc(v)}">{esc(v.upper())}</span>'
                     if v else '<span class="meta">awaiting review</span>')
            corrected = ""
            if item.get("new_statement"):
                corrected = (f'<p class="meta">amended to: '
                             f'{esc(item["new_statement"])}</p>')
            form = (
                f'<form method="post" action="/transcripts/{esc(interview_id)}/validate">'
                f'<input type="hidden" name="claim_id" value="{esc(item["claim_id"])}">'
                '<div class="row">'
                '<button class="primary" name="verdict" value="accepted" type="submit">Accept</button>'
                '<button name="verdict" value="amended" type="submit">Amend</button>'
                '<button class="danger" name="verdict" value="rejected" type="submit">Reject</button>'
                "</div>"
                '<div class="row" style="margin-top:8px">'
                '<input type="text" name="statement" placeholder="corrected wording (for Amend)">'
                "</div>"
                '<div class="row" style="margin-top:8px">'
                '<input type="text" name="reason" placeholder="reason (required to amend or reject)">'
                "</div></form>"
            )
            cards += (
                '<div class="card">'
                f'<div class="row"><span class="tier">tier {item["tier"]} · '
                f'{esc(item["claim_type"])}</span><div class="spacer"></div>{badge}</div>'
                # Evidence is deliberately rendered BEFORE the judgement controls,
                # and the quote links to the exact verbatim moment it rests on.
                f'<a class="quote evi" href="/transcripts/{esc(interview_id)}'
                f'#seg-{esc(item["segment_id"])}">{esc(item["quote"])}</a>'
                f'<div class="meta">gate 1 grounded ✓ · gate 2 supported ✓ · '
                f'{esc(item["segment_id"])} '
                f'[{item["start"]}:{item["end"]}] · {esc(item["match_kind"])} · '
                f'<a href="/transcripts/{esc(interview_id)}#seg-{esc(item["segment_id"])}">'
                f'open in transcript</a></div>'
                f"<h3 style=\"margin-top:10px\">{esc(item['statement'])}</h3>"
                f"{corrected}{form}</div>"
            )

    body = (
        f"<h1>Review · {esc(participant)}</h1>"
        f'<p class="sub">{esc(interview_id)} — AI-proposed claims. Nothing is a finding '
        f"until you accept it.</p>"
        + _nav()
        + f'<p class="meta">{unsourced} rejected as unsourced · {unsupported} rejected as '
          f"unsupported by their quote · confabulation rate {confabulation:.0%}</p>"
        + '<div class="note">The quote is shown above each claim on purpose: a decision '
          "recorded without reviewing the evidence is a rubber stamp, and the system "
          "keeps the evidence you reviewed as part of the record.</div>"
        + cards
        + f'<p style="margin-top:20px"><a class="btn" href="/transcripts/{esc(interview_id)}/report">'
          "Consultant report</a> "
          f'<a class="btn" href="/transcripts/{esc(interview_id)}/employer">Employer release</a> '
          f'<a class="btn" href="/transcripts/{esc(interview_id)}">Full transcript</a></p>'
    )
    return layout("Review", body, posture=posture, warn=warn)


# --- documents -------------------------------------------------------------

def transcript_page(*, title: str, subtitle: str, segments: list[dict],
                    back: str, posture: str, warn: bool, note: str = "") -> str:
    """The stored record with a stable anchor per segment.

    Every finding everywhere in the product deep-links to ``#seg-{segment_id}``;
    the ``:target`` highlight is what makes provenance feel like provenance —
    click a claim, land on the exact sentence it quotes.
    """
    note_html = f'<div class="note">{esc(note)}</div>' if note else ""
    rows = ""
    for seg in segments:
        who = "Groundwork" if seg["speaker"] == "interviewer" else "Participant"
        rows += (
            f'<section class="seg" id="{esc(seg["id"])}">'
            f'<div class="who">{esc(who)} · {esc(seg["id"])}</div>'
            f'<div>{esc(seg["text"])}</div></section>'
        )
    body = (
        f"<h1>{esc(title)}</h1><p class=\"sub\">{esc(subtitle)}</p>"
        + _nav() + note_html
        + f'<div class="card">{rows}</div>'
        + f'<p><a class="btn" href="{esc(back)}">Back</a></p>'
    )
    return layout(title, body, posture=posture, warn=warn)


def grounded_header(*, proposed: int, grounded: int, unsourced: int,
                    unsupported: int, confabulation: float) -> str:
    """The honesty block: what the gates admitted, and what they refused."""
    return (
        f'<div class="grounded"><strong>Grounded by construction.</strong> '
        f'{grounded} of {proposed} proposed claims carried a quote that exists '
        f"verbatim in the transcript and supports the claim; {unsourced} were "
        f"rejected as unsourced and {unsupported} as unsupported by their quote. "
        f"Confabulation rate {confabulation:.0%}. Rejected claims are dropped, "
        f"not softened — nothing below was written by the model without evidence."
        f"</div>"
    )


def consultant_report_page(*, transcript_id: str, participant: str,
                           findings: list[dict], grounding: dict | None,
                           posture: str, warn: bool) -> str:
    """The deliverable as evidence cards — every claim opens its verbatim moment."""
    from html import escape as _e

    if not findings:
        cards = ('<p class="sub">No validated findings yet — accept or amend '
                 'claims on the review page.</p>')
    else:
        cards = ""
        for f in findings:
            tag = f.verdict.value
            ev = f.claim.evidence[0]
            corrected = ""
            if f.decision.correction is not None and f.decision.correction.new_statement:
                corrected = (f'<p class="meta">amended to: '
                             f'{_e(f.decision.correction.new_statement)}</p>')
            cards += (
                '<div class="card">'
                f'<div class="row"><span class="tier">tier {f.claim.tier} · '
                f'{_e(f.claim.claim_type.value)}</span><div class="spacer"></div>'
                f'<span class="verdict {_e(tag)}">{_e(tag.upper())}</span></div>'
                f'<h3>{_e(f.statement)}</h3>'
                f'<a class="quote evi" href="/transcripts/{_e(transcript_id)}'
                f'#seg-{_e(ev.ref.segment_id)}">{_e(ev.quote)}</a>'
                f'<div class="meta">gate 1 grounded ✓ · gate 2 supported ✓ · '
                f'{_e(ev.ref.segment_id)} [{ev.ref.start}:{ev.ref.end}] · '
                f'{_e(ev.match_kind)} · '
                f'<a href="/transcripts/{_e(transcript_id)}#seg-{_e(ev.ref.segment_id)}">'
                f'open in transcript</a></div>{corrected}</div>'
            )
    grounding_html = ""
    if grounding:
        grounding_html = grounded_header(
            proposed=grounding["proposed"], grounded=grounding["grounded"],
            unsourced=grounding["unsourced"], unsupported=grounding["unsupported"],
            confabulation=grounding["confabulation"])
    body = (
        f"<h1>Consultant report · {_e(participant)}</h1>"
        f'<p class="sub">{_e(transcript_id)} · validated findings only · '
        f"every claim opens the verbatim moment it rests on</p>"
        + _nav() + grounding_html + cards
    )
    return layout("Consultant report", body, posture=posture, warn=warn)


def engagement_release_note(engagement_id: str, engagement_name: str) -> str:
    """The per-transcript employer page's pointer to the engagement-level
    release. Built here so the anchor is escaped inside the views module —
    routes hand over data, never hand-assembled HTML."""
    return (
        "A single interview cannot be anonymous within itself, so this page "
        "releases only suppressions. "
        f'<a href="/engagements/{esc(engagement_id)}/employer">'
        f"Open the engagement-level release for {esc(engagement_name)}</a>."
    )


def document(*, title: str, subtitle: str, markdown: str, back: str,
             posture: str, warn: bool, note: str = "",
             note_html: str = "") -> str:
    if note and note_html:
        raise ValueError("pass note (plain text) or note_html (pre-escaped), not both")
    note_html = f'<div class="note">{esc(note) if note else note_html}</div>' \
        if (note or note_html) else ""
    body = (
        f"<h1>{esc(title)}</h1><p class=\"sub\">{esc(subtitle)}</p>"
        + _nav() + note_html
        + f'<div class="card"><pre>{esc(markdown)}</pre></div>'
        + f'<p><a class="btn" href="{esc(back)}">Back</a></p>'
    )
    return layout(title, body, posture=posture, warn=warn)


def deliverables(*, engagement_name: str, interview_count: int, k_anonymity: int,
                 synthesis_md: str, employer_md: str, auto_validated: bool,
                 posture: str, warn: bool) -> str:
    """Both documents, side by side — the demo's pitch page.

    The contrast IS the product: the consultant's copy keeps attributed verbatim
    testimony because the participant was promised confidentiality inside the
    firewall; the employer's copy is aggregate-only at k={k}, with a ledger of
    what was withheld and why. Same engagement, two documents, and the difference
    is exactly what makes people answer honestly.
    """
    note = (
        "Same interviews, two documents. The consultant sees who said what, "
        "quoted verbatim. The employer sees group-level findings only — and "
        f"topics backed by fewer than {k_anonymity} people are withheld into a "
        "ledger, not summarised, because a sub-k topic can identify the people "
        "who raised it."
    )
    if auto_validated:
        note += (" Some or all verdicts were recorded by the auto-sim reviewer "
                 "(a demo), not a human consultant.")
    body = (
        f"<h1>Deliverables · {esc(engagement_name)}</h1>"
        f'<p class="sub">{interview_count} interviews · consultant view (left) vs '
        f"employer release (right, k-anonymity {k_anonymity})</p>"
        + _nav()
        + f'<div class="note">{esc(note)}</div>'
        + '<div class="split">'
        + '<div class="card left"><div class="label">Consultant — inside the '
          "firewall</div><h3>Attributed, verbatim, every claim cited</h3>"
          f'<div class="doc"><pre>{esc(synthesis_md)}</pre></div></div>'
        + '<div class="card right"><div class="label">Employer — what leaves '
          "the room</div><h3>Aggregate-only, k-anonymity "
          f'{k_anonymity}, withheld ledgered</h3>'
          f'<div class="doc"><pre>{esc(employer_md)}</pre></div></div>'
        + "</div>"
    )
    return layout("Deliverables", body, posture=posture, warn=warn)


def message(*, title: str, text: str, back: str = "/", posture: str = "",
            warn: bool = False) -> str:
    body = (f"<h1>{esc(title)}</h1><p class=\"sub\">{esc(text)}</p>"
            f'<p><a class="btn" href="{esc(back)}">Back</a></p>')
    return layout(title, body, posture=posture, warn=warn)
