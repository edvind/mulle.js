# Mårten Andersson (1978) – structured works

Extracted from *Mårten Andersson*, text by Teddy Gummerus (Askild & Kärnekull 1978, ISBN 91 7008 820 9).
The book is a monograph, not a complete catalogue: it shows a selection of works up to 1978. The text was
read from the page images and is kept in the book's original Swedish. PDF page numbers equal the book's page numbers.

- `catalogue.json` – `works` (59), `portfolios` (2), `section_texts` (the general text of the Grafik chapter), source info.
- `works.csv` – one row per work; list fields are joined with `; `, `dimensions_cm` as `a x b`.

## Contents
| category | count | book numbering |
|---|---|---|
| Oljemålning | 28 | Oljemålning 1–31 |
| Akvarell | 2 | no. 6 and 26 in the same series |
| Bemålat föremål | 1 | no. 4 (painted cabinet) |
| Offentlig utsmyckning | 5 | Utsmyckning 1–5 |
| Grafik | 23 | not numbered (portfolio sheets numbered 1–5 within the portfolio) |

## Fields (works)
Same idea as `grafik-boken-boman`, plus:
- `book_number` – the book's own number, e.g. `Oljemålning 12`, `Utsmyckning 3`, `6`.
- `category` – Oljemålning / Akvarell / Bemålat föremål / Offentlig utsmyckning / Grafik.
- `date_text`, `year`, `year_start` – date as printed; `year` is the completion year, `year_start` is set when a start year is given.
- `dimensions_text`, `dimensions_cm`, `dimensions_approx` – size as printed. `dimensions_cm` keeps the book's order, because
  the order is **not consistent**: compared with the 2015 Grafik-boken, some prints are listed width × height (e.g. Husguden 27 x 41) and others height × width.
  So the values are not mapped to height and width.
- `location`, `collaborators` – for the public commissions.
- `ownership` – the book says works are privately owned unless stated otherwise.
- `image_black_and_white`, `image_is_detail`, `is_cover_image` – what the reproduction in the book shows.
- `grafik_boken_id` – for prints, the matching `id` in `../grafik-boken-boman/catalogue.json`.

## Things to check (also in `review_flags`)
- **Dates that differ from the 2015 Grafik-boken:** Husguden (1952 vs 1953), Livet är en dröm (1957 vs 1968), Kyssen (1957 vs 1962), and the oil Kaffedrickarna (1967 here, 1964 there).
- **Sizes that differ:** Brudparet 1972 (63 x 86 vs 68 x 54 / 83 x 61), Vinter i Edstuga (35 x 27 vs 27 x 39), Selkroken (116 x 120 vs 118 x 115).
- **Två profiler** has no technique given here; the 2015 book says linocut.
- **Odjuret** is one entry, "Oljemålning 30 och 31", with two versions (1961 and 1977); split into two records.
- **Oljemålning 9, Metaren**, points to the introduction for its text; the text is taken from p. 15.
- Several entries (e.g. Sommarblommor, Bukett från Rom, Motiv från Tännäs) have no description in the book, so `description` is empty.
