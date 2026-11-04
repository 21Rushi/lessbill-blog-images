# lessbill-blog-images

Cover images for two Blogger blogs:
- LessBill: lessbill.blogspot.com -> `covers/YYYY-MM-DD-slug.jpg`
- Blog For Today: 21stbirthd.blogspot.com -> `covers/bft/YYYY-MM-DD-slug.jpg`

Make a cover:
- LessBill (new look every day — palette/layout rotate by the date in the file name; pick an --icon that fits the topic):
  `python3 tools/make_lessbill_cover.py "Headline" "Subtitle" covers/YYYY-MM-DD-slug.jpg --icon gpu|server|cloud|coins|pods|network|storage|chart|bell|tag|robot|gauge [--stat "92%"]`
- Old single-style generator (still used for Blog For Today):
- `python3 tools/make_cover.py "Title" "Subtitle" covers/YYYY-MM-DD-slug.jpg`
- `python3 tools/make_cover.py "Title" "Subtitle" covers/bft/YYYY-MM-DD-slug.jpg bft "TRENDING · TECH"`

Use in posts: `https://raw.githubusercontent.com/21Rushi/lessbill-blog-images/main/<path>`
