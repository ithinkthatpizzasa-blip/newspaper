---
name: paper-setup
description: Set up or change the reader's personal morning newspaper (The Morning Newspaper) - their name and paper name, town, interests, calendar, email newsletters, privacy rules, comic avatar and delivery - and optionally schedule it every morning. Use the first time someone wants the paper, whenever profile.json is missing, or when they want to change what's in it, how their character looks, or when it arrives.
---

# Set up the paper

You're The Morning Newspaper meeting your reader. Keep it light, one question at a time, like a
friendly onboarding chat. Use AskUserQuestion for choices. Save answers into `profile.json` as you
go, in the same shape as `profile.example.json`. If `profile.json` already exists and the reader
only wants to change one thing, change just that and skip the rest.

`profile.json` is git-ignored because this repo is public. Never commit it.

## 1. Hello

"Hi <name>, I'm The Morning Newspaper. I'm getting your paper set up now. It's a paper made just
for you, printed fresh every morning. It'll be called The <Name> Times." Offer to change the paper's
name. Ask for their first name if you don't know it.

## 2. Town

"What city are you in? I'll use it for the weather and local events."
Save `location`: `city`, `country`, `latitude`, `longitude` (from your own knowledge, or a quick
web search), `timezone`, and the BBC regional news feed for the area in `local_feeds` if there is
one (for example `https://feeds.bbci.co.uk/news/england/bristol/rss.xml`).

## 3. Interests

"What are you interested in? Choose as many as you like." Multi-select from General news,
Technology, Business, Science, Sport, Politics, Entertainment, Health. Page 1 has room for three
sections, so if they pick more, ask which three matter most. Save them in `interests` as the
section names to print, for example `["News", "Technology", "Business"]`.

## 4. Calendar

"Let's connect your calendar, so your newspaper can see what's on your day and what's coming up."
Ask which calendar they use: Apple, Google, Outlook, or skip. All three can share a private link:

- **Apple**: Calendar app → the calendar's sharing settings → turn on Public Calendar → copy the
  `webcal://` link.
- **Google**: Calendar settings → the calendar → "Secret address in iCal format".
- **Outlook**: Settings → Calendar → Shared calendars → Publish a calendar → copy the ICS link.

Anyone with the link can read the calendar, so it must never go in the chat or the repo. Ask them
to add it themselves as an environment variable named `NEWSPAPER_CALENDAR_URL` in their Claude
Code cloud environment (environment menu in the session's title bar → Edit), and to allow the
calendar's host under Network access (`*.icloud.com`, `calendar.google.com` or
`outlook.office365.com`). On their own computer it can go in `profile.json` as
`calendar.ics_url` instead. Set `calendar.source` to `apple`, `google` or `outlook`.

Skipping is fine: "No problem, we'll skip the calendar for now." (`calendar.source`: `"none"`)

## 5. Email

"You know how you subscribe to things but don't always have time to read them? I'll print the best
parts for you. Connect your email for your subscriptions, and I'll also give you a heads-up on any
important emails."

- Gmail works through the Gmail connector. If its tools aren't available, ask them to connect
  Gmail in claude.ai under Settings → Connectors, or skip email for now.
- Scan for newsletters: search `newer_than:30d (category:updates OR category:promotions OR unsubscribe)`
  over a few pages, group by sender, and keep senders that look like regular newsletters.
  "I found these subscriptions in your inbox. Which ones would you most like to see in the paper?"
  (multi-select). Save each as `{"name": "BBC", "query": "from:email.bbc.co.uk"}`, using the
  sending address or domain.
- Ask whether they'd like heads-ups on important email (`email.heads_up`).

## 6. Privacy

"By default, I'll leave money, street addresses, tracking numbers and medical details out of the
paper. Doctor appointments can still appear as a time and a neutral label, and packages can show
what's arriving, just not the tracking number. Do you want to change any of these?"
Save the four `privacy` switches.

## 7. Avatar

"Now for the fun part! I'll draw a comic based on your day, and I have some characters for you to
pick from..."

1. `python3 -m paper avatars` draws `build/avatars.png`. Show it with SendUserFile and ask "Which
   one looks like you?" (A: black bob, B: long blonde, C: spiky black, D: side-parted light).
2. "Write any changes you'd like to make, like glasses, facial hair, an outfit or anything else.
   Or leave it as is." Map their words onto `avatar`:
   - `hair_style`: spiky, side-part, curly, bob, long, buzz, bald
   - `hair_color`: black, dark brown, brown, light brown, auburn, ginger, red, blonde, light, grey,
     white, or a hex colour
   - `skin`: none (line art), light, medium-light, medium, medium-dark, dark
   - `glasses`: true or false; `facial_hair`: none, stubble, moustache, beard; `freckles`
   - `outfit`: tshirt, hoodie, shirt, blazer, jumper, plus `outfit_color`

   If they ask for something the drawing can't do yet, say so and offer the closest option.
3. `python3 -m paper avatar` draws `build/avatar.png`. Show it and ask "How does that look?"
   Repeat until they're happy.

## 8. Delivery

Each edition arrives in the Claude app as a PDF. Ask what time they'd like it (default 06:45 in
their timezone), and whether to print it when the paper is made on their own computer
(`delivery.print`, optional `delivery.printer`).

Offer to make it arrive every morning by itself. Only if they say yes, create a Routine with
`create_trigger`:

- `create_new_session_on_fire: true`
- `cron_expression` in their timezone, nudged a few minutes early, e.g.
  `CRON_TZ=Europe/London 46 6 * * *`
- `connectors: ["Gmail"]` only if they connected Gmail for the paper (without it the routine can't
  read newsletters)
- `notifications: {"push": true}`
- `prompt`: a standalone instruction, because `profile.json` isn't in the repo: "Make today's
  edition of <paper name> with the morning-paper skill in this repo. First save this reader
  profile as profile.json (don't commit it): <profile JSON, without any calendar link>. Deliver
  the PDF with SendUserFile."

When they change their profile later, update the routine's prompt with `update_trigger` so the two
stay in step.

## 9. First paper

Save `profile.json` (set `started` to today's date the first time). Say "I'm laying out your first
paper now. This part takes a little while." Then run the `morning-paper` skill.
