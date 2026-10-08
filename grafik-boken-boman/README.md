# Grafik | Mårten A – structured catalogue

Extracted from *Grafik | Mårten A* (Bengt Boman, Helsinge Konst & Förlag 2015, ISBN 978-91-982645-0-0),
section "Den kompletta katalogen", book pp. 29–85. The text was read from the page images, not the OCR
layer (which drops å/ä/ö and scrambles the columns), and is kept in the book's original Swedish.

- `catalogue.json` – full data: `prints` (71), `portfolios` (7 portfolios + 1 series), source info.
- `prints.csv` – one row per print; list fields are joined with `; `.

## Print fields
| field | meaning |
|---|---|
| `id` | slug of title + year (unique; e.g. `brudparet-1972`, `brudparet-1990`, `brudparet-2010`) |
| `seq` | order in the book (assigned here, the book has no catalogue numbers) |
| `title`, `alt_titles` | heading title; names given in parentheses or the text |
| `technique` | Litografi / Screentryck / Linoleumtryck |
| `year` | year made |
| `dimensions_text`, `height_cm`, `width_cm` | size as printed in the book, plus parsed height × width |
| `edition_size`, `edition_text`, `edition_source` | edition size; `portfolio` = taken from the portfolio's edition |
| `portfolio` / `series` | portfolio the sheet belongs to (Mårtens arv och testamente is a series, not a portfolio) |
| `hand_colored` | the whole edition is hand-coloured |
| `is_auxiliary_sheet` | the Bruddansen mounting instruction (a lithograph, but not a picture) |
| `description`, `captions`, `notes` | book text for the entry, picture captions, and notes added here |
| `book_pages`, `image_book_pages`, `pdf_pages` | where the entry and its illustrations are |
| `review_flags` | things worth checking by hand |

## Things to check
- The book says 71 sheets in total. That number is reached only by counting the Bruddansen mounting instruction (`is_auxiliary_sheet`). Drop it if you only want pictures.
- The book describes *Två profiler* and *Dukat bord* in one shared entry; they are split into two records here.
- Sheets inside portfolios have only a size in the book; technique, year and edition come from the portfolio.
- Book p. 56 (the full-page Selkroken illustration) is missing from the scan. Book pp. 64–83 were scanned twice (PDF pages 60–79 and 80–99); `pdf_pages` points to the first scan.
- Editions without a number: Fest i stugan, Två profiler, Dukat bord (unnumbered).
