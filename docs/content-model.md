# Content model

Everything an editor changes is one of the files below. Layout, menus and
styling live in `layouts/` and `assets/` and are never edited through the CMS.
The form editor's config (`.pages.yml`) mirrors this page field for field. A
change to a key here is a change there, and in every template that reads it.

**Never rename or remove a key** that has shipped: content already in the
repo uses it. Add a new key instead, and make templates tolerate it missing.

Dates are `YYYY-MM-DD`. Times are free text ("7:00 pm"). Every field not
marked *required* may be empty or absent, and templates must render without
it. That is how a half-filled form stays publishable.

## `data/club.yml`: club-wide facts

| Key | Type | Notes |
| --- | --- | --- |
| `name` | text, *required* | "Chippewa Valley Sports Car Club" |
| `tagline` | text | One line under the name on the home page |
| `email` | text | Contact address, shown on Contact; also how people join the mailing list |
| `nearby_events.label`, `.lat`, `.lng`, `.radius` | text, numbers | Where the Events page's MotorsportReg links search from (Eau Claire, 300 miles: MotorsportReg ignores smaller radii) |
| `hero_photo_credit` | text | Who took the home page's header photo; shown in its corner |
| `hero_photo_credit_url` | url | Link for that credit |
| `mailing_list_url` | url | A signup page for the mailing list. Empty: the Find us card emails `email` instead |
| `tax_status` | text | e.g. `501(c)(7)`; the Sponsors page says it and that the club is not a 501(c)(3) |
| `discord_invite` | url | The permanent invite; the site's main call to action |
| `media_form_url` | url | Where members submit videos and photos (`/submit/`) |
| `next_meeting.date` | date | Past or empty: the site says "Next meeting: date TBA" |
| `next_meeting.time` | text | |
| `next_meeting.venue` | text | "Hangar 54" |
| `next_meeting.address` | text | |
| `next_meeting.map_url` | url | |
| `next_meeting.notes` | text | One line, such as "Bring your waiver" |

## `data/socials.yml`: links to the club elsewhere

A list. An entry with an empty `url` is hidden, so all six can sit here
before the accounts exist. A platform may appear twice (the club's Facebook
page and its Facebook group); `label` tells them apart.

| Key | Type | Notes |
| --- | --- | --- |
| `name` | one of `facebook`, `discord`, `youtube`, `instagram`, `tiktok`, `reddit`, *required* | Picks the icon |
| `url` | url | |
| `label` | text | Accessible name; defaults to the name, capitalized |
| `blurb` | text | One line for the home page's "Find us" section; entries without one only show in the footer |

## `data/sponsors.yml`: who supports the club

A list, shown in order.

| Key | Type | Notes |
| --- | --- | --- |
| `name` | text, *required* | |
| `url` | url | The site adds `utm_source=cvscc.org&utm_medium=referral&utm_campaign=sponsors` so sponsors can see the referrals |
| `logo` | image path under `static/images/sponsors/` | Missing: the name is shown instead |
| `lane` | `club` or `event` | Defaults to `club`. Club sponsors back the whole season; event sponsors back one event |
| `tier` | club lane: `title`, `gold`, `supporter`; event lane: `presenting`, `event`, `in-kind` | Defaults to `supporter` (club) or `event` (event). Higher tiers show first and larger |
| `event` | file name of a `content/events/` page, without `.md` | Event lane: the sponsor also shows on that event's page |
| `event_label` | text | Event lane: the heading it's grouped under on the Sponsors page, e.g. `2027 CVTC Autocross` |
| `offer` | text | "10% off parts for members" |
| `code` | text | A discount or referral code to quote |
| `blurb` | text | One or two sentences |

## `data/clubs.yml`: other clubs near us

A list, shown in order on /community/nearby-clubs/.

| Key | Type | Notes |
| --- | --- | --- |
| `name` | text, *required* | |
| `url` | url | Their site (or a MotorsportReg search for their events) |
| `area` | text | Where they're based |
| `runs` | text | What they run, e.g. Autocross |
| `where` | text | One line: their venues or series |
| `note` | text | Optional extra line |

## `data/venues.yml`: places the club runs events

A map from a key (used as an event's `venue`) to `name`, `url`, `where`
(one line: how to find it), `map_url`, `thanks` (one line shown on event
pages) and `page` (the site's own page about it, e.g. `rock-falls-raceway/`).

## `content/events/<slug>.md`: things on the calendar

Front matter:

| Key | Type | Notes |
| --- | --- | --- |
| `title` | text, *required* | |
| `date` | date, *required* | The day of the event. `buildFuture` is on, so future dates publish |
| `end_date` | date | Multi-day events |
| `event_type` | one of `autocross`, `track`, `drag`, `rally`, `social`, `meeting`, `sim`, *required* | Not `type`: Hugo reserves that front-matter key to pick the page template |
| `location` | text | Optional when `venue` is set (the venue's name is shown) |
| `venue` | key in `data/venues.yml` | e.g. `rock-falls-raceway`: the event page shows the venue with a map link and a thank-you |
| `host` | text | Who runs it, when the club is attending rather than running it (a club outing to a Test & Tune): shown as "Hosted by ..." |
| `register_url` | url | MotorsportReg, Eventbrite, Facebook event |
| `summary` | text | One line for lists |
| `results` | slug of a `content/results/` page | Set after the event; the event links to its results |
| `announce` | boolean | Defaults to `false`. Tick to post this once, with a link, after the site updates. Only ticked items are ever announced |
| `announce_text` | text | Optional. What the post says. Empty: the title and summary |

The body is optional free text. "Upcoming" means `date` (or `end_date`) is
today or later **at build time**; the deploy workflow rebuilds every day, so
past events drop off on their own.

## `content/results/<slug>.md`: what happened

| Key | Type | Notes |
| --- | --- | --- |
| `title` | text, *required* | "2027 CVTC Autocross" |
| `date` | date, *required* | |
| `event` | slug of a `content/events/` page | |
| `results_file` | file path under `static/results/` | PDF or HTML from the timing software. An AXWare raw-time PDF is imported automatically (`scripts/import-results.py`) |
| `results_url` | url | Results hosted elsewhere (MotorsportReg, a series site) |
| `highlights` | list of `{class, place, driver, car, time}` | Optional podium table; any subset of the keys |
| `summary` | text | One line for lists |
| `announce` | boolean | Defaults to `false`. Tick to post this once, with a link, after the site updates. Only ticked items are ever announced |
| `announce_text` | text | Optional. What the post says. Empty: the title and summary |

The body is an optional write-up; the tables come from `assets/results/<slug>.md`, generated from `results-src/`. The Results list groups pages by year.

## `content/news/<slug>.md`: posts

| Key | Type | Notes |
| --- | --- | --- |
| `title` | text, *required* | |
| `date` | date, *required* | |
| `summary` | text | |
| `image` | image path under `static/images/news/` | |
| `announce` | boolean | Defaults to `false`. Tick to post this once, with a link, after the site updates. Only ticked items are ever announced |
| `announce_text` | text | Optional. What the post says. Empty: the title and summary |

## Plain pages

`content/about.md`, `content/join.md`, `content/contact.md`,
`content/submit.md`, `content/privacy.md`, `content/terms.md` and
`content/sponsor-the-club.md` are a title and a body. Any page may also set
`review:` (text): the page then shows a "Draft: for club review" banner with
that text, for information the club hasn't decided yet. Clear it once decided. Privacy and Terms exist because TikTok's and Meta's developer
apps, which publish the club's videos, require those URLs.

## `/announce.json` feed

The site generates a JSON Feed 1.1 feed at `/announce.json` that contains all
news, events and results pages. The feed includes:
- `version`: "https://jsonfeed.org/version/1.1"
- `title`: site title
- `home_page_url`: site permalink
- `feed_url`: absolute URL to the feed itself
- `items`: array of feed items, each with:
  - `id`: `cvscc:` plus the page's path in the site (e.g. `cvscc:/news/2026-10-24-new-website`), stable when the domain changes; fanout's ledger keys on it
  - `url`: page permalink (absolute)
  - `title`: page title
  - `summary`: page summary when set
  - `date_published`: ISO 8601 date
  - `image`: absolute URL to page image when set
  - `_fanout`: object with:
    - `announce`: true only when `.Params.announce` is true
    - `text`: `.Params.announce_text` when set
    - `kind`: page section ("news", "events", or "results")

All pages in the news, events and results sections appear in the feed; the
`_fanout.announce` flag is true only for pages where `.Params.announce` is set.
