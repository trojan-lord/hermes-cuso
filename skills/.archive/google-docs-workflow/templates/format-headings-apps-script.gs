/**
 * Google Doc heading/content font-size normalizer — no-OAuth path
 * -----------------------------------------------------------------
 * Rule applied: headings → HEADER_SIZE (14pt), body/table content → BODY_SIZE (11pt).
 * Edit the two constants below to taste, then follow the run instructions
 * in the parent skill (Extensions → Apps Script → paste → Run → authorize).
 *
 * HOW TO RUN:
 *   1. Open the doc in a browser
 *   2. Extensions → Apps Script
 *   3. Delete the default code, paste this whole file
 *   4. Click "Run" (top toolbar), pick the main function
 *   5. First run asks for authorization: choose the account, click
 *      "Advanced" → "Go to <project name> (unsafe)" → "Allow"
 *      (normal for personal scripts; the script only touches font sizes)
 *   6. Switch back to the doc tab — done.
 *
 * Safe: only changes FONT SIZE. Preserves bold, colors, alignment, table structure.
 * Idempotent: safe to run twice.
 */

var HEADER_SIZE = 14; // pt for headings
var BODY_SIZE   = 11; // pt for everything else
var KEEP_BIG_TITLES = false; // true = leave paragraphs already LARGER than HEADER_SIZE alone

function formatDoc() {
  var body = DocumentApp.getActiveDocument().getBody();
  walk(body, false);
}

function walk(container, inTable) {
  var n = container.getNumChildren();
  for (var i = 0; i < n; i++) {
    var el = container.getChild(i);
    var type = el.getType();

    if (type === DocumentApp.ElementType.PARAGRAPH) {
      var text = el.getText();
      if (text.length === 0) continue; // spacer paragraphs — leave alone
      var isHeader = !inTable && el.getHeading() !== DocumentApp.ParagraphHeading.NORMAL;
      setSize(el, isHeader ? HEADER_SIZE : BODY_SIZE);

    } else if (type === DocumentApp.ElementType.LIST_ITEM) {
      setSize(el, BODY_SIZE);

    } else if (type === DocumentApp.ElementType.TABLE) {
      var rows = el.getNumRows();
      for (var r = 0; r < rows; r++) {
        var cells = el.getRow(r).getNumCells();
        for (var c = 0; c < cells; c++) {
          walk(el.getRow(r).getCell(c), true); // table content = subject matter = body size
        }
      }
    }
    // other element types (images, equations, etc.) — untouched
  }
}

function setSize(p, size) {
  var text = p.getText();
  if (KEEP_BIG_TITLES) {
    // detect the current rendered size from the first run
    var first = p.editAsText().getFontSize(0);
    if (first && first > HEADER_SIZE) return; // leave oversized banners alone
  }
  // paragraph-level attribute as a base...
  p.setAttributes({ FONT_SIZE: size });
  // ...and run-level override so spans that carry their own sizes get normalized too
  p.editAsText().setFontSize(0, text.length - 1, size);
}
