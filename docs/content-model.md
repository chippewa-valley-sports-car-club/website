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

## `content/events/<slug>.md`: things on the calendar

Front matter:

| Key | Type | Notes |
| --- | --- | --- |
| `title` | text, *required* | |
| `date` | date, *required* | The day of the event. `buildFuture` is on, so future dates publish |
| `end_date` | date | Multi-day events |
| `event_type` | one of `autocross`, `track`, `rally`, `social`, `meeting`, `sim`, *required* | Not `type`: Hugo reserves that front-matter key to pick the page template |
| `location` | text | |
| `register_url` | url | MotorsportReg, Eventbrite, Facebook event |
| `summary` | text | One line for lists |
| `results` | slug of a `content/results/` page | Set after the event; the event links to its results |

The body is optional free text. "Upcoming" means `date` (or `end_date`) is
today or later **at build time**; the deploy workflow rebuilds every day, so
past events drop off on their own.

## `content/results/<slug>.md`: what happened

| Key | Type | Notes |
| --- | --- | --- |
| `title` | text, *required* | "2027 CVTC Autocross" |
| `date` | date, *required* | |
| `event` | slug of a `content/events/` page | |
| `results_file` | file path under `static/results/` | PDF or HTML from the timing software |
| `results_url` | url | Results hosted elsewhere (MotorsportReg, a series site) |
| `highlights` | list of `{class, place, driver, car, time}` | Optional podium table; any subset of the keys |
| `summary` | text | One line for lists |

The body is an optional write-up. The Results list groups pages by year.

## `content/news/<slug>.md`: posts

| Key | Type | Notes |
| --- | --- | --- |
| `title` | text, *required* | |
| `date` | date, *required* | |
| `summary` | text | |
| `image` | image path under `static/images/news/` | |

## Plain pages

`content/about.md`, `content/join.md`, `content/contact.md`,
`content/submit.md`, `content/privacy.md` and `content/terms.md` are a title
and a body. Privacy and Terms exist because TikTok's and Meta's developer
apps, which publish the club's videos, require those URLs.
