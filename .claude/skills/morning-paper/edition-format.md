# edition.json

One file per day at `build/<YYYY-MM-DD>/edition.json`. Every section except `date` is optional; leave
out anything you have nothing good for and the layout closes up around it. See
`paper/samples/sample-edition.json` for a complete example.

```jsonc
{
  "date": "2026-10-04",                       // required, the reader's local date

  "weather": {
    "kind": "showers",                        // icon + default comic sky, see "Weather kinds"
    "short": "Sunny spells, shower by teatime",      // ≤ 7 words, goes in the masthead ear
    "summary": "Bright start, then a passing shower after 4pm.",   // ≤ 16 words
    "high": 15, "low": 8,                     // °C as numbers
    "rain_chance": 40,                        // %, or null if unknown
    "wind": "Breezy, gusts to 20 mph",        // optional
    "sunrise": "07:16", "sunset": "18:39",    // optional, 24h
    "advice": "Sunglasses now, brolly later.",       // ≤ 14 words, optional
    "outlook": [                              // next 3 days
      { "day": "Mon", "kind": "rain", "high": 14, "low": 9 }
    ],
    "source": "Met Office"
  },

  "lead": {
    "section": "UK",                          // small red kicker above the headline
    "headline": "≤ 12 words",
    "standfirst": "One or two sentences, ≤ 35 words, that sum the story up.",
    "body": ["paragraph", "paragraph"],       // 230–300 words in 4–6 paragraphs
    "source": "BBC News"
  },

  "headlines": {                              // front-page headlines box, when profile.headlines is set
    "title": "BBC headlines",                 // "Today's headlines" if the feed couldn't be read
    "source": "BBC News",
    "as_of": "6:40am",                        // when the feed was read
    "items": [                                // 6–8, in the feed's order, wording unchanged
      { "headline": "The feed's own headline", "summary": "optional, ≤ 12 words" }
    ]
  },

  "sections": [                               // up to 3 on page 1, or 2 beside a headlines box
    { "name": "News", "stories": [
        { "headline": "≤ 8 words", "body": "15–22 words", "source": "Reuters" }
    ] }
  ],

  "your_day": {
    "events":   [{ "time": "09:00", "title": "Geography", "where": "Room 4" }],   // ≤ 6; time null = all day
    "upcoming": [{ "when": "Tue", "title": "Essay due" }],                        // ≤ 3
    "note": "Shown under the events, or instead of them if there are none (≤ 30 words)."
  },

  "inbox": {
    "newsletters": [                          // 260–340 words in total across all of them
      { "from": "BBC", "headline": "≤ 10 words",
        "summary": "Optional short paragraph.",
        "points": ["one line each, ≤ 25 words"] }
    ],
    "heads_up": [                             // ≤ 4, ≤ 22 words each; only things the reader needs to know
      { "from": "School office", "text": "Reply slip for the museum trip is due Thursday." }
    ]
  },

  "more": {                                  // ONLY when there are no newsletters (e.g. no Gmail):
    "title": "More to read",                  // fills the inbox column with 4–5 extra stories,
    "items": [                                // 260–340 words in total (sport, science, culture...)
      { "label": "Science", "headline": "≤ 10 words", "body": "≤ 70 words", "source": "BBC News" }
    ]
  },

  "local": { "items": [                       // 3–4 items, 150–210 words in total
    { "label": "Event", "when": "Sat", "headline": "≤ 9 words", "body": "≤ 45 words" }
  ] },

  "comic": {
    "title": "Sam's Sunday",
    "panels": [                               // exactly 4
      { "scene": "bedroom", "mood": "sleepy", "pose": "center", "prop": "phone",
        "caption": "7:02am", "speech": "Five more minutes...", "thought": false, "sfx": "BEEP!",
        "weather": "rain" }
    ]
  },

  "extras": {
    "quote":       { "text": "≤ 22 words", "by": "Who said it" },
    "on_this_day": { "year": 1957, "text": "≤ 26 words" },
    "word":        { "word": "Petrichor", "meaning": "≤ 16 words" },
    "puzzle":      { "question": "≤ 24 words", "answer": "≤ 8 words (printed upside down)" }
  },

  "sources": ["BBC News", "Met Office", "Bristol Post"]   // credits in the footer
}
```

## Comic vocabulary

Only `scene` and `mood` affect the drawing; unknown values fall back to safe defaults.

- **scene**: `bedroom`, `night` (dark bedroom), `kitchen`, `desk`, `classroom`, `street`, `town`,
  `bus`, `train`, `park`, `sofa`, `pitch`, `cafe`, `library`, `burst` (sunburst for big moments),
  `plain`. Aliases work too: `school`→classroom, `homework`→desk, `breakfast`→kitchen,
  `commute`→bus, `football`→pitch, `shops`→town, `bedtime`→night.
- **mood**: `happy`, `excited`, `laughing`, `proud`, `sleepy`, `surprised`, `thinking`, `worried`,
  `determined`, `grumpy`, `smug`, `neutral`.
- **prop** (optional): `mug`, `phone`, `book`, `newspaper`, `football`, `umbrella`, `laptop`,
  `headphones`, `backpack`, `scarf`, `beanie`.
- **pose**: `center` (default), `left`, `right`. The speech bubble goes on the opposite side.
- **weather** (optional): overrides the day's sky for that panel, see below.
- **speech**: ≤ 9 words. **caption**: ≤ 4 words (times work well). **sfx**: ≤ 10 characters.
  **thought**: `true` draws a thought bubble instead of speech.

## Weather kinds

`clear`, `partly-cloudy`, `cloudy`, `fog`, `drizzle`, `rain`, `showers`, `heavy-rain`, `thunder`,
`snow`, `windy`, `night`. Everyday words like "sunny", "overcast" or "sunny spells" are mapped
automatically.
