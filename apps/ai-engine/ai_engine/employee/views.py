"""HTML for the employee interview surface.

A different visual language from the consultant workspace on purpose: one column, one
task, larger type, no navigation. The person using this is not a power user — they are
someone deciding whether it is safe to be honest about their workplace.

The confidentiality statement is not decoration. In the candor experiment it *is* the
treatment being measured, so it is shown before the first question and repeated where
the decision to disclose actually happens. Every promise it makes is one the code
enforces: pseudonymisation at invitation time, aggregate-only employer release,
k-anonymity, and discard-on-withdrawal.
"""
from __future__ import annotations

from html import escape


def esc(value) -> str:
    return escape(str(value), quote=True)


CSS = """
:root { color-scheme: light dark; --fg:#16161a; --muted:#5c5c66; --bg:#fbfbfc;
        --card:#fff; --line:#e2e2e7; --accent:#1f6f54; --soft:#eef5f2; }
@media (prefers-color-scheme: dark) {
  :root { --fg:#ecedef; --muted:#a0a0aa; --bg:#131316; --card:#1c1c21;
          --line:#2c2c34; --accent:#6fc3a0; --soft:#1b2622; }
}
* { box-sizing:border-box; }
body { margin:0; font:17px/1.65 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
       color:var(--fg); background:var(--bg); }
main { max-width:640px; margin:0 auto; padding:40px 22px 80px; }
h1 { font-size:26px; line-height:1.25; margin:0 0 10px; }
h2 { font-size:18px; margin:30px 0 8px; }
p { margin:0 0 14px; }
.lede { color:var(--muted); font-size:16px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:14px;
        padding:20px 22px; margin:0 0 18px; }
.promise { background:var(--soft); border:1px solid var(--line); border-radius:14px;
           padding:18px 22px; margin:0 0 20px; }
.promise ul { margin:10px 0 0; padding-left:20px; }
.promise li { margin:0 0 8px; }
.question { font-size:20px; font-weight:600; line-height:1.4; margin:0 0 14px; }
textarea { font:inherit; width:100%; padding:12px 14px; border-radius:10px;
           border:1px solid var(--line); background:var(--bg); color:var(--fg);
           min-height:120px; resize:vertical; }
button { font:inherit; font-weight:600; padding:12px 20px; border-radius:10px;
         border:1px solid var(--accent); background:var(--accent); color:#fff;
         cursor:pointer; }
button.quiet { background:transparent; color:var(--muted); border-color:var(--line);
               font-weight:400; padding:9px 14px; }
.row { display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin-top:14px; }
.spacer { flex:1; }
.mine { border-left:3px solid var(--line); padding:2px 0 2px 14px; margin:0 0 16px;
        color:var(--muted); font-size:15px; }
.mine .q { color:var(--fg); font-weight:600; }
.progress { color:var(--muted); font-size:14px; margin:0 0 22px; }
.small { font-size:14px; color:var(--muted); }
"""


def layout(title: str, body: str) -> str:
    return (
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        '<meta name=viewport content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title><style>{CSS}</style></head>"
        f"<body><main>{body}</main></body></html>"
    )


THE_PROMISE = """
<div class="promise">
  <strong>What happens to what you say</strong>
  <ul>
    <li><strong>Your name is not attached to your answers.</strong> This interview was
        opened under a code, and your name was never entered into this tool.</li>
    <li><strong>Your employer does not see your answers.</strong> They receive a summary
        across everyone interviewed — group-level findings only, with no names and no
        quotes of what anyone said.</li>
    <li><strong>A topic is only reported if several people raise it.</strong> If you are
        the only person who mentions something, it is withheld rather than reported.</li>
    <li><strong>You can stop at any time</strong>, and if you stop, what you have said is
        discarded and never stored.</li>
  </ul>
</div>
"""


def welcome(*, token: str, objective_note: str) -> str:
    body = (
        "<h1>A short, confidential conversation about how work actually gets done</h1>"
        f'<p class="lede">{esc(objective_note)}</p>'
        + THE_PROMISE
        + '<div class="card">'
        "<p>It takes about 15 minutes. There are no right answers, and nothing you say "
        "is evaluated as your performance. The most useful answers are specific ones — "
        "what actually happened, the last time it happened.</p>"
        f'<form method="post" action="/i/{esc(token)}/begin">'
        '<div class="row"><button type="submit">Begin</button>'
        '<div class="spacer"></div>'
        '<span class="small">Beginning means you agree to the above.</span>'
        "</div></form></div>"
    )
    return layout("Confidential interview", body)


def question_page(*, token: str, question: str, answered: list[dict],
                  turn: int, max_turns: int) -> str:
    history = ""
    if answered:
        history = "<h2>What you have said so far</h2>"
        for pair in answered:
            history += (f'<div class="mine"><div class="q">{esc(pair["question"])}</div>'
                        f'<div>{esc(pair["answer"])}</div></div>')

    body = (
        f'<p class="progress">Question {turn} of about {max_turns} · your answers are '
        "confidential to the interviewer</p>"
        f'<div class="card"><p class="question">{esc(question)}</p>'
        f'<form method="post" action="/i/{esc(token)}/answer" '
        f'onsubmit="var b=this.querySelector(\'button.primary\');if(b)b.disabled=true">'
        '<textarea name="answer" required autofocus '
        'placeholder="In your own words. Specifics help more than summaries."></textarea>'
        '<div class="row"><button type="submit">Continue</button>'
        '<div class="spacer"></div></div></form></div>'
        '<div class="card"><p class="small">Prefer not to answer a particular question? '
        "Say so and we will move on. If you would rather stop altogether, everything you "
        "have said will be discarded.</p>"
        f'<form method="post" action="/i/{esc(token)}/withdraw">'
        '<button class="quiet" type="submit">Stop and discard my answers</button>'
        "</form></div>"
        + history
    )
    return layout("Confidential interview", body)


def review_before_finish(*, token: str, answered: list[dict]) -> str:
    history = ""
    for pair in answered:
        history += (f'<div class="mine"><div class="q">{esc(pair["question"])}</div>'
                    f'<div>{esc(pair["answer"])}</div></div>')
    body = (
        "<h1>That is everything — thank you</h1>"
        '<p class="lede">Before this is submitted, here is what you said. Nothing has '
        "been shared yet.</p>"
        + history
        + '<div class="card">'
        f'<form method="post" action="/i/{esc(token)}/finish">'
        '<div class="row"><button type="submit">Submit my answers</button>'
        '<div class="spacer"></div></div></form>'
        f'<form method="post" action="/i/{esc(token)}/withdraw" style="margin-top:12px">'
        '<button class="quiet" type="submit">Discard everything instead</button>'
        "</form></div>"
    )
    return layout("Confidential interview", body)


def finished() -> str:
    body = (
        "<h1>Submitted — thank you</h1>"
        '<p class="lede">Your answers have gone to the interviewing consultant only.</p>'
        + THE_PROMISE
        + '<p class="small">You can close this page. The link will not open again.</p>'
    )
    return layout("Thank you", body)


def withdrawn() -> str:
    body = (
        "<h1>Discarded</h1>"
        '<p class="lede">Nothing you said was stored, and nothing was shared with '
        "anyone. There is no record of your answers.</p>"
        '<p class="small">You can close this page. Thank you for your time.</p>'
    )
    return layout("Discarded", body)


def already_submitted() -> str:
    """A withdrawal request on a completed interview, told honestly.

    The testimony was consented to and stored; claiming otherwise would be the
    worst thing this page could say. Erasure now goes through the consultant,
    not through this link.
    """
    body = (
        "<h1>That interview is already complete</h1>"
        '<p class="lede">You submitted this interview, so it has been stored and '
        "handed over as you agreed. It cannot be withdrawn from this page.</p>"
        '<p class="small">If you want your answers removed, contact the '
        "interviewing consultant and ask for erasure — they can do that on your "
        "behalf.</p>"
    )
    return layout("Already submitted", body)


def answer_too_long(token: str, max_chars: int) -> str:
    """A refused oversized answer — recoverable, and nothing was recorded."""
    body = (
        "<h1>That answer is too long</h1>"
        f'<p class="lede">Answers are capped at {max_chars:,} characters. Your '
        "answer was not recorded — please split it into shorter parts and "
        "answer again.</p>"
        '<div class="card">'
        f'<form method="get" action="/i/{esc(token)}">'
        '<button type="submit">Back to the question</button></form>'
        "</div>"
    )
    return layout("Answer too long", body)


def temporarily_unavailable(token: str) -> str:
    """A model failure, told honestly: recoverable, and nothing was lost.

    Distinct from :func:`unavailable`, which is a dead link. Conflating the two would
    tell someone their interview was over when it is merely paused — and they would
    not come back.
    """
    body = (
        "<h1>Just a moment — we couldn't reach the interviewer</h1>"
        '<p class="lede">Nothing you have said has been lost. This is a temporary '
        "problem on our side, not anything you did.</p>"
        '<div class="card">'
        f'<form method="get" action="/i/{esc(token)}">'
        '<button type="submit">Try again</button></form>'
        '<p class="small" style="margin-top:14px">If it keeps happening, close the page '
        "and come back to this link later — your answers so far are still here.</p>"
        "</div>"
    )
    return layout("One moment", body)


def unavailable() -> str:
    """One page for every not-usable case, so nothing is revealed by the difference."""
    body = (
        "<h1>This link is not available</h1>"
        '<p class="lede">It may have already been used, or it may have expired. If you '
        "were expecting to take part, ask whoever sent it for a new link.</p>"
    )
    return layout("Not available", body)
